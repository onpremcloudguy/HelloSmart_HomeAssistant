"""Smart vehicle cloud API client."""

from __future__ import annotations

import json
import logging
from urllib.parse import urlparse

import aiohttp

from .auth import AuthenticationError, build_signed_headers
from .const import (
    API_CODE_SUCCESS,
    API_CODE_TOKEN_EXPIRED,
    API_CODE_VEHICLE_NOT_LINKED,
    EU_API_BASE_URL,
    OTA_BASE_URL,
    URL_ALLOWLIST,
)
from .models import (
    Account,
    AuthState,
    ChargingState,
    OTAInfo,
    Vehicle,
    VehicleData,
    VehicleStatus,
    charging_state_from_api,
)

_LOGGER = logging.getLogger(__name__)


class SmartAPIError(Exception):
    """Base exception for Smart API errors."""


class TokenExpiredError(SmartAPIError):
    """Raised when the API reports token expiry (code 1402 or HTTP 401)."""


class VehicleNotLinkedError(SmartAPIError):
    """Raised when the API reports vehicle not linked (code 8006)."""


class RateLimitedError(SmartAPIError):
    """Raised when the API returns HTTP 429."""

    def __init__(self, retry_after: int = 60) -> None:
        super().__init__(f"Rate limited, retry after {retry_after}s")
        self.retry_after = retry_after


class SmartAPI:
    """Client for the Smart vehicle cloud API."""

    def __init__(self, session: aiohttp.ClientSession) -> None:
        self._session = session

    def _validate_url(self, url: str) -> None:
        """Validate URL against the allowlist (FR-015) and enforce HTTPS (FR-016)."""
        parsed = urlparse(url)
        if parsed.scheme != "https":
            raise SmartAPIError(f"HTTPS required, got {parsed.scheme}")
        if parsed.hostname not in URL_ALLOWLIST:
            raise SmartAPIError(f"URL host not in allowlist: {parsed.hostname}")

    async def _signed_request(
        self,
        method: str,
        url: str,
        account: Account,
        *,
        json_body: dict | None = None,
    ) -> dict:
        """Execute a signed API request and handle standard error codes."""
        self._validate_url(url)

        body_str: str | None = None
        if json_body is not None:
            body_str = json.dumps(json_body)

        headers = build_signed_headers(method, url, body_str, account)

        kwargs: dict = {"headers": headers}
        if body_str is not None:
            kwargs["data"] = body_str

        async with self._session.request(method, url, **kwargs) as resp:
            if resp.status == 401:
                raise TokenExpiredError("HTTP 401 Unauthorized")
            if resp.status == 429:
                retry_after = int(resp.headers.get("Retry-After", "60"))
                raise RateLimitedError(retry_after)
            resp.raise_for_status()
            data = await resp.json()

        code = data.get("code")
        try:
            code = int(code) if code is not None else None
        except (ValueError, TypeError):
            pass
        if code == API_CODE_TOKEN_EXPIRED:
            raise TokenExpiredError("API code 1402: token expired")
        if code == API_CODE_VEHICLE_NOT_LINKED:
            raise VehicleNotLinkedError("API code 8006: vehicle not linked")
        if code != API_CODE_SUCCESS:
            raise SmartAPIError(f"API error code {code}: {data}")

        return data

    async def async_get_vehicles(self, account: Account) -> list[Vehicle]:
        """Fetch list of vehicles for the authenticated account."""
        base_url = self._get_base_url(account)
        url = (
            f"{base_url}/device-platform/user/vehicle/secure"
            f"?needSharedCar=1&userId={account.api_user_id}"
        )

        data = await self._signed_request("GET", url, account)

        vehicles: list[Vehicle] = []
        for item in data.get("data", {}).get("list", []):
            vehicle = Vehicle(
                vin=item.get("vin", ""),
                model_name=item.get("modelName", ""),
                model_year=item.get("modelYear", ""),
                series_code=item.get("seriesCodeVs", ""),
                base_url=base_url,
            )
            vehicles.append(vehicle)

        _LOGGER.debug("Discovered %d vehicle(s)", len(vehicles))
        return vehicles

    async def async_select_vehicle(
        self, account: Account, vin: str
    ) -> None:
        """Select the active vehicle (required before fetching status)."""
        base_url = self._get_base_url(account)
        url = f"{base_url}/device-platform/user/session/update"
        body = {
            "vin": vin,
            "sessionToken": account.api_access_token,
            "language": "",
        }

        await self._signed_request("POST", url, account, json_body=body)
        _LOGGER.debug("Selected vehicle %s", vin[:6] + "...")

    async def async_get_vehicle_status(
        self, account: Account, vin: str
    ) -> VehicleStatus:
        """Fetch current status for a vehicle."""
        from .models import Region

        base_url = self._get_base_url(account)
        if account.region == Region.EU:
            latest = "true"
        else:
            # INTL: Python bool repr per reference
            latest = "False"
        target = "basic,more"
        url = (
            f"{base_url}/remote-control/vehicle/status/{vin}"
            f"?latest={latest}&target={target}&userId={account.api_user_id}"
        )

        data = await self._signed_request("GET", url, account)

        vehicle_status_data = (
            data.get("data", {})
            .get("vehicleStatus", {})
            .get("additionalVehicleStatus", {})
        )

        return self._parse_vehicle_status(vehicle_status_data, data)

    async def async_get_soc(
        self, account: Account, vin: str
    ) -> dict:
        """Fetch SOC / charging detail for a vehicle."""
        base_url = self._get_base_url(account)
        url = (
            f"{base_url}/remote-control/vehicle/status/soc/{vin}"
            f"?setting=charging"
        )

        data = await self._signed_request("GET", url, account)
        return data.get("data", {})

    async def async_get_ota_info(
        self, account: Account, vin: str
    ) -> OTAInfo:
        """Fetch OTA firmware info for a vehicle (different host, no HMAC signing)."""
        url = f"{OTA_BASE_URL}/app/info/{vin}"
        self._validate_url(url)

        headers = {
            "id-token": account.device_id,
            "access_token": account.api_access_token,
            "content-type": "application/json",
        }

        async with self._session.get(url, headers=headers) as resp:
            if resp.status == 403:
                _LOGGER.debug("OTA endpoint returned 403 — may not be available for this region")
                return OTAInfo(current_version="", target_version="")
            resp.raise_for_status()
            data = await resp.json()

        return OTAInfo(
            current_version=data.get("currentVersion", ""),
            target_version=data.get("targetVersion", ""),
        )

    @staticmethod
    def _get_base_url(account: Account) -> str:
        """Get the API base URL for the account's region.

        Both EU and INTL use api.ecloudeu.com for vehicle data.
        apiv2.ecloudeu.com is only used for INTL session exchange (in auth.py).
        """
        return EU_API_BASE_URL

    @staticmethod
    def _parse_vehicle_status(
        additional_status: dict, raw_data: dict
    ) -> VehicleStatus:
        """Parse the nested additionalVehicleStatus response into VehicleStatus."""
        from datetime import datetime

        ev = additional_status.get("electricVehicleStatus", {})
        doors_raw = additional_status.get("doorsStatus", {})
        windows_raw = additional_status.get("windowStatus", {})
        climate_raw = additional_status.get("climateStatus", {})

        # Parse battery and range
        battery_level = int(ev.get("chargeLevel", 0) or 0)
        battery_level = max(0, min(100, battery_level))
        range_remaining = float(ev.get("distanceToEmptyOnBatteryOnly", 0) or 0)

        # Parse charging state
        charger_state_raw = int(ev.get("chargerState", 0) or 0)
        charging_state = charging_state_from_api(charger_state_raw)
        charger_connected = str(ev.get("statusOfChargerConnection", "0")) == "1"

        # Parse doors (values are typically "0"=closed, "1"=open)
        doors: dict[str, bool] = {}
        for key, value in doors_raw.items():
            if isinstance(value, (str, int)):
                doors[key] = str(value) == "1"

        # Parse windows
        windows: dict[str, bool] = {}
        for key, value in windows_raw.items():
            if isinstance(value, (str, int)):
                windows[key] = str(value) == "1"

        # Parse climate
        climate_active = bool(climate_raw.get("climateActive", False))

        # Parse GPS from running status
        running_status = additional_status.get("runningStatus", {})
        gps_data = running_status.get("gpsInformation", {})
        latitude = None
        longitude = None
        if gps_data:
            try:
                lat = float(gps_data.get("latitude", 0))
                lon = float(gps_data.get("longitude", 0))
                if -90 <= lat <= 90 and -180 <= lon <= 180 and (lat != 0 or lon != 0):
                    latitude = lat
                    longitude = lon
            except (ValueError, TypeError):
                pass

        # Parse update time
        update_time = (
            raw_data.get("data", {}).get("vehicleStatus", {}).get("updateTime")
        )
        last_updated = None
        if update_time:
            try:
                last_updated = datetime.fromtimestamp(int(update_time) / 1000)
            except (ValueError, TypeError, OSError):
                pass

        return VehicleStatus(
            battery_level=battery_level,
            range_remaining=range_remaining,
            charging_state=charging_state,
            charger_connected=charger_connected,
            doors=doors,
            windows=windows,
            climate_active=climate_active,
            latitude=latitude,
            longitude=longitude,
            last_updated=last_updated,
        )
