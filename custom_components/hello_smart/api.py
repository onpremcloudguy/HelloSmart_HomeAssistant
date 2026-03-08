"""Smart vehicle cloud API client."""

from __future__ import annotations

import json
import logging
from datetime import datetime
from typing import Any
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
    ChargingReservation,
    ChargingState,
    ClimateSchedule,
    DiagnosticEntry,
    EnergyRanking,
    FOTANotification,
    FragranceDetails,
    FridgeStatus,
    GeofenceInfo,
    LockerSecret,
    LockerStatus,
    OTAInfo,
    Region,
    TelematicsStatus,
    TripJournal,
    Vehicle,
    VehicleCapabilities,
    VehicleData,
    VehicleRunningState,
    VehicleStatus,
    VtmSettings,
    charging_state_from_api,
    power_mode_from_api,
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

    async def async_get_vehicle_state(
        self, account: Account, vin: str
    ) -> VehicleRunningState:
        """Fetch condensed vehicle running state."""
        base_url = self._get_base_url(account)
        url = f"{base_url}/remote-control/vehicle/status/state/{vin}"
        data = await self._signed_request("GET", url, account)
        d = data.get("data", {})
        return VehicleRunningState(
            power_mode=power_mode_from_api(d.get("powerMode", "0")),
            speed=float(d.get("speed", 0) or 0),
        )

    async def async_get_telematics(
        self, account: Account, vin: str
    ) -> TelematicsStatus:
        """Fetch telematics unit status."""
        base_url = self._get_base_url(account)
        url = f"{base_url}/remote-control/vehicle/telematics/{vin}"
        data = await self._signed_request("GET", url, account)
        d = data.get("data", {})
        backup = d.get("backupBattery", {}) or {}
        connected_raw = d.get("connectivityStatus", "")
        return TelematicsStatus(
            connected=connected_raw == "connected" if connected_raw else None,
            sw_version=d.get("swVersion", ""),
            hw_version=d.get("hwVersion", ""),
            imei=d.get("imei", ""),
            power_mode=power_mode_from_api(d.get("powerMode", "0")) if d.get("powerMode") else None,
            backup_battery_voltage=float(backup.get("voltage", 0) or 0) if backup.get("voltage") else None,
            backup_battery_level=float(backup.get("stateOfCharge", 0) or 0) if backup.get("stateOfCharge") else None,
        )

    async def async_get_diagnostic_history(
        self, account: Account, vin: str
    ) -> DiagnosticEntry | None:
        """Fetch most recent diagnostic entry."""
        base_url = self._get_base_url(account)
        url = f"{base_url}/remote-control/vehicle/status/history/diagnostic/{vin}"
        data = await self._signed_request("GET", url, account)
        entries = data.get("data", {}).get("diagnosticList", [])
        if not entries:
            return None
        latest = entries[0]
        ts = None
        if latest.get("timestamp"):
            try:
                ts = datetime.fromtimestamp(int(latest["timestamp"]) / 1000)
            except (ValueError, TypeError, OSError):
                pass
        return DiagnosticEntry(
            dtc_code=latest.get("dtcCode", ""),
            severity=latest.get("severity", ""),
            timestamp=ts,
            status=latest.get("status", ""),
        )

    async def async_get_charging_reservation(
        self, account: Account, vin: str
    ) -> ChargingReservation:
        """Fetch charging reservation / schedule."""
        base_url = self._get_base_url(account)
        url = f"{base_url}/remote-control/charging/reservation/{vin}"
        data = await self._signed_request("GET", url, account)
        d = data.get("data", {})
        return ChargingReservation(
            active=d.get("reservationStatus") == "active",
            start_time=d.get("startTime", ""),
            end_time=d.get("endTime", ""),
            target_soc=int(d["targetSoc"]) if d.get("targetSoc") else None,
        )

    async def async_get_climate_schedule(
        self, account: Account, vin: str
    ) -> ClimateSchedule | None:
        """Fetch climate pre-conditioning schedule."""
        base_url = self._get_base_url(account)
        url = f"{base_url}/remote-control/schedule/{vin}"
        data = await self._signed_request("GET", url, account)
        d = data.get("data", {})
        if isinstance(d, list):
            schedules = d
        elif isinstance(d, dict):
            schedules = d.get("scheduleList", [])
        else:
            schedules = []
        if not schedules:
            return None
        s = schedules[0]
        return ClimateSchedule(
            enabled=bool(s.get("enabled", False)),
            scheduled_time=s.get("scheduledTime", ""),
            temperature=float(s["temperature"]) if s.get("temperature") else None,
            duration=int(s["duration"]) if s.get("duration") else None,
        )

    async def async_get_fridge_status(
        self, account: Account, vin: str
    ) -> FridgeStatus:
        """Fetch mini-fridge status."""
        base_url = self._get_base_url(account)
        url = f"{base_url}/remote-control/getFridge/status/{vin}"
        data = await self._signed_request("GET", url, account)
        d = data.get("data", {})
        return FridgeStatus(
            active=d.get("fridgeStatus") == "on",
            temperature=float(d["temperature"]) if d.get("temperature") else None,
            mode=d.get("mode", ""),
        )

    async def async_get_locker_status(
        self, account: Account, vin: str
    ) -> LockerStatus:
        """Fetch locker / front trunk status."""
        base_url = self._get_base_url(account)
        url = f"{base_url}/remote-control/getLocker/status/{vin}"
        data = await self._signed_request("GET", url, account)
        d = data.get("data", {})
        return LockerStatus(
            open=d.get("lockerStatus") == "open" if d.get("lockerStatus") else None,
            locked=d.get("lockStatus") == "locked" if d.get("lockStatus") else None,
        )

    async def async_get_vtm_settings(
        self, account: Account
    ) -> VtmSettings:
        """Fetch vehicle theft monitoring settings."""
        base_url = self._get_base_url(account)
        url = f"{base_url}/remote-control/getVtmSettingStatus"
        data = await self._signed_request("GET", url, account)
        d = data.get("data", {})
        return VtmSettings(
            enabled=bool(d.get("vtmEnabled", False)),
            notification_enabled=bool(d.get("notificationEnabled", False)),
            geofence_alert_enabled=bool(d.get("geofenceAlertEnabled", False)),
        )

    async def async_get_fragrance(
        self, account: Account, vin: str
    ) -> FragranceDetails:
        """Fetch extended fragrance system status."""
        base_url = self._get_base_url(account)
        url = f"{base_url}/remote-control/vehicle/fragrance/{vin}"
        data = await self._signed_request("GET", url, account)
        d = data.get("data", {})
        return FragranceDetails(
            active=bool(d.get("fragranceActive", False)),
            level=d.get("fragranceLevel", ""),
            fragrance_type=d.get("fragranceType", ""),
        )

    async def async_get_trip_journal(
        self, account: Account, vin: str
    ) -> TripJournal | None:
        """Fetch most recent trip from journal."""
        base_url = self._get_base_url(account)
        url = f"{base_url}/geelyTCAccess/tcservices/vehicle/status/journalLogV4/{vin}"
        data = await self._signed_request("GET", url, account)
        logs = data.get("data", {}).get("journalLogs", [])
        if not logs:
            return None
        t = logs[0]
        start_time = None
        end_time = None
        if t.get("startTime"):
            try:
                start_time = datetime.fromtimestamp(int(t["startTime"]) / 1000)
            except (ValueError, TypeError, OSError):
                pass
        if t.get("endTime"):
            try:
                end_time = datetime.fromtimestamp(int(t["endTime"]) / 1000)
            except (ValueError, TypeError, OSError):
                pass
        return TripJournal(
            trip_id=t.get("tripId", ""),
            distance=float(t["distance"]) if t.get("distance") else None,
            duration=int(t["duration"]) if t.get("duration") else None,
            energy_consumption=float(t["energyConsumption"]) if t.get("energyConsumption") else None,
            avg_energy_consumption=float(t["averageEnergyConsumption"]) if t.get("averageEnergyConsumption") else None,
            avg_speed=float(t["averageSpeed"]) if t.get("averageSpeed") else None,
            max_speed=float(t["maxSpeed"]) if t.get("maxSpeed") else None,
            start_time=start_time,
            end_time=end_time,
        )

    async def async_get_total_distance(
        self, account: Account, vin: str
    ) -> float | None:
        """Fetch total distance from TC endpoint."""
        base_url = self._get_base_url(account)
        url = f"{base_url}/geelyTCAccess/tcservices/vehicle/status/getTotalDistanceByLabel/{vin}"
        data = await self._signed_request("GET", url, account)
        d = data.get("data", {})
        if d.get("totalDistance"):
            try:
                return float(d["totalDistance"])
            except (ValueError, TypeError):
                pass
        return None

    async def async_get_geofences(
        self, account: Account, vin: str
    ) -> GeofenceInfo:
        """Fetch geofence summary."""
        base_url = self._get_base_url(account)
        url = f"{base_url}/geelyTCAccess/tcservices/vehicle/geofence/all/{vin}"
        data = await self._signed_request("GET", url, account)
        d = data.get("data", [])
        if isinstance(d, list):
            fences = d
        else:
            fences = d.get("geofences", []) if isinstance(d, dict) else []
        return GeofenceInfo(count=len(fences), geofences=fences)

    async def async_get_capabilities(
        self, account: Account, vin: str
    ) -> VehicleCapabilities:
        """Fetch vehicle capability flags."""
        base_url = self._get_base_url(account)
        url = f"{base_url}/geelyTCAccess/tcservices/capability/{vin}"
        data = await self._signed_request("GET", url, account)
        caps = data.get("data", {}).get("capabilities", [])
        service_ids = [c.get("serviceId", "") for c in caps if c.get("enabled")]
        return VehicleCapabilities(service_ids=service_ids)

    async def async_get_energy_ranking(
        self, account: Account, vin: str,
        latitude: float = 0.0, longitude: float = 0.0,
    ) -> EnergyRanking:
        """Fetch energy consumption ranking."""
        base_url = self._get_base_url(account)
        url = (
            f"{base_url}/geelyTCAccess/tcservices/vehicle/status/ranking/"
            f"aveEnergyConsumption/vehicleModel/{vin}"
            f"?topn=100&latitude={latitude}&longitude={longitude}"
        )
        data = await self._signed_request("GET", url, account)
        d = data.get("data", {})
        return EnergyRanking(
            my_ranking=int(d["myRanking"]) if d.get("myRanking") else None,
            my_value=float(d["myValue"]) if d.get("myValue") else None,
            total_participants=int(d["totalParticipants"]) if d.get("totalParticipants") else None,
        )

    async def async_get_fota_notification(
        self, account: Account
    ) -> FOTANotification:
        """Fetch FOTA notification status."""
        base_url = self._get_base_url(account)
        url = f"{base_url}/fota/geea/assignment/notification"
        data = await self._signed_request("GET", url, account)
        d = data.get("data", {})
        notifications = d.get("notifications", []) if isinstance(d, dict) else []
        return FOTANotification(
            has_notification=bool(notifications),
            pending_count=len(notifications),
        )

    async def async_get_locker_secret(
        self, account: Account, vin: str
    ) -> LockerSecret:
        """Fetch locker secret/PIN configuration status."""
        base_url = self._get_base_url(account)
        url = f"{base_url}/remote-control/locker/secret/{vin}"
        data = await self._signed_request("GET", url, account)
        d = data.get("data", {})
        return LockerSecret(
            has_secret=bool(d.get("hasSecret")),
            secret_set=bool(d.get("secretSet")),
        )

    async def async_get_plant_no(
        self, account: Account, vin: str
    ) -> str:
        """Fetch factory plant number."""
        base_url = self._get_base_url(account)
        url = f"{base_url}/geelyTCAccess/tcservices/customer/vehicle/plantNo/{vin}"
        data = await self._signed_request("GET", url, account)
        return data.get("data", {}).get("plantNo", "")

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
        ev = additional_status.get("electricVehicleStatus", {})
        doors_raw = additional_status.get("doorsStatus", {})
        windows_raw = additional_status.get("windowStatus", {})
        climate_raw = additional_status.get("climateStatus", {})
        maintenance_raw = additional_status.get("maintenanceStatus", {})
        basic_raw = additional_status.get("basicVehicleStatus", {})

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

        # Parse tyre data from maintenanceStatus
        def _safe_float(val: Any) -> float | None:
            if val is None:
                return None
            try:
                return float(val)
            except (ValueError, TypeError):
                return None

        def _safe_int(val: Any) -> int | None:
            if val is None:
                return None
            try:
                return int(val)
            except (ValueError, TypeError):
                return None

        def _safe_bool(val: Any) -> bool | None:
            if val is None:
                return None
            return str(val).lower() in ("1", "true")

        tyre_pressure_fl = _safe_float(maintenance_raw.get("tyreStatusDriver"))
        tyre_pressure_fr = _safe_float(maintenance_raw.get("tyreStatusPassenger"))
        tyre_pressure_rl = _safe_float(maintenance_raw.get("tyreStatusDriverRear"))
        tyre_pressure_rr = _safe_float(maintenance_raw.get("tyreStatusPassengerRear"))
        tyre_temp_fl = _safe_float(maintenance_raw.get("tyreTempDriver"))
        tyre_temp_fr = _safe_float(maintenance_raw.get("tyreTempPassenger"))
        tyre_temp_rl = _safe_float(maintenance_raw.get("tyreTempDriverRear"))
        tyre_temp_rr = _safe_float(maintenance_raw.get("tyreTempPassengerRear"))
        tyre_warning_fl = _safe_bool(maintenance_raw.get("tyrePreWarningDriver"))
        tyre_warning_fr = _safe_bool(maintenance_raw.get("tyrePreWarningPassenger"))
        tyre_warning_rl = _safe_bool(maintenance_raw.get("tyrePreWarningDriverRear"))
        tyre_warning_rr = _safe_bool(maintenance_raw.get("tyrePreWarningPassengerRear"))

        # Maintenance fields
        odometer = _safe_float(maintenance_raw.get("odometer"))
        days_to_service = _safe_int(maintenance_raw.get("daysToService"))
        distance_to_service = _safe_float(maintenance_raw.get("distanceToService"))
        washer_fluid_level = _safe_int(maintenance_raw.get("washerFluidLevelStatus"))
        brake_fluid_ok = _safe_bool(maintenance_raw.get("brakeFluidLevelStatus"))

        # 12V battery from maintenanceStatus.mainBatteryStatus
        main_battery = maintenance_raw.get("mainBatteryStatus", {})
        battery_12v_voltage = _safe_float(main_battery.get("voltage")) if main_battery else None
        battery_12v_level = _safe_float(main_battery.get("chargeLevel")) if main_battery else None

        # Climate extras
        fragrance_active = _safe_bool(climate_raw.get("fragActive"))
        interior_temp = _safe_float(climate_raw.get("interiorTemp"))
        exterior_temp = _safe_float(climate_raw.get("exteriorTemp"))

        # Power mode from basicVehicleStatus
        power_mode_raw = basic_raw.get("engineStatus")
        power_mode = power_mode_from_api(power_mode_raw) if power_mode_raw is not None else None

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
            tyre_pressure_fl=tyre_pressure_fl,
            tyre_pressure_fr=tyre_pressure_fr,
            tyre_pressure_rl=tyre_pressure_rl,
            tyre_pressure_rr=tyre_pressure_rr,
            tyre_temp_fl=tyre_temp_fl,
            tyre_temp_fr=tyre_temp_fr,
            tyre_temp_rl=tyre_temp_rl,
            tyre_temp_rr=tyre_temp_rr,
            tyre_warning_fl=tyre_warning_fl,
            tyre_warning_fr=tyre_warning_fr,
            tyre_warning_rl=tyre_warning_rl,
            tyre_warning_rr=tyre_warning_rr,
            odometer=odometer,
            days_to_service=days_to_service,
            distance_to_service=distance_to_service,
            washer_fluid_level=washer_fluid_level,
            brake_fluid_ok=brake_fluid_ok,
            battery_12v_voltage=battery_12v_voltage,
            battery_12v_level=battery_12v_level,
            fragrance_active=fragrance_active,
            interior_temp=interior_temp,
            exterior_temp=exterior_temp,
            power_mode=power_mode,
        )
