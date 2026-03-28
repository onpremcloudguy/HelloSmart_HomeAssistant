"""Smart vehicle cloud API client."""

from __future__ import annotations

import json
import logging
from datetime import datetime
from typing import Any
from urllib.parse import urlparse

import aiohttp

from .auth import AuthenticationError, build_signed_headers, build_vc_signed_headers
from .const import (
    API_CHARGING_RESERVATION_PATH,
    API_CLIMATE_SCHEDULE_PATH,
    API_CODE_SUCCESS,
    API_CODE_TOKEN_EXPIRED,
    API_CODE_VEHICLE_NOT_LINKED,
    API_TELEMATICS_COMMAND_PATH,
    API_VC_ABILITY_PATH,
    EU_API_BASE_URL,
    OTA_BASE_URL,
    URL_ALLOWLIST,
    VC_EU_BASE_URL,
    VC_INTL_BASE_URL,
)
from .models import (
    Account,
    AuthState,
    ChargingReservation,
    ChargingState,
    ClimateSchedule,
    CommandResult,
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
    VehicleAbility,
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
                color_name=item.get("colorName", ""),
                color_code=item.get("colorCode", ""),
                model_code=item.get("modelCode", ""),
                factory_code=item.get("factoryCode", ""),
                vehicle_photo_small=item.get("vehiclePhotoSmall", ""),
                vehicle_photo_big=item.get("vehiclePhotoBig", ""),
                plate_no=item.get("plateNo", ""),
                engine_no=item.get("engineNo", ""),
                mat_code=item.get("matCode", ""),
                series_name=item.get("seriesName", ""),
                vehicle_type=item.get("vehicleType", ""),
                fuel_tank_capacity=item.get("fuelTankCapacity", ""),
                ihu_platform=item.get("ihuPlatform", ""),
                tbox_platform=item.get("tboxPlatform", ""),
                default_vehicle=bool(item.get("defaultVehicle", False)),
                share_status=item.get("shareStatus", ""),
                iccid=item.get("iccid", ""),
                msisdn=item.get("msisdn", ""),
                tem_id=item.get("temId", ""),
                ihu_id=item.get("ihuId", ""),
                tem_type=item.get("temType", ""),
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
        """Fetch SOC / charging target for a vehicle.

        Returns dict with 'target_soc' (int, 0-100) extracted from the API's
        soc field (which is percentage * 10, e.g. '1000' = 100%).
        """
        base_url = self._get_base_url(account)
        url = (
            f"{base_url}/remote-control/vehicle/status/soc/{vin}"
            f"?setting=charging"
        )

        data = await self._signed_request("GET", url, account)
        d = data.get("data", {})
        result: dict = {}
        if d.get("soc"):
            try:
                result["target_soc"] = int(d["soc"]) // 10
            except (ValueError, TypeError):
                pass
        # Capture all other SOC endpoint fields
        if d.get("chargeUAct"):
            try:
                result["charge_voltage"] = float(d["chargeUAct"])
            except (ValueError, TypeError):
                pass
        if d.get("chargeIAct"):
            try:
                result["charge_current"] = float(d["chargeIAct"])
            except (ValueError, TypeError):
                pass
        if d.get("timeToFullyCharged"):
            try:
                result["time_to_full"] = int(d["timeToFullyCharged"])
            except (ValueError, TypeError):
                pass
        if d.get("chargeLevel"):
            try:
                result["charge_level"] = int(d["chargeLevel"])
            except (ValueError, TypeError):
                pass
        if d.get("chargerState"):
            try:
                result["charger_state"] = int(d["chargerState"])
            except (ValueError, TypeError):
                pass
        return result

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
            engine_status=d.get("engineStatus", ""),
            usage_mode=d.get("usageMode", ""),
            car_mode=d.get("carMode", ""),
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
    ) -> ChargingReservation | None:
        """Fetch charging reservation / schedule.

        The API returns a paginated command history. When list is null or
        empty, no reservation exists. Otherwise parse the latest entry.
        """
        base_url = self._get_base_url(account)
        url = f"{base_url}/remote-control/charging/reservation/{vin}"
        data = await self._signed_request("GET", url, account)
        d = data.get("data", {})

        # Real API returns {pagination, serviceResult, list}
        entries = d.get("list")
        if not entries:
            return None

        # Parse the latest reservation entry
        latest = entries[0] if isinstance(entries, list) else None
        if not latest:
            return None

        return ChargingReservation(
            active=latest.get("reservationStatus") == "active",
            start_time=latest.get("startTime", ""),
            end_time=latest.get("endTime", ""),
            target_soc=int(latest["targetSoc"]) if latest.get("targetSoc") else None,
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
            schedule_id=s.get("scheduleId", ""),
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
            movement_alert_enabled=bool(d.get("movementAlertEnabled", False)),
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
    ) -> tuple[TripJournal | None, int | None]:
        """Fetch most recent trip from journal.

        Returns a tuple of (trip, total_trips).
        """
        base_url = self._get_base_url(account)
        url = f"{base_url}/geelyTCAccess/tcservices/vehicle/status/journalLogV4/{vin}"
        data = await self._signed_request("GET", url, account)
        journal_data = data.get("data", {})
        logs = journal_data.get("journalLogs", [])
        total_trips = None
        if journal_data.get("totalTrips"):
            try:
                total_trips = int(journal_data["totalTrips"])
            except (ValueError, TypeError):
                pass
        if not logs:
            return None, total_trips
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
        trip = TripJournal(
            trip_id=t.get("tripId", ""),
            distance=float(t["distance"]) if t.get("distance") else None,
            duration=int(t["duration"]) if t.get("duration") else None,
            energy_consumption=float(t["energyConsumption"]) if t.get("energyConsumption") else None,
            avg_energy_consumption=float(t["averageEnergyConsumption"]) if t.get("averageEnergyConsumption") else None,
            avg_speed=float(t["averageSpeed"]) if t.get("averageSpeed") else None,
            max_speed=float(t["maxSpeed"]) if t.get("maxSpeed") else None,
            start_time=start_time,
            end_time=end_time,
            regenerated_energy=float(t["regeneratedEnergy"]) if t.get("regeneratedEnergy") else None,
            start_address=t.get("startAddress", ""),
            end_address=t.get("endAddress", ""),
        )
        return trip, total_trips

    async def async_get_total_distance(
        self, account: Account, vin: str
    ) -> tuple[float | None, datetime | None]:
        """Fetch total distance from TC endpoint.

        Returns a tuple of (distance, update_time).
        """
        base_url = self._get_base_url(account)
        url = f"{base_url}/geelyTCAccess/tcservices/vehicle/status/getTotalDistanceByLabel/{vin}"
        data = await self._signed_request("GET", url, account)
        d = data.get("data", {})
        distance = None
        update_time = None
        if d.get("totalDistance"):
            try:
                distance = float(d["totalDistance"])
            except (ValueError, TypeError):
                pass
        if d.get("updateTime"):
            try:
                update_time = datetime.fromtimestamp(int(d["updateTime"]) / 1000)
            except (ValueError, TypeError, OSError):
                pass
        return distance, update_time

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
        inner = data.get("data", {})

        # Primary format: APK model (TscVehicleCapability) with data.list[]
        cap_list = inner.get("list", [])
        if cap_list:
            _LOGGER.debug(
                "Capability response uses 'list' format (%d entries) for %s",
                len(cap_list),
                vin[:6] + "...",
            )
            capability_flags = {
                c["functionId"]: c.get("valueEnable", False)
                for c in cap_list
                if c.get("functionId")
            }

            # The API may return v2 capability IDs (with _2 suffix or
            # renamed keys) while the APK FunctionId constants use v1
            # names.  Propagate v2 values to their v1 aliases so entity
            # filtering works regardless of API version.
            _V2_TO_V1: dict[str, list[str]] = {
                "charging_status_2": ["charging_status"],
                "remote_climate_control_2": [
                    "remote_air_condition_switch",
                    "climate_status",
                ],
                "curtain_status_2": ["curtain_status"],
                "sunroof_automatic_close": ["skylight_rolling_status"],
                "recharge_lid_status_2": ["recharge_lid_status"],
                "remote_control_lock_2": ["remote_control_lock"],
                "remote_control_unlock_2": ["remote_control_unlock"],
                "remote_control_window_2": [
                    "remote_window_close",
                    "remote_window_open",
                ],
                "remote_control_ventilate_2": ["seat_ventilation_status"],
                "tire_pressure_warning_2": ["tyre_pressure"],
            }
            for v2_key, v1_aliases in _V2_TO_V1.items():
                if v2_key in capability_flags:
                    for v1_key in v1_aliases:
                        capability_flags.setdefault(v1_key, capability_flags[v2_key])

            # IDs with no v2 equivalent in the API: assume enabled when
            # the broader feature category is present.
            # - remote_control_fragrance: enabled if fragrance warning exists
            # - remote_seat_preheat_switch: enabled if climate control exists
            # - remote_trunk_open: enabled if trunk_status exists
            _INFER: dict[str, str] = {
                "remote_control_fragrance": "fragrance_exhausted_warning_2",
                "remote_seat_preheat_switch": "remote_climate_control_2",
                "remote_trunk_open": "trunk_status",
            }
            for v1_key, indicator in _INFER.items():
                if v1_key not in capability_flags and indicator in capability_flags:
                    capability_flags[v1_key] = capability_flags[indicator]

            # Also extract service_ids if present in this format
            service_ids = [
                c.get("serviceId", "")
                for c in cap_list
                if c.get("serviceId") and c.get("enabled")
            ]
            return VehicleCapabilities(
                service_ids=service_ids,
                capability_flags=capability_flags,
            )

        # Fallback: legacy format with data.capabilities[]
        caps = inner.get("capabilities", [])
        if caps:
            _LOGGER.debug(
                "Capability response uses 'capabilities' format (%d entries) for %s",
                len(caps),
                vin[:6] + "...",
            )
            service_ids = [c.get("serviceId", "") for c in caps if c.get("enabled")]
            return VehicleCapabilities(service_ids=service_ids)

        _LOGGER.debug("Capability response empty for %s", vin[:6] + "...")
        return VehicleCapabilities()

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

    async def async_send_command(
        self, account: Account, vin: str, payload: dict
    ) -> CommandResult:
        """Send a vehicle command via PUT to the telematics endpoint.

        The JSON body is serialized with no spaces per API contract C-001.
        The response has success/message at the top level of the envelope.
        """
        base_url = self._get_base_url(account)
        url = f"{base_url}{API_TELEMATICS_COMMAND_PATH}/{vin}"
        self._validate_url(url)

        body_str = json.dumps(payload, separators=(",", ":"))
        headers = build_signed_headers("PUT", url, body_str, account)

        service_id = payload.get("serviceId", "")
        now = datetime.now()

        async with self._session.put(url, headers=headers, data=body_str) as resp:
            if resp.status == 401:
                raise TokenExpiredError("HTTP 401 Unauthorized")
            if resp.status == 429:
                retry_after = int(resp.headers.get("Retry-After", "60"))
                raise RateLimitedError(retry_after)
            resp.raise_for_status()
            data = await resp.json()

        code = data.get("code")
        if code is not None:
            try:
                code = int(code)
            except (ValueError, TypeError):
                pass
            if code == API_CODE_TOKEN_EXPIRED:
                raise TokenExpiredError("API code 1402: token expired")

        _LOGGER.debug("Command %s response: %s", service_id, data)

        # The standard API envelope has success/message at the top level:
        #   {"code": 1000, "data": {...}, "success": true, "message": "..."}
        # Check top-level first, then fall back to nested data.data
        if "success" in data:
            success = data["success"]
            error_msg = data.get("message")
        elif "data" in data and isinstance(data["data"], dict):
            success = data["data"].get("success", False)
            error_msg = data["data"].get("message")
        else:
            success = False
            error_msg = data.get("message")

        return CommandResult(
            success=bool(success),
            service_id=service_id,
            timestamp=now,
            error_message=error_msg if not success else None,
        )

    async def async_set_charging_reservation(
        self, account: Account, vin: str, data: dict
    ) -> CommandResult:
        """Update charging reservation via PUT."""
        base_url = self._get_base_url(account)
        url = f"{base_url}{API_CHARGING_RESERVATION_PATH}/{vin}"
        self._validate_url(url)

        body_str = json.dumps(data, separators=(",", ":"))
        headers = build_signed_headers("PUT", url, body_str, account)
        now = datetime.now()

        async with self._session.put(url, headers=headers, data=body_str) as resp:
            if resp.status == 401:
                raise TokenExpiredError("HTTP 401 Unauthorized")
            if resp.status == 429:
                retry_after = int(resp.headers.get("Retry-After", "60"))
                raise RateLimitedError(retry_after)
            resp.raise_for_status()
            resp_data = await resp.json()

        success = resp_data.get("success", resp_data.get("code") == API_CODE_SUCCESS)
        return CommandResult(
            success=bool(success),
            service_id="charging_reservation",
            timestamp=now,
            error_message=resp_data.get("message") if not success else None,
        )

    async def async_set_climate_schedule(
        self, account: Account, vin: str, data: dict
    ) -> CommandResult:
        """Update climate schedule via PUT."""
        base_url = self._get_base_url(account)
        url = f"{base_url}{API_CLIMATE_SCHEDULE_PATH}/{vin}"
        self._validate_url(url)

        body_str = json.dumps(data, separators=(",", ":"))
        headers = build_signed_headers("PUT", url, body_str, account)
        now = datetime.now()

        async with self._session.put(url, headers=headers, data=body_str) as resp:
            if resp.status == 401:
                raise TokenExpiredError("HTTP 401 Unauthorized")
            if resp.status == 429:
                retry_after = int(resp.headers.get("Retry-After", "60"))
                raise RateLimitedError(retry_after)
            resp.raise_for_status()
            resp_data = await resp.json()

        success = resp_data.get("success", resp_data.get("code") == API_CODE_SUCCESS)
        return CommandResult(
            success=bool(success),
            service_id="climate_schedule",
            timestamp=now,
            error_message=resp_data.get("message") if not success else None,
        )

    @staticmethod
    def _get_base_url(account: Account) -> str:
        """Get the API base URL for the account's region.

        Both EU and INTL use api.ecloudeu.com for vehicle data.
        apiv2.ecloudeu.com is only used for INTL session exchange (in auth.py).
        """
        return EU_API_BASE_URL

    @staticmethod
    def _get_vc_base_url(account: Account) -> str:
        """Get the Vehicle Services (VC) base URL for ability/image endpoints."""
        if account.region == Region.EU:
            return VC_EU_BASE_URL
        return VC_INTL_BASE_URL

    async def async_get_vehicle_ability(
        self, account: Account, vin: str, model_code: str
    ) -> VehicleAbility | None:
        """Fetch vehicle ability data including image URLs.

        Calls the vc/vehicle/v1/ability/{modelCode}/{vin} endpoint.
        For INTL: sg-app-api.smart.com uses Alibaba Cloud API Gateway HmacSHA256.
        For EU: vehicle.vbs.srv.smart.com uses api_access_token directly.
        """
        if not model_code:
            _LOGGER.debug("No model_code for %s, skipping ability fetch", vin[:6] + "...")
            return None

        vc_base = self._get_vc_base_url(account)
        url = f"{vc_base}{API_VC_ABILITY_PATH}/{model_code}/{vin}"

        _LOGGER.debug("Fetching vehicle ability: %s", url)

        self._validate_url(url)

        if account.region == Region.INTL:
            headers = build_vc_signed_headers("GET", url, account)
        else:
            # EU VC endpoint uses api_access_token
            headers = {
                "x-smart-id": account.api_user_id,
                "authorization": account.api_access_token,
                "accept": "application/json",
                "content-type": "application/json",
            }

        async with self._session.request("GET", url, headers=headers) as resp:
            if resp.status == 401:
                raise TokenExpiredError("HTTP 401 from VC ability endpoint")
            if resp.status == 429:
                retry_after = int(resp.headers.get("Retry-After", "60"))
                raise RateLimitedError(retry_after)
            if resp.status != 200:
                body = await resp.text()
                ca_error = resp.headers.get("x-ca-error-message", "")
                _LOGGER.debug(
                    "VC ability endpoint returned %d for %s: ca_error=%s body=%s",
                    resp.status, vin[:6] + "...", ca_error, body[:500],
                )
                return None
            data = await resp.json()

        code = data.get("code")
        try:
            code = int(code) if code is not None else None
        except (ValueError, TypeError):
            pass
        if code not in (API_CODE_SUCCESS, 200):
            _LOGGER.debug("VC ability API returned code %s", code)
            return None

        # VC ability uses "result" key (not "data" like other endpoints)
        result = data.get("result") or data.get("data") or {}
        vsc = result.get("vscData") or {}
        _LOGGER.debug(
            "VC ability: imagesPath=%s, model=%s, color=%s",
            vsc.get("imagesPath", "")[:80] if vsc.get("imagesPath") else "none",
            vsc.get("modelName", ""),
            vsc.get("colorNameMss", ""),
        )
        _LOGGER.debug(
            "VC ability images: top=%s, interior=%s, battery=%s",
            vsc.get("topImagesPath", "")[:80] if vsc.get("topImagesPath") else "none",
            vsc.get("interiorImagesPath", "")[:80] if vsc.get("interiorImagesPath") else "none",
            vsc.get("batteryImagesPath", "")[:80] if vsc.get("batteryImagesPath") else "none",
        )

        return VehicleAbility(
            images_path=vsc.get("imagesPath", ""),
            top_images_path=vsc.get("topImagesPath", ""),
            battery_images_path=vsc.get("batteryImagesPath", ""),
            interior_images_path=vsc.get("interiorImagesPath", ""),
            color_code=vsc.get("colorCode", ""),
            color_name_mss=vsc.get("colorNameMss", ""),
            contrast_color_code=vsc.get("contrastColorCode", ""),
            contrast_color_name=vsc.get("contrastColorNameMSS", ""),
            interior_color_name=vsc.get("interiorColorNameMss", ""),
            hub_code=vsc.get("hubCode", ""),
            hub_name=vsc.get("hubNameMSS", ""),
            model_code_mss=vsc.get("modelCodeMss", ""),
            model_code_vdp=vsc.get("modelCodeVdp", ""),
            model_name=vsc.get("modelName", ""),
            vehicle_name=vsc.get("vehicleName", ""),
            vehicle_nickname=vsc.get("vehicleNickname", ""),
            side_logo_light_name=vsc.get("sideLogoLightNameMSS", ""),
            license_plate_number=vsc.get("licensePlateNumber", ""),
        )

    async def async_download_image(
        self, url: str, dest_path: str
    ) -> bool:
        """Download an image from a URL to a local file path.

        Only downloads if the file doesn't already exist.
        Returns True if the file exists (downloaded or already present).
        """
        import asyncio
        import os

        if await asyncio.to_thread(os.path.exists, dest_path):
            return True

        if not url:
            return False

        parsed = urlparse(url)
        if parsed.scheme != "https":
            _LOGGER.debug("Refusing non-HTTPS image URL: %s", url[:60])
            return False

        self._validate_url(url)

        try:
            async with self._session.get(
                url,
                timeout=aiohttp.ClientTimeout(total=30),
            ) as resp:
                if resp.status != 200:
                    _LOGGER.debug("Image download failed: HTTP %d from %s", resp.status, url[:60])
                    return False

                content_type = resp.headers.get("Content-Type", "")
                if not content_type.startswith(("image/", "application/octet-stream")):
                    _LOGGER.debug("Unexpected content-type for image: %s", content_type)
                    return False

                content = await resp.read()

                # Size guard: reject files > 10 MB
                if len(content) > 10 * 1024 * 1024:
                    _LOGGER.warning("Image too large (%d bytes), skipping", len(content))
                    return False

                def _write_file() -> None:
                    os.makedirs(os.path.dirname(dest_path), exist_ok=True)
                    with open(dest_path, "wb") as f:
                        f.write(content)

                await asyncio.to_thread(_write_file)

            _LOGGER.debug("Downloaded vehicle image to %s", dest_path)
            return True
        except Exception:
            _LOGGER.debug("Failed to download image from %s", url[:60], exc_info=True)
            return False

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
        charger_connected = str(ev.get("statusOfChargerConnection", "0")) in ("1", "2", "3")

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
        altitude = None
        if gps_data:
            try:
                lat = float(gps_data.get("latitude", 0))
                lon = float(gps_data.get("longitude", 0))
                if -90 <= lat <= 90 and -180 <= lon <= 180 and (lat != 0 or lon != 0):
                    latitude = lat
                    longitude = lon
            except (ValueError, TypeError):
                pass
            try:
                alt_raw = gps_data.get("altitude")
                if alt_raw is not None:
                    altitude = float(alt_raw)
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

        washer_val = _safe_int(maintenance_raw.get("washerFluidLevelStatus"))
        if washer_val is None or washer_val == 7:
            washer_fluid_low = None
        else:
            washer_fluid_low = washer_val in (1, 2)

        brake_val = _safe_int(maintenance_raw.get("brakeFluidLevelStatus"))
        if brake_val is None or brake_val == 7:
            brake_fluid_ok = None
        else:
            brake_fluid_ok = brake_val not in (1, 2)

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

        # ── Running status (lights, trip meters, speed) ─────────────────
        trip_meter_1 = _safe_float(running_status.get("tripMeter1"))
        trip_meter_2 = _safe_float(running_status.get("tripMeter2"))
        avg_speed = _safe_float(running_status.get("avgSpeed"))
        engine_coolant_level = _safe_int(running_status.get("engineCoolantLevelStatus"))

        # Light status booleans (0=off, non-zero=on)
        light_low_beam = _safe_bool(running_status.get("loBeam"))
        light_high_beam = _safe_bool(running_status.get("hiBeam"))
        light_drl = _safe_bool(running_status.get("drl"))
        light_front_fog = _safe_bool(running_status.get("frntFog"))
        light_rear_fog = _safe_bool(running_status.get("reFog"))
        light_position_front = _safe_bool(running_status.get("posLiFrnt"))
        light_position_rear = _safe_bool(running_status.get("posLiRe"))
        light_turn_left = _safe_bool(running_status.get("trunIndrLe"))
        light_turn_right = _safe_bool(running_status.get("trunIndrRi"))
        light_reverse = _safe_bool(running_status.get("reverseLi"))
        light_stop = _safe_bool(running_status.get("stopLi"))
        light_hazard = _safe_bool(running_status.get("dbl"))
        light_ahbc = _safe_bool(running_status.get("ahbc"))
        light_afs = _safe_bool(running_status.get("afs"))
        light_ahl = _safe_bool(running_status.get("ahl"))
        light_highway = _safe_bool(running_status.get("hwl"))
        light_corner = _safe_bool(running_status.get("cornrgLi"))
        light_welcome = _safe_bool(running_status.get("welcome"))
        light_goodbye = _safe_bool(running_status.get("goodbye"))
        light_home_safe = _safe_bool(running_status.get("homeSafe"))
        light_approach = _safe_bool(running_status.get("approach"))
        light_show = _safe_bool(running_status.get("ltgShow"))
        light_all_weather = _safe_bool(running_status.get("allwl"))
        light_flash = _safe_bool(running_status.get("flash"))

        # ── Climate detailed ────────────────────────────────────────────
        # Position value 101 is a sentinel meaning "not equipped".
        # Normalise to None so entities show as unavailable.
        _NOT_EQUIPPED = 101

        window_position_driver = _safe_int(climate_raw.get("winPosDriver"))
        if window_position_driver == _NOT_EQUIPPED:
            window_position_driver = None
        window_position_passenger = _safe_int(climate_raw.get("winPosPassenger"))
        if window_position_passenger == _NOT_EQUIPPED:
            window_position_passenger = None
        window_position_driver_rear = _safe_int(
            climate_raw.get("winPosDriverRear")
        )
        if window_position_driver_rear == _NOT_EQUIPPED:
            window_position_driver_rear = None
        window_position_passenger_rear = _safe_int(
            climate_raw.get("winPosPassengerRear")
        )
        if window_position_passenger_rear == _NOT_EQUIPPED:
            window_position_passenger_rear = None

        sunroof_position = _safe_int(climate_raw.get("sunroofPos"))
        if sunroof_position == _NOT_EQUIPPED:
            sunroof_position = None
            sunroof_open = None
        else:
            sunroof_open = _safe_bool(climate_raw.get("sunroofOpenStatus"))

        sun_curtain_rear_position = _safe_int(climate_raw.get("sunCurtainRearPos"))
        if sun_curtain_rear_position == _NOT_EQUIPPED:
            sun_curtain_rear_position = None
            sun_curtain_rear_open = None
        else:
            sun_curtain_rear_open = _safe_bool(
                climate_raw.get("sunCurtainRearOpenStatus")
            )

        curtain_position = _safe_int(climate_raw.get("curtainPos"))
        if curtain_position == _NOT_EQUIPPED:
            curtain_position = None
            curtain_open = None
        else:
            curtain_open = _safe_bool(climate_raw.get("curtainOpenStatus"))
        driver_seat_heating = _safe_int(climate_raw.get("drvHeatSts"))
        passenger_seat_heating = _safe_int(climate_raw.get("passHeatingSts"))
        rear_left_seat_heating = _safe_int(climate_raw.get("rlHeatingSts"))
        rear_right_seat_heating = _safe_int(climate_raw.get("rrHeatingSts"))
        driver_seat_ventilation = _safe_int(climate_raw.get("drvVentSts"))
        passenger_seat_ventilation = _safe_int(climate_raw.get("passVentSts"))
        rear_left_seat_ventilation = _safe_int(climate_raw.get("rlVentSts"))
        rear_right_seat_ventilation = _safe_int(climate_raw.get("rrVentSts"))
        steering_wheel_heating = _safe_int(climate_raw.get("steerWhlHeatingSts"))
        pre_climate_active = _safe_bool(climate_raw.get("preClimateActive"))
        defrost_active = _safe_bool(climate_raw.get("defrost"))
        air_blower_active = _safe_bool(climate_raw.get("airBlowerActive"))
        climate_overheat_protection = _safe_bool(
            climate_raw.get("climateOverHeatProActive")
        )

        # ── Driving safety ──────────────────────────────────────────────
        safety_raw = additional_status.get("drivingSafetyStatus", {})
        door_lock_driver = _safe_int(safety_raw.get("doorLockStatusDriver"))
        door_lock_passenger = _safe_int(safety_raw.get("doorLockStatusPassenger"))
        door_lock_driver_rear = _safe_int(safety_raw.get("doorLockStatusDriverRear"))
        door_lock_passenger_rear = _safe_int(
            safety_raw.get("doorLockStatusPassengerRear")
        )
        central_locking = _safe_int(safety_raw.get("centralLockingStatus"))
        trunk_locked = _safe_int(safety_raw.get("trunkLockStatus"))
        trunk_open = _safe_bool(safety_raw.get("trunkOpenStatus"))
        engine_hood_open = _safe_bool(safety_raw.get("engineHoodOpenStatus"))
        electric_park_brake = _safe_bool(safety_raw.get("electricParkBrakeStatus"))
        tank_flap_open_raw = safety_raw.get("tankFlapStatus")
        tank_flap_open = (
            int(tank_flap_open_raw) == 0
            if tank_flap_open_raw is not None
            else None
        )
        srs_crash = _safe_bool(safety_raw.get("srsCrashStatus"))
        seatbelt_driver = (
            bool(safety_raw.get("seatBeltStatusDriver"))
            if safety_raw.get("seatBeltStatusDriver") is not None
            else None
        )
        seatbelt_passenger = (
            bool(safety_raw.get("seatBeltStatusPassenger"))
            if safety_raw.get("seatBeltStatusPassenger") is not None
            else None
        )
        seatbelt_rear_left = (
            bool(safety_raw.get("seatBeltStatusDriverRear"))
            if safety_raw.get("seatBeltStatusDriverRear") is not None
            else None
        )
        seatbelt_rear_right = (
            bool(safety_raw.get("seatBeltStatusPassengerRear"))
            if safety_raw.get("seatBeltStatusPassengerRear") is not None
            else None
        )
        seatbelt_rear_middle = (
            bool(safety_raw.get("seatBeltStatusMidRear"))
            if safety_raw.get("seatBeltStatusMidRear") is not None
            else None
        )

        # ── Pollution ───────────────────────────────────────────────────
        pollution_raw = additional_status.get("pollutionStatus", {})
        interior_pm25 = _safe_float(pollution_raw.get("interiorPM25"))
        interior_pm25_level = _safe_int(pollution_raw.get("interiorPM25Level"))
        exterior_pm25_level = _safe_int(pollution_raw.get("exteriorPM25Level"))
        relative_humidity = _safe_int(pollution_raw.get("relHumSts"))

        # ── EV additional ───────────────────────────────────────────────
        range_at_full_charge = _safe_float(
            ev.get("distanceToEmptyOnBattery100Soc")
        )
        average_power_consumption = _safe_float(ev.get("averPowerConsumption"))
        dc_charge_current = _safe_float(ev.get("dcChargeIAct"))
        charge_v = _safe_float(ev.get("chargeUAct"))
        charge_a = _safe_float(ev.get("chargeIAct"))
        charging_power = (
            round(charge_v * charge_a / 1000, 2)
            if charge_v is not None and charge_a is not None
            and charge_v > 0 and charge_a > 0
            else None
        )
        charge_lid_ac_raw = ev.get("chargeLidAcStatus")
        charge_lid_ac_open = (
            int(charge_lid_ac_raw) != 0
            if charge_lid_ac_raw is not None
            else None
        )
        charge_lid_dc_raw = ev.get("chargeLidDcAcStatus")
        charge_lid_dc_open = (
            int(charge_lid_dc_raw) != 0
            if charge_lid_dc_raw is not None
            else None
        )

        # ── Maintenance additional ──────────────────────────────────────
        engine_hours_to_service = _safe_int(
            maintenance_raw.get("engineHrsToService")
        )
        service_warning = _safe_int(maintenance_raw.get("serviceWarningStatus"))
        battery_12v_soh = _safe_float(
            main_battery.get("stateOfHealth") if main_battery else None
        )

        return VehicleStatus(
            battery_level=battery_level,
            range_remaining=range_remaining,
            charging_state=charging_state,
            charger_connected=charger_connected,
            charge_voltage=_safe_float(ev.get("chargeUAct")),
            charge_current=_safe_float(ev.get("chargeIAct")),
            time_to_full=_safe_int(ev.get("timeToFullyCharged")),
            doors=doors,
            windows=windows,
            climate_active=climate_active,
            latitude=latitude,
            longitude=longitude,
            altitude=altitude,
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
            washer_fluid_low=washer_fluid_low,
            brake_fluid_ok=brake_fluid_ok,
            battery_12v_voltage=battery_12v_voltage,
            battery_12v_level=battery_12v_level,
            fragrance_active=fragrance_active,
            interior_temp=interior_temp,
            exterior_temp=exterior_temp,
            power_mode=power_mode,
            # Running status
            trip_meter_1=trip_meter_1,
            trip_meter_2=trip_meter_2,
            average_speed=avg_speed,
            engine_coolant_level=engine_coolant_level,
            # Lights
            light_low_beam=light_low_beam,
            light_high_beam=light_high_beam,
            light_drl=light_drl,
            light_front_fog=light_front_fog,
            light_rear_fog=light_rear_fog,
            light_position_front=light_position_front,
            light_position_rear=light_position_rear,
            light_turn_left=light_turn_left,
            light_turn_right=light_turn_right,
            light_reverse=light_reverse,
            light_stop=light_stop,
            light_hazard=light_hazard,
            light_ahbc=light_ahbc,
            light_afs=light_afs,
            light_ahl=light_ahl,
            light_highway=light_highway,
            light_corner=light_corner,
            light_welcome=light_welcome,
            light_goodbye=light_goodbye,
            light_home_safe=light_home_safe,
            light_approach=light_approach,
            light_show=light_show,
            light_all_weather=light_all_weather,
            light_flash=light_flash,
            # Climate detailed
            window_position_driver=window_position_driver,
            window_position_passenger=window_position_passenger,
            window_position_driver_rear=window_position_driver_rear,
            window_position_passenger_rear=window_position_passenger_rear,
            sunroof_position=sunroof_position,
            sunroof_open=sunroof_open,
            sun_curtain_rear_position=sun_curtain_rear_position,
            sun_curtain_rear_open=sun_curtain_rear_open,
            curtain_position=curtain_position,
            curtain_open=curtain_open,
            driver_seat_heating=driver_seat_heating,
            passenger_seat_heating=passenger_seat_heating,
            rear_left_seat_heating=rear_left_seat_heating,
            rear_right_seat_heating=rear_right_seat_heating,
            driver_seat_ventilation=driver_seat_ventilation,
            passenger_seat_ventilation=passenger_seat_ventilation,
            rear_left_seat_ventilation=rear_left_seat_ventilation,
            rear_right_seat_ventilation=rear_right_seat_ventilation,
            steering_wheel_heating=steering_wheel_heating,
            pre_climate_active=pre_climate_active,
            defrost_active=defrost_active,
            air_blower_active=air_blower_active,
            climate_overheat_protection=climate_overheat_protection,
            # Driving safety
            door_lock_driver=door_lock_driver,
            door_lock_passenger=door_lock_passenger,
            door_lock_driver_rear=door_lock_driver_rear,
            door_lock_passenger_rear=door_lock_passenger_rear,
            central_locking=central_locking,
            trunk_locked=trunk_locked,
            trunk_open=trunk_open,
            engine_hood_open=engine_hood_open,
            electric_park_brake=electric_park_brake,
            tank_flap_open=tank_flap_open,
            srs_crash=srs_crash,
            seatbelt_driver=seatbelt_driver,
            seatbelt_passenger=seatbelt_passenger,
            seatbelt_rear_left=seatbelt_rear_left,
            seatbelt_rear_right=seatbelt_rear_right,
            seatbelt_rear_middle=seatbelt_rear_middle,
            # Pollution
            interior_pm25=interior_pm25,
            interior_pm25_level=interior_pm25_level,
            exterior_pm25_level=exterior_pm25_level,
            relative_humidity=relative_humidity,
            # EV additional
            range_at_full_charge=range_at_full_charge,
            average_power_consumption=average_power_consumption,
            dc_charge_current=dc_charge_current,
            charging_power=charging_power,
            charge_lid_ac_open=charge_lid_ac_open,
            charge_lid_dc_open=charge_lid_dc_open,
            # Maintenance additional
            engine_hours_to_service=engine_hours_to_service,
            service_warning=service_warning,
            battery_12v_state_of_health=battery_12v_soh,
        )
