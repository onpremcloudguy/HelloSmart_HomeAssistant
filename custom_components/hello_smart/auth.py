"""Region-aware authentication and HMAC-SHA1 request signing for Smart API."""

from __future__ import annotations

import base64
import hashlib
import hmac
import json
import logging
import secrets
import time
import uuid
from urllib.parse import urlparse, parse_qs, urlencode, quote

import aiohttp

from .const import (
    ACCEPT_HEADER,
    API_SESSION_PATH,
    EMPTY_BODY_MD5,
    EU_API_BASE_URL,
    EU_APP_ID,
    EU_AUTH_BASE_URL,
    EU_CONTEXT_URL,
    EU_DEVICE_ID_LENGTH,
    EU_IDENTITY_TYPE,
    EU_OPERATOR_CODE,
    EU_SIGNING_SECRET,
    GIGYA_API_KEY,
    INTL_APP_ID,
    INTL_AUTH_BASE_URL,
    INTL_DEVICE_ID_LENGTH,
    INTL_IDENTITY_TYPE,
    INTL_OPERATOR_CODE,
    INTL_SIGNING_SECRET,
    INTL_VEHICLE_APP_ID,
    INTL_X_CA_KEY,
    INTL_API_BASE_URL,
)
from .models import Account, AuthState, Region

_LOGGER = logging.getLogger(__name__)


def _generate_device_id(length: int) -> str:
    """Generate a random hex device identifier."""
    return secrets.token_hex(length // 2)


def _md5_base64(data: str | bytes) -> str:
    """Compute base64-encoded MD5 hash of data."""
    if isinstance(data, str):
        data = data.encode("utf-8")
    return base64.b64encode(hashlib.md5(data).digest()).decode()


def _create_sign(
    nonce: str,
    params: dict,
    timestamp: str,
    method: str,
    url: str,
    body: str | None = None,
    use_intl: bool = False,
    url_encode_params: bool = False,
) -> str:
    """Create HMAC-SHA1 signature matching reference pySmartHashtag utils."""
    body_md5 = _md5_base64(body) if body else EMPTY_BODY_MD5

    if url_encode_params and params:
        encoded_params = {k: quote(str(v), safe="") for k, v in params.items()}
        url_params = "&".join(f"{k}={v}" for k, v in encoded_params.items())
    elif params:
        url_params = "&".join(f"{k}={v}" for k, v in params.items())
    else:
        url_params = ""

    payload = (
        f"{ACCEPT_HEADER}\n"
        f"x-api-signature-nonce:{nonce}\n"
        f"x-api-signature-version:1.0\n"
        f"\n"
        f"{url_params}\n"
        f"{body_md5}\n"
        f"{timestamp}\n"
        f"{method}\n"
        f"{url}"
    )

    secret = INTL_SIGNING_SECRET if use_intl else EU_SIGNING_SECRET
    signature = base64.b64encode(
        hmac.new(secret, payload.encode("utf-8"), hashlib.sha1).digest()
    ).decode()
    return signature


def build_signed_headers(
    method: str,
    url: str,
    body: str | None,
    account: Account,
) -> dict[str, str]:
    """Build all required signed headers for a vehicle API request.

    Routes to region-specific header generation matching
    the pySmartHashtag reference implementation.
    """
    if account.region == Region.INTL:
        return _build_intl_headers(method, url, body, account)
    return _build_eu_headers(method, url, body, account)


def _build_eu_headers(
    method: str,
    url: str,
    body: str | None,
    account: Account,
) -> dict[str, str]:
    """Generate EU vehicle API headers (matching generate_default_header)."""
    parsed = urlparse(url)
    path = parsed.path
    params_str = parsed.query

    # EU uses dict-style params for signing
    params_dict: dict[str, str] = {}
    if params_str:
        for pair in params_str.split("&"):
            if "=" in pair:
                k, v = pair.split("=", 1)
                params_dict[k] = v

    timestamp = str(int(time.time() * 1000))
    nonce = secrets.token_hex(8)

    sign = _create_sign(nonce, params_dict, timestamp, method, path, body)

    headers = {
        "x-app-id": EU_APP_ID,
        "accept": ACCEPT_HEADER,
        "x-agent-type": "iOS",
        "x-device-type": "mobile",
        "x-operator-code": EU_OPERATOR_CODE,
        "x-device-identifier": account.device_id,
        "x-env-type": "production",
        "x-version": "smartNew",
        "accept-language": "en_US",
        "x-api-signature-version": "1.0",
        "x-api-signature-nonce": nonce,
        "x-device-manufacture": "Apple",
        "x-device-brand": "Apple",
        "x-device-model": "iPhone",
        "x-agent-version": "17.1",
        "content-type": "application/json; charset=utf-8",
        "user-agent": "Hello smart/1.4.0 (iPhone; iOS 17.1; Scale/3.00)",
        "x-signature": sign,
        "x-timestamp": timestamp,
    }
    if account.api_access_token:
        headers["authorization"] = account.api_access_token

    return headers


def _build_intl_headers(
    method: str,
    url: str,
    body: str | None,
    account: Account,
) -> dict[str, str]:
    """Generate INTL vehicle API headers (matching generate_intl_header)."""
    parsed = urlparse(url)
    path = parsed.path
    params_str = parsed.query

    params_dict: dict[str, str] = {}
    if params_str:
        for pair in params_str.split("&"):
            if "=" in pair:
                k, v = pair.split("=", 1)
                params_dict[k] = v

    timestamp = str(int(time.time() * 1000))
    nonce = str(uuid.uuid4()).upper()

    # INTL requires URL-encoded params in signature for GET requests
    url_encode_params = method.upper() == "GET"
    sign = _create_sign(
        nonce, params_dict, timestamp, method, path, body,
        use_intl=True, url_encode_params=url_encode_params,
    )

    headers = {
        "x-app-id": INTL_VEHICLE_APP_ID,
        "accept": ACCEPT_HEADER,
        "x-agent-type": "iOS",
        "x-device-type": "mobile",
        "x-operator-code": INTL_OPERATOR_CODE,
        "x-device-identifier": account.device_id,
        "x-env-type": "production",
        "accept-language": "en_US",
        "x-api-signature-version": "1.0",
        "x-api-signature-nonce": nonce,
        "x-device-manufacture": "Apple",
        "x-device-brand": "Apple",
        "x-device-model": "iPhone",
        "x-agent-version": "18.6.1",
        "content-type": "application/json",
        "user-agent": "GlobalSmart/1.0.7 (iPhone; iOS 18.6.1; Scale/3.00)",
        "x-signature": sign,
        "x-timestamp": timestamp,
        "platform": "NON-CMA",
        "x-vehicle-series": "HC1H2D3B6213-01_IL",
    }
    if account.api_access_token:
        headers["authorization"] = account.api_access_token
    if account.api_client_id:
        headers["x-client-id"] = account.api_client_id

    return headers


def _build_intl_session_headers(
    body: str,
    device_id: str,
) -> dict[str, str]:
    """Generate INTL headers for the session/secure exchange (step 3).

    Matches _generate_vehicle_api_headers from reference — no auth token yet.
    """
    timestamp = str(int(time.time() * 1000))
    nonce = str(uuid.uuid4()).upper()

    sign = _create_sign(
        nonce=nonce,
        params={"identity_type": INTL_IDENTITY_TYPE},
        timestamp=timestamp,
        method="POST",
        url=API_SESSION_PATH,
        body=body,
        use_intl=True,
    )

    return {
        "x-app-id": INTL_VEHICLE_APP_ID,
        "x-operator-code": INTL_OPERATOR_CODE,
        "x-agent-type": "iOS",
        "x-agent-version": "18.6.1",
        "x-device-type": "mobile",
        "x-device-identifier": device_id,
        "x-device-manufacture": "Apple",
        "x-device-brand": "Apple",
        "x-device-model": "iPhone",
        "x-env-type": "production",
        "x-api-signature-version": "1.0",
        "x-api-signature-nonce": nonce,
        "x-timestamp": timestamp,
        "platform": "NON-CMA",
        "accept": ACCEPT_HEADER,
        "accept-language": "en_US",
        "content-type": "application/json",
        "user-agent": "GlobalSmart/1.0.7 (iPhone; iOS 18.6.1; Scale/3.00)",
        "x-signature": sign,
    }


async def async_login_intl(
    session: aiohttp.ClientSession,
    email: str,
    password: str,
) -> Account:
    """Authenticate against the Smart INTL API (3-step flow).

    Per contracts/smart-api.md INTL endpoints and research.md R2.
    """
    account = Account(
        username=email,
        region=Region.INTL,
        device_id=_generate_device_id(INTL_DEVICE_ID_LENGTH),
    )

    # Step 1: POST login
    login_url = f"{INTL_AUTH_BASE_URL}/iam/service/api/v1/login"
    login_headers = {
        "Content-Type": "application/json;charset=UTF-8",
        "Accept": "application/json;charset=UTF-8",
        "X-Ca-Key": INTL_X_CA_KEY,
        "X-Ca-Nonce": str(uuid.uuid4()),
        "X-Ca-Timestamp": str(int(time.time() * 1000)),
        "X-App-Id": INTL_APP_ID,
        "User-Agent": "ALIYUN-ANDROID-DEMO",
    }
    login_body = json.dumps({"email": email, "password": password})

    async with session.post(
        login_url, data=login_body, headers=login_headers
    ) as resp:
        resp.raise_for_status()
        login_data = await resp.json()

    result = login_data.get("result", {})
    intl_access_token = result.get("accessToken", "")
    intl_id_token = result.get("idToken", "")
    intl_user_id = result.get("userId", "")
    expires_in = result.get("expiresIn", 86400)

    if not intl_access_token:
        _LOGGER.error("INTL login failed: no access token returned")
        account.state = AuthState.AUTH_FAILED
        raise AuthenticationError("INTL login failed: invalid credentials")

    _LOGGER.debug("INTL login step 1 complete for user")

    # Step 2: GET authorize
    authorize_url = (
        f"{INTL_AUTH_BASE_URL}/iam/service/api/v1/oauth20/authorize"
        f"?accessToken={intl_access_token}"
    )
    authorize_headers = {
        "Content-Type": "application/json;charset=UTF-8",
        "Accept": "application/json;charset=UTF-8",
        "X-Ca-Key": INTL_X_CA_KEY,
        "X-Ca-Nonce": str(uuid.uuid4()),
        "X-Ca-Timestamp": str(int(time.time() * 1000)),
        "X-App-Id": INTL_APP_ID,
        "User-Agent": "ALIYUN-ANDROID-DEMO",
        "Xs-Auth-Token": intl_id_token,
    }

    async with session.get(authorize_url, headers=authorize_headers) as resp:
        resp.raise_for_status()
        auth_data = await resp.json()

    auth_code = auth_data.get("result", "")
    if not auth_code:
        _LOGGER.error("INTL authorize failed: no auth code returned")
        account.state = AuthState.AUTH_FAILED
        raise AuthenticationError("INTL authorize failed")

    _LOGGER.debug("INTL login step 2 complete (auth code obtained)")

    # Step 3: POST session exchange
    session_url = (
        f"{INTL_API_BASE_URL}{API_SESSION_PATH}"
        f"?identity_type={INTL_IDENTITY_TYPE}"
    )
    session_body_str = json.dumps({"authCode": auth_code})
    session_headers = _build_intl_session_headers(session_body_str, account.device_id)

    async with session.post(
        session_url, data=session_body_str, headers=session_headers
    ) as resp:
        resp.raise_for_status()
        session_data = await resp.json()

    if session_data.get("code") != 1000:
        _LOGGER.error("INTL session exchange failed: code=%s", session_data.get("code"))
        account.state = AuthState.AUTH_FAILED
        raise AuthenticationError("INTL session exchange failed")

    data = session_data.get("data", {})
    account.api_access_token = data.get("accessToken", "")
    account.api_refresh_token = data.get("refreshToken", "")
    account.api_user_id = data.get("userId", "")
    account.api_client_id = data.get("clientId", "")
    account.access_token = intl_access_token
    account.state = AuthState.AUTHENTICATED

    from datetime import datetime, timedelta

    account.expires_at = datetime.now() + timedelta(seconds=expires_in)

    _LOGGER.debug("INTL login complete — session established")
    return account


async def async_login_eu(
    session: aiohttp.ClientSession,
    email: str,
    password: str,
) -> Account:
    """Authenticate against the Smart EU API (4-step Gigya flow).

    Per contracts/smart-api.md EU endpoints and research.md R1.
    """
    account = Account(
        username=email,
        region=Region.EU,
        device_id=_generate_device_id(EU_DEVICE_ID_LENGTH),
    )

    # Step 1: GET context
    context_url = (
        f"{EU_CONTEXT_URL}/login-app/api/v1/authorize?uiLocales=de-DE"
    )
    context_headers = {
        "x-app-id": EU_APP_ID,
        "x-requested-with": "com.smart.hellosmart",
        "accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
    }

    async with session.get(
        context_url, headers=context_headers, allow_redirects=False
    ) as resp:
        if resp.status not in (301, 302, 303, 307):
            _LOGGER.error("EU context request did not redirect: status=%s", resp.status)
            account.state = AuthState.AUTH_FAILED
            raise AuthenticationError("EU context request failed")

        location = resp.headers.get("Location", "")

    parsed_location = urlparse(location)
    context_params = parse_qs(parsed_location.query)
    context = context_params.get("context", [None])[0]

    if not context:
        _LOGGER.error("EU context extraction failed from redirect URL")
        account.state = AuthState.AUTH_FAILED
        raise AuthenticationError("EU context extraction failed")

    _LOGGER.debug("EU login step 1 complete (context obtained)")

    # Step 2: POST Gigya login
    gigya_url = f"{EU_AUTH_BASE_URL}/accounts.login"
    gigya_body = urlencode(
        {
            "loginID": email,
            "password": password,
            "sessionExpiration": "2592000",
            "targetEnv": "jssdk",
            "include": "profile,data,emails,subscriptions,preferences,",
            "includeUserInfo": "True",
            "loginMode": "standard",
            "lang": "de",
            "APIKey": GIGYA_API_KEY,
            "source": "showScreenSet",
            "sdk": "js_latest",
            "sdkBuild": "15482",
            "format": "json",
        }
    )
    gigya_headers = {"Content-Type": "application/x-www-form-urlencoded"}

    async with session.post(gigya_url, data=gigya_body, headers=gigya_headers) as resp:
        resp.raise_for_status()
        gigya_data = await resp.json(content_type=None)

    # Gigya returns 200 even on errors
    if "errorCode" in gigya_data and gigya_data["errorCode"] != 0:
        _LOGGER.error(
            "EU Gigya login failed: code=%s", gigya_data.get("errorCode")
        )
        account.state = AuthState.AUTH_FAILED
        raise AuthenticationError("EU Gigya login failed: invalid credentials")

    session_info = gigya_data.get("sessionInfo", {})
    login_token = session_info.get("login_token", "")
    expires_in = session_info.get("expires_in", 3600)

    if not login_token:
        _LOGGER.error("EU Gigya login failed: no login_token")
        account.state = AuthState.AUTH_FAILED
        raise AuthenticationError("EU Gigya login failed")

    _LOGGER.debug("EU login step 2 complete (login_token obtained)")

    # Step 3: GET authorize continue
    authorize_url = (
        f"{EU_AUTH_BASE_URL}/oidc/op/v1.0/{GIGYA_API_KEY}/authorize/continue"
        f"?context={context}&login_token={login_token}"
    )

    async with session.get(authorize_url, allow_redirects=False) as resp:
        if resp.status not in (301, 302, 303, 307):
            _LOGGER.error(
                "EU authorize continue did not redirect: status=%s", resp.status
            )
            account.state = AuthState.AUTH_FAILED
            raise AuthenticationError("EU authorize continue failed")

        redirect_location = resp.headers.get("Location", "")

    # Extract access_token from URL fragment
    fragment = urlparse(redirect_location).fragment
    fragment_params = parse_qs(fragment)
    eu_access_token = fragment_params.get("access_token", [None])[0]

    if not eu_access_token:
        _LOGGER.error("EU access token extraction failed from redirect fragment")
        account.state = AuthState.AUTH_FAILED
        raise AuthenticationError("EU access token extraction failed")

    _LOGGER.debug("EU login step 3 complete (access_token obtained)")

    # Step 4: POST session exchange
    session_url = (
        f"{EU_API_BASE_URL}/auth/account/session/secure"
        f"?identity_type={EU_IDENTITY_TYPE}"
    )
    session_body = {"accessToken": eu_access_token}
    session_body_bytes = aiohttp.payload.JsonPayload(session_body)._value

    signed_headers = build_signed_headers(
        "POST",
        session_url,
        session_body_bytes,
        Account(
            username=email,
            region=Region.EU,
            device_id=account.device_id,
            api_access_token=eu_access_token,
        ),
    )

    async with session.post(
        session_url, json=session_body, headers=signed_headers
    ) as resp:
        resp.raise_for_status()
        session_data = await resp.json()

    if session_data.get("code") != 1000:
        _LOGGER.error(
            "EU session exchange failed: code=%s", session_data.get("code")
        )
        account.state = AuthState.AUTH_FAILED
        raise AuthenticationError("EU session exchange failed")

    data = session_data.get("data", {})
    account.api_access_token = data.get("accessToken", "")
    account.api_refresh_token = data.get("refreshToken", "")
    account.api_user_id = data.get("userId", "")
    account.access_token = eu_access_token
    account.state = AuthState.AUTHENTICATED

    from datetime import datetime, timedelta

    account.expires_at = datetime.now() + timedelta(seconds=expires_in)

    _LOGGER.debug("EU login complete — session established")
    return account


class AuthenticationError(Exception):
    """Raised when Smart API authentication fails."""
