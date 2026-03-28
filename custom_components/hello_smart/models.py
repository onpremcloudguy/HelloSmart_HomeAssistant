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


class VehicleModel(enum.StrEnum):
    """Smart vehicle model derived from matCode[0:3] or seriesCodeVs.

    From APK VehicleModel.java and VehicleInfoConstants.java:
      HX1 / HX11 = Smart #1
      HC1 / HC11 = Smart #3
      HY1 / HY11 = Smart #5
    """

    HASHTAG_ONE = "#1"
    HASHTAG_THREE = "#3"
    HASHTAG_FIVE = "#5"
    UNKNOWN = "Unknown"

    @staticmethod
    def from_codes(mat_code: str, series_code: str = "") -> VehicleModel:
        """Derive model from matCode[0:3] or seriesCodeVs."""
        _PREFIX_MAP = {
            "HX1": VehicleModel.HASHTAG_ONE,
            "HC1": VehicleModel.HASHTAG_THREE,
            "HY1": VehicleModel.HASHTAG_FIVE,
        }
        if len(mat_code) >= 3:
            model = _PREFIX_MAP.get(mat_code[:3])
            if model:
                return model
        _SERIES_MAP = {
            "HX11": VehicleModel.HASHTAG_ONE,
            "HC11": VehicleModel.HASHTAG_THREE,
            "HY11": VehicleModel.HASHTAG_FIVE,
        }
        # Strip regional suffix (e.g. "HC11_IL" → "HC11")
        base = series_code.split("_")[0] if series_code else ""
        return _SERIES_MAP.get(base, VehicleModel.UNKNOWN)


class VehicleEdition(enum.StrEnum):
    """Vehicle trim / edition derived from matCode[5:7].

    Feature availability per edition (from APK VehicleEdition.java):
      - PURE:    no driver seat heating, no PM2.5 sensor
      - PRO:     no PM2.5 sensor
      - PULSE:   all features
      - PREMIUM: all features
      - BRABUS:  all features (top of range)
      - LAUNCH:  all features
      - UNKNOWN: treat as fully equipped (no filtering)

    Applies identically across all models (#1, #3, #5).
    """

    PURE = "Pure"
    PRO = "Pro"
    PULSE = "Pulse"
    PREMIUM = "Premium"
    BRABUS = "BRABUS"
    LAUNCH = "Launch Edition"
    UNKNOWN = "Unknown"

    @property
    def has_driver_seat_heating(self) -> bool:
        """Pure trim lacks driver seat heating."""
        return self != VehicleEdition.PURE

    @property
    def has_pm25(self) -> bool:
        """Pure and Pro trims lack PM2.5 air quality sensor."""
        return self not in (VehicleEdition.PURE, VehicleEdition.PRO)

    @staticmethod
    def from_mat_code(mat_code: str) -> VehicleEdition:
        """Extract edition from matCode positions [5:7]."""
        if len(mat_code) < 7:
            return VehicleEdition.UNKNOWN
        code = mat_code[5:7]
        _MAP = {
            "D3": VehicleEdition.BRABUS,
            "D2": VehicleEdition.PREMIUM,
            "D1": VehicleEdition.PRO,
            "GN": VehicleEdition.PULSE,
            "80": VehicleEdition.PURE,
            "01": VehicleEdition.LAUNCH,
        }
        return _MAP.get(code, VehicleEdition.UNKNOWN)


class ChargingState(enum.StrEnum):
    """Human-readable charging states mapped from API chargerState codes."""

    NOT_CHARGING = "not_charging"
    AC_CHARGING = "ac_charging"
    DC_CHARGING = "dc_charging"
    SUPER_CHARGING = "super_charging"
    PLUGGED_NOT_CHARGING = "plugged_not_charging"
    BOOST_CHARGING = "boost_charging"
    WIRELESS_CHARGING = "wireless_charging"


def charging_state_from_api(value: int) -> ChargingState:
    """Map API chargerState integer to ChargingState enum.

    Values confirmed from APK TspEdgeRepository.ChargerState enum:
      0  = not charging
      2  = AC charging
      15 = DC charging
      24 = super charging (DC fast)
      25 = plugged but not charging
      28 = boost charging
      30 = wireless charging
    """
    _MAP = {
        0: ChargingState.NOT_CHARGING,
        2: ChargingState.AC_CHARGING,
        15: ChargingState.DC_CHARGING,
        24: ChargingState.SUPER_CHARGING,
        25: ChargingState.PLUGGED_NOT_CHARGING,
        28: ChargingState.BOOST_CHARGING,
        30: ChargingState.WIRELESS_CHARGING,
    }
    return _MAP.get(value, ChargingState.NOT_CHARGING)


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
    id_token: str = ""  # INTL only — Xs-Auth-Token for VC endpoints
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
    # Extended fields from list-vehicles API
    color_name: str = ""
    color_code: str = ""
    model_code: str = ""
    factory_code: str = ""
    vehicle_photo_small: str = ""
    vehicle_photo_big: str = ""
    plate_no: str = ""
    engine_no: str = ""
    mat_code: str = ""
    series_name: str = ""
    vehicle_type: str = ""
    fuel_tank_capacity: str = ""
    ihu_platform: str = ""
    tbox_platform: str = ""
    default_vehicle: bool = False
    share_status: str = ""
    iccid: str = ""
    msisdn: str = ""
    tem_id: str = ""
    ihu_id: str = ""
    tem_type: str = ""

    @property
    def edition(self) -> VehicleEdition:
        """Derive the vehicle edition/trim from matCode."""
        return VehicleEdition.from_mat_code(self.mat_code)

    @property
    def smart_model(self) -> VehicleModel:
        """Derive the Smart model (#1/#3/#5) from matCode or seriesCode."""
        return VehicleModel.from_codes(self.mat_code, self.series_code)


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
    washer_fluid_low: bool | None = None
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

    # ── Running status ──────────────────────────────────────────────────
    trip_meter_1: float | None = None
    trip_meter_2: float | None = None
    average_speed: float | None = None
    engine_coolant_level: int | None = None

    # ── Light status (from runningStatus) ───────────────────────────────
    light_low_beam: bool | None = None
    light_high_beam: bool | None = None
    light_drl: bool | None = None
    light_front_fog: bool | None = None
    light_rear_fog: bool | None = None
    light_position_front: bool | None = None
    light_position_rear: bool | None = None
    light_turn_left: bool | None = None
    light_turn_right: bool | None = None
    light_reverse: bool | None = None
    light_stop: bool | None = None
    light_hazard: bool | None = None
    light_ahbc: bool | None = None
    light_afs: bool | None = None
    light_ahl: bool | None = None
    light_highway: bool | None = None
    light_corner: bool | None = None
    light_welcome: bool | None = None
    light_goodbye: bool | None = None
    light_home_safe: bool | None = None
    light_approach: bool | None = None
    light_show: bool | None = None
    light_all_weather: bool | None = None
    light_flash: bool | None = None

    # ── Climate detailed ────────────────────────────────────────────────
    window_position_driver: int | None = None
    window_position_passenger: int | None = None
    window_position_driver_rear: int | None = None
    window_position_passenger_rear: int | None = None
    sunroof_position: int | None = None
    sunroof_open: bool | None = None
    sun_curtain_rear_position: int | None = None
    sun_curtain_rear_open: bool | None = None
    curtain_position: int | None = None
    curtain_open: bool | None = None
    driver_seat_heating: int | None = None
    passenger_seat_heating: int | None = None
    rear_left_seat_heating: int | None = None
    rear_right_seat_heating: int | None = None
    driver_seat_ventilation: int | None = None
    passenger_seat_ventilation: int | None = None
    rear_left_seat_ventilation: int | None = None
    rear_right_seat_ventilation: int | None = None
    steering_wheel_heating: int | None = None
    pre_climate_active: bool | None = None
    defrost_active: bool | None = None
    air_blower_active: bool | None = None
    climate_overheat_protection: bool | None = None

    # ── Driving safety ──────────────────────────────────────────────────
    door_lock_driver: int | None = None
    door_lock_passenger: int | None = None
    door_lock_driver_rear: int | None = None
    door_lock_passenger_rear: int | None = None
    central_locking: int | None = None
    trunk_locked: int | None = None
    trunk_open: bool | None = None
    engine_hood_open: bool | None = None
    electric_park_brake: bool | None = None
    tank_flap_open: bool | None = None
    srs_crash: bool | None = None
    seatbelt_driver: bool | None = None
    seatbelt_passenger: bool | None = None
    seatbelt_rear_left: bool | None = None
    seatbelt_rear_right: bool | None = None
    seatbelt_rear_middle: bool | None = None

    # ── Pollution ───────────────────────────────────────────────────────
    interior_pm25: float | None = None
    interior_pm25_level: int | None = None
    exterior_pm25_level: int | None = None
    relative_humidity: int | None = None

    # ── GPS additional ─────────────────────────────────────────────────
    altitude: float | None = None

    # ── EV additional ───────────────────────────────────────────────────
    range_at_full_charge: float | None = None
    average_power_consumption: float | None = None
    dc_charge_current: float | None = None
    charging_power: float | None = None
    charge_lid_ac_open: bool | None = None
    charge_lid_dc_open: bool | None = None

    # ── Maintenance additional ──────────────────────────────────────────
    engine_hours_to_service: int | None = None
    service_warning: int | None = None
    battery_12v_state_of_health: float | None = None


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
    engine_status: str = ""
    usage_mode: str = ""
    car_mode: str = ""


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
    regenerated_energy: float | None = None
    start_address: str = ""
    end_address: str = ""


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

    schedule_id: str = ""
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
    movement_alert_enabled: bool = False


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
    capability_flags: dict[str, bool] = field(default_factory=dict)


@dataclass
class StaticVehicleData:
    """Cached static vehicle data fetched once per session."""

    capabilities: VehicleCapabilities | None = None
    ability: VehicleAbility | None = None
    plant_no: str = ""
    vehicle_image_path: str = ""


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
@dataclass
class VehicleAbility:
    """Vehicle ability/visual configuration from vc/vehicle/v1/ability endpoint."""

    images_path: str = ""
    top_images_path: str = ""
    battery_images_path: str = ""
    interior_images_path: str = ""
    color_code: str = ""
    color_name_mss: str = ""
    contrast_color_code: str = ""
    contrast_color_name: str = ""
    interior_color_name: str = ""
    hub_code: str = ""
    hub_name: str = ""
    model_code_mss: str = ""
    model_code_vdp: str = ""
    model_name: str = ""
    vehicle_name: str = ""
    vehicle_nickname: str = ""
    side_logo_light_name: str = ""
    license_plate_number: str = ""


@dataclass
class CommandResult:
    """Outcome of a single vehicle command."""

    success: bool
    service_id: str
    timestamp: datetime
    error_message: str | None = None


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
    total_distance_update_time: datetime | None = None
    total_trips: int | None = None
    locker_secret: LockerSecret | None = None
    fota_notification: FOTANotification | None = None
    ability: VehicleAbility | None = None
    vehicle_image_path: str = ""
    last_command_time: datetime | None = None
