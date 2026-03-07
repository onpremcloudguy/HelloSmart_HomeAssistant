#!/usr/bin/env python3
"""Manual Smart API test script for developer debugging.

Usage:
    python scripts/debug/test_smart_api.py --email user@example.com --password secret --region INTL
    python scripts/debug/test_smart_api.py --email user@example.com --password secret --region EU

Requires: Python 3.13+, aiohttp (pip install aiohttp)

Works standalone — does NOT require Home Assistant to be installed.
"""

from __future__ import annotations

import argparse
import asyncio
import importlib
import importlib.util
import json
import sys
import types
from pathlib import Path

# ---------------------------------------------------------------------------
# Bootstrap: load hello_smart sub-modules without triggering __init__.py
# (which imports homeassistant).  We create a minimal package stub and then
# import only const → models → auth → api.
# ---------------------------------------------------------------------------
_PKG_DIR = Path(__file__).resolve().parents[2] / "custom_components" / "hello_smart"

def _load_module(name: str, deps: dict[str, types.ModuleType] | None = None) -> types.ModuleType:
    """Load a single .py file as hello_smart.<name> with relative-import support."""
    full_name = f"hello_smart.{name}"
    spec = importlib.util.spec_from_file_location(full_name, _PKG_DIR / f"{name}.py")
    mod = importlib.util.module_from_spec(spec)  # type: ignore[arg-type]
    sys.modules[full_name] = mod
    if deps:
        for dep_name, dep_mod in deps.items():
            sys.modules[f"hello_smart.{dep_name}"] = dep_mod
    spec.loader.exec_module(mod)  # type: ignore[union-attr]
    return mod

# Create a bare package so relative imports resolve
_pkg = types.ModuleType("hello_smart")
_pkg.__path__ = [str(_PKG_DIR)]  # type: ignore[attr-defined]
sys.modules["hello_smart"] = _pkg

_const = _load_module("const")
_models = _load_module("models", {"const": _const})
_auth = _load_module("auth", {"const": _const, "models": _models})
_api = _load_module("api", {"const": _const, "models": _models, "auth": _auth})

import aiohttp  # noqa: E402

# Re-export what we need under readable names
async_login_intl = _auth.async_login_intl
async_login_eu = _auth.async_login_eu
AuthenticationError = _auth.AuthenticationError
SmartAPI = _api.SmartAPI
SmartAPIError = _api.SmartAPIError
Region = _models.Region

# Fields to mask in output
_REDACT_KEYS = {
    "access_token",
    "accessToken",
    "refresh_token",
    "refreshToken",
    "api_access_token",
    "api_refresh_token",
    "password",
    "userId",
    "api_user_id",
    "login_token",
    "idToken",
    "authCode",
    "api_client_id",
    "clientId",
}


def _redact(obj: object) -> object:
    """Recursively replace sensitive values with **REDACTED**."""
    if isinstance(obj, dict):
        return {
            k: "**REDACTED**" if k in _REDACT_KEYS else _redact(v)
            for k, v in obj.items()
        }
    if isinstance(obj, list):
        return [_redact(item) for item in obj]
    return obj


def _account_summary(account: object) -> dict:
    """Build a redacted summary dict from an Account dataclass."""
    from dataclasses import asdict
    from datetime import datetime
    from enum import Enum

    raw = asdict(account)  # type: ignore[arg-type]
    redacted = _redact(raw)  # type: ignore[return-value]

    def _make_serializable(obj: object) -> object:
        if isinstance(obj, dict):
            return {k: _make_serializable(v) for k, v in obj.items()}
        if isinstance(obj, list):
            return [_make_serializable(i) for i in obj]
        if isinstance(obj, datetime):
            return obj.isoformat()
        if isinstance(obj, Enum):
            return obj.value
        return obj

    return _make_serializable(redacted)  # type: ignore[return-value]


async def _verbose_login_intl(
    session: aiohttp.ClientSession, email: str, password: str
) -> "Account":
    """INTL login with full raw-response tracing at each step."""
    import secrets as _secrets
    import time as _time

    Account = _models.Account
    Region = _models.Region
    AuthState = _models.AuthState

    device_id = _secrets.token_hex(16)
    account = Account(username=email, region=Region.INTL, device_id=device_id)

    # Step 1: POST login
    print("\n  --- INTL Step 1: POST login ---")
    login_url = f"{_const.INTL_AUTH_BASE_URL}/iam/service/api/v1/login"
    login_headers = {
        "X-Ca-Key": _const.INTL_X_CA_KEY,
        "X-Ca-Nonce": _secrets.token_hex(16),
        "X-Ca-Timestamp": str(int(_time.time() * 1000)),
        "X-App-Id": _const.INTL_APP_ID,
        "User-Agent": "ALIYUN-ANDROID-DEMO",
        "Content-Type": "application/json",
    }
    login_body = {"email": email, "password": password}

    print(f"  URL: {login_url}")
    print(f"  Headers: {json.dumps(_redact(login_headers), indent=4)}")

    async with session.post(login_url, json=login_body, headers=login_headers) as resp:
        print(f"  Status: {resp.status}")
        login_data = await resp.json()
        print(f"  Response: {json.dumps(_redact(login_data), indent=4)}")

    result = login_data.get("result", {})
    intl_access_token = result.get("accessToken", "")
    intl_id_token = result.get("idToken", "")
    expires_in = result.get("expiresIn", 86400)

    if not intl_access_token:
        raise Exception("Step 1 failed: no accessToken in result")

    print("  ✓ Step 1 OK")

    # Step 2: GET authorize
    print("\n  --- INTL Step 2: GET authorize ---")
    authorize_url = (
        f"{_const.INTL_AUTH_BASE_URL}/iam/service/api/v1/oauth20/authorize"
        f"?accessToken={intl_access_token}"
    )
    authorize_headers = {
        "X-Ca-Key": _const.INTL_X_CA_KEY,
        "X-Ca-Nonce": _secrets.token_hex(16),
        "X-Ca-Timestamp": str(int(_time.time() * 1000)),
        "X-App-Id": _const.INTL_APP_ID,
        "Xs-Auth-Token": intl_id_token,
    }

    print(f"  URL: {_redact_url(authorize_url)}")
    print(f"  Headers: {json.dumps(_redact(authorize_headers), indent=4)}")

    async with session.get(authorize_url, headers=authorize_headers) as resp:
        print(f"  Status: {resp.status}")
        auth_data = await resp.json()
        print(f"  Response: {json.dumps(_redact(auth_data), indent=4)}")

    auth_code = auth_data.get("result", "")
    if not auth_code:
        raise Exception("Step 2 failed: no authCode in result")

    print("  ✓ Step 2 OK")

    # Step 3: POST session exchange
    print("\n  --- INTL Step 3: POST session exchange ---")
    session_url = (
        f"{_const.INTL_API_BASE_URL}/auth/account/session/secure"
        f"?identity_type={_const.INTL_IDENTITY_TYPE}"
    )
    session_body_str = json.dumps({"authCode": auth_code}, separators=(",", ":"))

    # Build signed headers using the dedicated INTL session header builder
    signed_headers = _auth._build_intl_session_headers(session_body_str, device_id)

    print(f"  URL: {session_url}")
    print(f"  Body: {session_body_str[:40]}...")
    print(f"  Signed headers: {json.dumps(_redact(signed_headers), indent=4)}")

    async with session.post(session_url, data=session_body_str, headers=signed_headers) as resp:
        print(f"  Status: {resp.status}")
        session_data = await resp.json()
        print(f"  Response (raw keys): {list(session_data.keys())}")
        print(f"  Response code: {session_data.get('code')} (type: {type(session_data.get('code')).__name__})")
        data_keys = list(session_data.get("data", {}).keys()) if isinstance(session_data.get("data"), dict) else "N/A"
        print(f"  Response data keys: {data_keys}")
        print(f"  Response (redacted): {json.dumps(_redact(session_data), indent=4)}")

    code = session_data.get("code")
    if code != 1000 and str(code) != "1000":
        raise Exception(f"Step 3 failed: code={code}")

    data = session_data.get("data", {})
    account.api_access_token = data.get("accessToken", "")
    account.api_refresh_token = data.get("refreshToken", "")
    account.api_user_id = data.get("userId", "")
    account.api_client_id = data.get("clientId", "")
    account.access_token = intl_access_token
    account.state = AuthState.AUTHENTICATED

    from datetime import datetime, timedelta
    account.expires_at = datetime.now() + timedelta(seconds=expires_in)

    print(f"  Token present: {bool(account.api_access_token)}")
    print(f"  Token length: {len(account.api_access_token)}")
    print(f"  User ID present: {bool(account.api_user_id)}")
    print("  ✓ Step 3 OK")

    # Now trace what a vehicle request would look like
    print("\n  --- Trace: Vehicle list request headers ---")
    vehicle_url = (
        f"{_const.EU_API_BASE_URL}/device-platform/user/vehicle/secure"
        f"?needSharedCar=1&userId={account.api_user_id}"
    )
    vehicle_headers = _auth.build_signed_headers("GET", vehicle_url, None, account)
    print(f"  URL: {_redact_url(vehicle_url)}")
    print(f"  Headers: {json.dumps(_redact(vehicle_headers), indent=4)}")

    return account


async def _verbose_login_eu(
    session: aiohttp.ClientSession, email: str, password: str
) -> "Account":
    """EU login — for now, fall back to standard flow with basic logging."""
    print("  (EU verbose tracing not yet implemented — using standard flow)")
    return await async_login_eu(session, email, password)


def _redact_url(url: str) -> str:
    """Redact token values from URL query strings."""
    from urllib.parse import urlparse, parse_qs, urlencode, urlunparse
    parsed = urlparse(url)
    params = parse_qs(parsed.query)
    for key in list(params.keys()):
        if key.lower() in {"accesstoken", "token", "userid"}:
            params[key] = ["**REDACTED**"]
    redacted_query = urlencode({k: v[0] for k, v in params.items()})
    return urlunparse(parsed._replace(query=redacted_query))


async def run(email: str, password: str, region: str, verbose: bool = False) -> None:
    """Execute the test flow: login → vehicles → status → SOC → OTA."""
    region_enum = Region(region.upper())

    async with aiohttp.ClientSession() as session:
        # --- Step 1: Authenticate ---
        print(f"\n{'='*60}")
        print(f"  Smart API Test — Region: {region_enum.value}")
        print(f"{'='*60}")

        if verbose:
            print("\n[1/5] Authenticating (verbose — showing raw responses)...")
            try:
                account = await _verbose_login_intl(session, email, password) if region_enum == Region.INTL else await _verbose_login_eu(session, email, password)
            except Exception as exc:
                print(f"  FAILED: {exc}")
                return
        else:
            print("\n[1/5] Authenticating...")
            try:
                if region_enum == Region.INTL:
                    account = await async_login_intl(session, email, password)
                else:
                    account = await async_login_eu(session, email, password)
            except AuthenticationError as exc:
                print(f"  FAILED: {exc}")
                return

        print("  OK — authenticated")
        print(f"  Account: {json.dumps(_account_summary(account), indent=2)}")

        api = SmartAPI(session)

        # --- Step 2: Discover vehicles ---
        print("\n[2/5] Fetching vehicles...")
        try:
            vehicles = await api.async_get_vehicles(account)
        except SmartAPIError as exc:
            print(f"  FAILED: {exc}")
            return

        if not vehicles:
            print("  No vehicles found — check account linking.")
            return

        for v in vehicles:
            vin_short = v.vin[:6] + "..." if v.vin else "???"
            print(f"  VIN: {vin_short}  Model: {v.model_name}  Year: {v.model_year}")

        # Process first vehicle for remaining tests
        vehicle = vehicles[0]

        # --- Step 3: Select vehicle & fetch status ---
        print(f"\n[3/5] Selecting vehicle {vehicle.vin[:6]}... and fetching status...")
        try:
            await api.async_select_vehicle(account, vehicle.vin)
            status = await api.async_get_vehicle_status(account, vehicle.vin)
        except SmartAPIError as exc:
            print(f"  FAILED: {exc}")
            return

        print(f"  Battery: {status.battery_level}%")
        print(f"  Range:   {status.range_remaining} km")
        print(f"  Charging: {status.charging_state.value}")
        print(f"  Charger connected: {status.charger_connected}")
        print(f"  Doors: {status.doors}")
        print(f"  Windows: {status.windows}")
        if status.latitude is not None:
            print(f"  GPS: ({status.latitude}, {status.longitude})")
        else:
            print("  GPS: not available")

        # --- Step 4: Fetch SOC detail ---
        print("\n[4/5] Fetching SOC/charging detail...")
        try:
            soc_data = await api.async_get_soc(account, vehicle.vin)
            print(f"  SOC data: {json.dumps(_redact(soc_data), indent=2)}")
        except SmartAPIError as exc:
            print(f"  FAILED (non-critical): {exc}")

        # --- Step 5: Fetch OTA info ---
        print("\n[5/5] Fetching OTA firmware info...")
        try:
            ota = await api.async_get_ota_info(account, vehicle.vin)
            print(f"  Current firmware: {ota.current_version}")
            print(f"  Target firmware:  {ota.target_version}")
            print(f"  Update available: {ota.update_available}")
        except SmartAPIError as exc:
            print(f"  FAILED (non-critical): {exc}")

        print(f"\n{'='*60}")
        print("  Test complete")
        print(f"{'='*60}\n")


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Manual Smart API connectivity test"
    )
    parser.add_argument("--email", required=True, help="Smart account email")
    parser.add_argument("--password", required=True, help="Smart account password")
    parser.add_argument(
        "--region",
        required=True,
        choices=["EU", "INTL", "eu", "intl"],
        help="Account region (EU or INTL)",
    )
    parser.add_argument(
        "--verbose", "-v",
        action="store_true",
        help="Show raw API responses for debugging",
    )
    args = parser.parse_args()
    asyncio.run(run(args.email, args.password, args.region, verbose=args.verbose))


if __name__ == "__main__":
    main()
