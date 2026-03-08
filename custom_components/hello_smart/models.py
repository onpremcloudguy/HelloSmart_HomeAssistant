"""Data models for the Hello Smart integration."""

from __future__ import annotations

import enum
from dataclasses import dataclass, field
from datetime import datetime
from typing import Any


class Region(enum.StrEnum):
    """Smart API regions."""

    EU = "EU"
    INTL = "INTL"


class AuthState(enum.StrEnum):
    """Account authentication state."""

    UNAUTHENTICATED = "unauthenticated"
    AUTHENTICATED = "authenticated"
    TOKEN_EXPIRED = "token_expired"
    AUTH_FAILED = "auth_failed"


class ChargingState(enum.StrEnum):
    """Human-readable charging states mapped from API chargerState 0–15."""

    NOT_CHARGING = "not_charging"
    CHARGE_PREPARATION = "charge_preparation"
    AC_CHARGING = "ac_charging"
    DC_CHARGING = "dc_charging"
    CHARGE_PAUSED = "charge_paused"
    FULLY_CHARGED = "fully_charged"


def charging_state_from_api(value: int) -> ChargingState:
    """Map API chargerState integer (0–15) to ChargingState enum."""
    if value == 0:
        return ChargingState.NOT_CHARGING
    if 1 <= value <= 3:
        return ChargingState.CHARGE_PREPARATION
    if 4 <= value <= 6:
        return ChargingState.AC_CHARGING
    if 7 <= value <= 9:
        return ChargingState.DC_CHARGING
    if 10 <= value <= 14:
        return ChargingState.CHARGE_PAUSED
    if value == 15:
        return ChargingState.FULLY_CHARGED
    return ChargingState.NOT_CHARGING


class PowerMode(enum.StrEnum):
    """Vehicle power/ignition mode."""

    OFF = "off"
    ACCESSORY = "accessory"
    ON = "on"
    CRANKING = "cranking"


def power_mode_from_api(value: str | int) -> PowerMode:
    """Map API powerMode string to PowerMode enum."""
    _MAP = {"0": PowerMode.OFF, "1": PowerMode.ACCESSORY, "2": PowerMode.ON, "3": PowerMode.CRANKING}
    return _MAP.get(str(value), PowerMode.OFF)


@dataclass
class Account:
    """A user's Smart cloud account and authentication state."""

    username: str
    region: Region
    device_id: str = ""
    access_token: str = ""
    refresh_token: str = ""
    api_access_token: str = ""
    api_refresh_token: str = ""
    api_user_id: str = ""
    api_client_id: str = ""  # INTL only
    expires_at: datetime | None = None
    state: AuthState = AuthState.UNAUTHENTICATED

    @property
    def is_token_valid(self) -> bool:
        """Check if the API token is present and not expired."""
        if not self.api_access_token or self.state != AuthState.AUTHENTICATED:
            return False
        if self.expires_at is None:
            return True
        return datetime.now() < self.expires_at


@dataclass
class Vehicle:
    """A single Smart vehicle linked to an account."""

    vin: str
    model_name: str = ""
    model_year: str = ""
    series_code: str = ""
    base_url: str = ""


@dataclass
class VehicleStatus:
    """Point-in-time snapshot of a vehicle's state."""

    battery_level: int = 0
    range_remaining: float = 0.0
    charging_state: ChargingState = ChargingState.NOT_CHARGING
    charger_connected: bool = False
    charge_voltage: float | None = None
    charge_current: float | None = None
    time_to_full: int | None = None
    doors: dict[str, bool] = field(default_factory=dict)
    windows: dict[str, bool] = field(default_factory=dict)
    climate_active: bool = False
    latitude: float | None = None
    longitude: float | None = None
    last_updated: datetime | None = None
    # Tyre data (from maintenanceStatus)
    tyre_pressure_fl: float | None = None
    tyre_pressure_fr: float | None = None
    tyre_pressure_rl: float | None = None
    tyre_pressure_rr: float | None = None
    tyre_temp_fl: float | None = None
    tyre_temp_fr: float | None = None
    tyre_temp_rl: float | None = None
    tyre_temp_rr: float | None = None
    tyre_warning_fl: bool | None = None
    tyre_warning_fr: bool | None = None
    tyre_warning_rl: bool | None = None
    tyre_warning_rr: bool | None = None
    # Maintenance data
    odometer: float | None = None
    days_to_service: int | None = None
    distance_to_service: float | None = None
    washer_fluid_level: int | None = None
    brake_fluid_ok: bool | None = None
    # 12V battery
    battery_12v_voltage: float | None = None
    battery_12v_level: float | None = None
    # Climate extras
    fragrance_active: bool | None = None
    interior_temp: float | None = None
    exterior_temp: float | None = None
    # Vehicle state
    power_mode: PowerMode | None = None


@dataclass
class OTAInfo:
    """Firmware update state for a vehicle."""

    current_version: str = ""
    target_version: str = ""

    @property
    def update_available(self) -> bool:
        """True if target version differs from current version."""
        return bool(
            self.target_version
            and self.current_version
            and self.target_version != self.current_version
        )


@dataclass
class TelematicsStatus:
    """Telematics unit connectivity and metadata."""

    connected: bool | None = None
    sw_version: str = ""
    hw_version: str = ""
    imei: str = ""
    power_mode: PowerMode | None = None
    backup_battery_voltage: float | None = None
    backup_battery_level: float | None = None


@dataclass
class VehicleRunningState:
    """Condensed vehicle running state."""

    power_mode: PowerMode = PowerMode.OFF
    speed: float = 0.0


@dataclass
class TripJournal:
    """Most recent trip data."""

    trip_id: str = ""
    distance: float | None = None
    duration: int | None = None
    energy_consumption: float | None = None
    avg_energy_consumption: float | None = None
    avg_speed: float | None = None
    max_speed: float | None = None
    start_time: datetime | None = None
    end_time: datetime | None = None


@dataclass
class ChargingReservation:
    """Charging schedule / reservation."""

    active: bool = False
    start_time: str = ""
    end_time: str = ""
    target_soc: int | None = None


@dataclass
class ClimateSchedule:
    """Climate pre-conditioning schedule."""

    enabled: bool = False
    scheduled_time: str = ""
    temperature: float | None = None
    duration: int | None = None


@dataclass
class FridgeStatus:
    """Mini-fridge status."""

    active: bool = False
    temperature: float | None = None
    mode: str = ""


@dataclass
class LockerStatus:
    """Front trunk / storage locker status."""

    open: bool | None = None
    locked: bool | None = None


@dataclass
class VtmSettings:
    """Vehicle theft monitoring settings."""

    enabled: bool = False
    notification_enabled: bool = False
    geofence_alert_enabled: bool = False


@dataclass
class FragranceDetails:
    """Extended fragrance system status."""

    active: bool = False
    level: str = ""
    fragrance_type: str = ""


@dataclass
class GeofenceInfo:
    """Geofence summary."""

    count: int = 0
    geofences: list[dict[str, Any]] = field(default_factory=list)


@dataclass
class VehicleCapabilities:
    """Feature capability flags for dynamic entity registration."""

    service_ids: list[str] = field(default_factory=list)


@dataclass
class DiagnosticEntry:
    """Most recent diagnostic result."""

    dtc_code: str = ""
    severity: str = ""
    timestamp: datetime | None = None
    status: str = ""


@dataclass
class LockerSecret:
    """Locker PIN configuration status."""

    has_secret: bool = False
    secret_set: bool = False


@dataclass
class FOTANotification:
    """FOTA (firmware-over-the-air) notification status."""

    has_notification: bool = False
    pending_count: int = 0


@dataclass
class EnergyRanking:
    """Energy consumption ranking among same model."""

    my_ranking: int | None = None
    my_value: float | None = None
    total_participants: int | None = None


@dataclass
class VehicleData:
    """Combined vehicle data returned by the coordinator."""

    vehicle: Vehicle
    status: VehicleStatus = field(default_factory=VehicleStatus)
    ota: OTAInfo = field(default_factory=OTAInfo)
    telematics: TelematicsStatus | None = None
    running_state: VehicleRunningState | None = None
    last_trip: TripJournal | None = None
    charging_reservation: ChargingReservation | None = None
    climate_schedule: ClimateSchedule | None = None
    fridge: FridgeStatus | None = None
    locker: LockerStatus | None = None
    vtm: VtmSettings | None = None
    fragrance: FragranceDetails | None = None
    geofence: GeofenceInfo | None = None
    capabilities: VehicleCapabilities | None = None
    diagnostic: DiagnosticEntry | None = None
    energy_ranking: EnergyRanking | None = None
    total_distance: float | None = None
    locker_secret: LockerSecret | None = None
    fota_notification: FOTANotification | None = None
