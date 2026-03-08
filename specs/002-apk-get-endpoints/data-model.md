# Data Model: APK GET Endpoint Extraction & Integration

**Branch**: `002-apk-get-endpoints` | **Date**: 2026-03-08

## Overview

All new dataclasses are added to the existing `models.py`. No new files. Models follow the established frozen/non-frozen conventions:
- `Vehicle` (mutable) — extended with new fields
- `VehicleStatus` (mutable) — extended with tyre/maintenance fields from existing response
- New data containers — mutable `@dataclass` with defaults (matches `VehicleStatus` pattern)
- `VehicleData` (mutable) — extended with new optional fields

## Enums

### PowerMode
```python
class PowerMode(enum.StrEnum):
    """Vehicle power/ignition mode."""
    OFF = "off"               # API value "0"
    ACCESSORY = "accessory"   # API value "1"
    ON = "on"                 # API value "2"
    CRANKING = "cranking"     # API value "3"
```

**Mapping function**:
```python
def power_mode_from_api(value: str | int) -> PowerMode:
    _MAP = {"0": PowerMode.OFF, "1": PowerMode.ACCESSORY, "2": PowerMode.ON, "3": PowerMode.CRANKING}
    return _MAP.get(str(value), PowerMode.OFF)
```

---

## Extended Existing Dataclasses

### Vehicle (existing — add fields)

| Field | Type | Default | Source |
|-------|------|---------|--------|
| `vin` | `str` | (existing) | Vehicle list API |
| `model_name` | `str` | `""` | (existing) |
| `model_year` | `str` | `""` | (existing) |
| `series_code` | `str` | `""` | (existing) |
| `base_url` | `str` | `""` | (existing) |

No new fields needed on `Vehicle`. All additional metadata comes from endpoint responses.

### VehicleStatus (existing — add fields)

| New Field | Type | Default | Source |
|-----------|------|---------|--------|
| `tyre_pressure_fl` | `float | None` | `None` | `maintenanceStatus.tyreStatusDriver` (kPa) |
| `tyre_pressure_fr` | `float | None` | `None` | `maintenanceStatus.tyreStatusPassenger` (kPa) |
| `tyre_pressure_rl` | `float | None` | `None` | `maintenanceStatus.tyreStatusDriverRear` (kPa) |
| `tyre_pressure_rr` | `float | None` | `None` | `maintenanceStatus.tyreStatusPassengerRear` (kPa) |
| `tyre_temp_fl` | `float | None` | `None` | `maintenanceStatus.tyreTempDriver` (°C) |
| `tyre_temp_fr` | `float | None` | `None` | `maintenanceStatus.tyreTempPassenger` (°C) |
| `tyre_temp_rl` | `float | None` | `None` | `maintenanceStatus.tyreTempDriverRear` (°C) |
| `tyre_temp_rr` | `float | None` | `None` | `maintenanceStatus.tyreTempPassengerRear` (°C) |
| `tyre_warning_fl` | `bool | None` | `None` | `maintenanceStatus.tyrePreWarningDriver` |
| `tyre_warning_fr` | `bool | None` | `None` | `maintenanceStatus.tyrePreWarningPassenger` |
| `tyre_warning_rl` | `bool | None` | `None` | `maintenanceStatus.tyrePreWarningDriverRear` |
| `tyre_warning_rr` | `bool | None` | `None` | `maintenanceStatus.tyrePreWarningPassengerRear` |
| `odometer` | `float | None` | `None` | `maintenanceStatus.odometer` (km) |
| `days_to_service` | `int | None` | `None` | `maintenanceStatus.daysToService` |
| `distance_to_service` | `float | None` | `None` | `maintenanceStatus.distanceToService` (km) |
| `washer_fluid_level` | `int | None` | `None` | `maintenanceStatus.washerFluidLevelStatus` |
| `brake_fluid_ok` | `bool | None` | `None` | `maintenanceStatus.brakeFluidLevelStatus` |
| `battery_12v_voltage` | `float | None` | `None` | `maintenanceStatus.mainBatteryStatus.voltage` (V) |
| `battery_12v_level` | `float | None` | `None` | `maintenanceStatus.mainBatteryStatus.chargeLevel` (%) |
| `fragrance_active` | `bool | None` | `None` | `climateStatus.fragActive` |
| `power_mode` | `PowerMode | None` | `None` | `basicVehicleStatus.engineStatus` or state endpoint |
| `interior_temp` | `float | None` | `None` | `climateStatus.interiorTemp` (°C) |
| `exterior_temp` | `float | None` | `None` | `climateStatus.exteriorTemp` (°C) |

**Note**: All new fields use `None` default to support dynamic entity visibility — entities with `None` values are not registered.

---

## New Dataclasses

### TelematicsStatus
```python
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
```

**Source endpoint**: `/remote-control/vehicle/telematics/{vin}`

### VehicleRunningState
```python
@dataclass
class VehicleRunningState:
    """Condensed vehicle running state."""
    power_mode: PowerMode = PowerMode.OFF
    speed: float = 0.0
```

**Source endpoint**: `/remote-control/vehicle/status/state/{vin}`

### TripJournal
```python
@dataclass
class TripJournal:
    """Most recent trip data."""
    trip_id: str = ""
    distance: float | None = None        # km
    duration: int | None = None           # seconds
    energy_consumption: float | None = None  # kWh
    avg_energy_consumption: float | None = None  # kWh/100km
    avg_speed: float | None = None        # km/h
    max_speed: float | None = None        # km/h
    start_time: datetime | None = None
    end_time: datetime | None = None
```

**Source endpoints**: `/remote-control/vehicle/status/journalLog/{vin}` or `/geelyTCAccess/tcservices/vehicle/status/journalLogV4/{vin}`

### ChargingReservation
```python
@dataclass
class ChargingReservation:
    """Charging schedule / reservation."""
    active: bool = False
    start_time: str = ""                  # "HH:mm"
    end_time: str = ""                    # "HH:mm"
    target_soc: int | None = None         # percent
```

**Source endpoint**: `/remote-control/charging/reservation/{vin}`

### ClimateSchedule
```python
@dataclass
class ClimateSchedule:
    """Climate pre-conditioning schedule."""
    enabled: bool = False
    scheduled_time: str = ""              # "HH:mm"
    temperature: float | None = None      # °C
    duration: int | None = None           # seconds
```

**Source endpoint**: `/remote-control/schedule/{vin}`

### FridgeStatus
```python
@dataclass
class FridgeStatus:
    """Mini-fridge status (Smart #1 with premium package)."""
    active: bool = False
    temperature: float | None = None      # °C
    mode: str = ""                        # "cooling" | "warming" | "off"
```

**Source endpoint**: `/remote-control/getFridge/status/{vin}`

### LockerStatus
```python
@dataclass
class LockerStatus:
    """Front trunk / storage locker status."""
    open: bool | None = None
    locked: bool | None = None
```

**Source endpoint**: `/remote-control/getLocker/status/{vin}`

### VtmSettings
```python
@dataclass
class VtmSettings:
    """Vehicle theft monitoring settings."""
    enabled: bool = False
    notification_enabled: bool = False
    geofence_alert_enabled: bool = False
```

**Source endpoint**: `/remote-control/getVtmSettingStatus`

### FragranceDetails
```python
@dataclass
class FragranceDetails:
    """Extended fragrance system status."""
    active: bool = False
    level: str = ""                       # "high" | "medium" | "low" | "empty"
    fragrance_type: str = ""
```

**Source endpoint**: `/remote-control/vehicle/fragrance/{vin}`

### GeofenceInfo
```python
@dataclass
class GeofenceInfo:
    """Geofence summary."""
    count: int = 0
    geofences: list[dict[str, Any]] = field(default_factory=list)
```

**Source endpoint**: `/geelyTCAccess/tcservices/vehicle/geofence/all/{vin}`

### VehicleCapabilities
```python
@dataclass
class VehicleCapabilities:
    """Feature capability flags for dynamic entity registration."""
    service_ids: list[str] = field(default_factory=list)
```

**Source endpoint**: `/geelyTCAccess/tcservices/capability/{vin}`

### DiagnosticEntry
```python
@dataclass
class DiagnosticEntry:
    """Most recent diagnostic result."""
    dtc_code: str = ""
    severity: str = ""
    timestamp: datetime | None = None
    status: str = ""                      # "active" | "resolved"
```

**Source endpoint**: `/remote-control/vehicle/status/history/diagnostic/{vin}`

### EnergyRanking
```python
@dataclass
class EnergyRanking:
    """Energy consumption ranking among same model."""
    my_ranking: int | None = None
    my_value: float | None = None         # kWh/100km
    total_participants: int | None = None
```

**Source endpoint**: `/geelyTCAccess/tcservices/vehicle/status/ranking/aveEnergyConsumption/...`

---

## Extended VehicleData

```python
@dataclass
class VehicleData:
    """Combined vehicle data returned by the coordinator."""
    vehicle: Vehicle
    status: VehicleStatus = field(default_factory=VehicleStatus)
    ota: OTAInfo = field(default_factory=OTAInfo)
    # New optional data sources (None = endpoint not called or failed)
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
    total_distance: float | None = None   # km (from getTotalDistanceByLabel)
```

---

## Entity-to-Field Mapping

### New Sensors (~25 entities per vehicle, shown when data is non-None)

| Entity Key | Device Class | Unit | Source Field |
|------------|-------------|------|-------------|
| `tyre_pressure_fl` | PRESSURE | kPa | `status.tyre_pressure_fl` |
| `tyre_pressure_fr` | PRESSURE | kPa | `status.tyre_pressure_fr` |
| `tyre_pressure_rl` | PRESSURE | kPa | `status.tyre_pressure_rl` |
| `tyre_pressure_rr` | PRESSURE | kPa | `status.tyre_pressure_rr` |
| `tyre_temp_fl` | TEMPERATURE | °C | `status.tyre_temp_fl` |
| `tyre_temp_fr` | TEMPERATURE | °C | `status.tyre_temp_fr` |
| `tyre_temp_rl` | TEMPERATURE | °C | `status.tyre_temp_rl` |
| `tyre_temp_rr` | TEMPERATURE | °C | `status.tyre_temp_rr` |
| `odometer` | DISTANCE | km | `status.odometer` or `total_distance` |
| `days_to_service` | DURATION | d | `status.days_to_service` |
| `distance_to_service` | DISTANCE | km | `status.distance_to_service` |
| `battery_12v_voltage` | VOLTAGE | V | `status.battery_12v_voltage` |
| `battery_12v_level` | BATTERY | % | `status.battery_12v_level` |
| `interior_temp` | TEMPERATURE | °C | `status.interior_temp` |
| `exterior_temp` | TEMPERATURE | °C | `status.exterior_temp` |
| `power_mode` | ENUM | — | `status.power_mode` or `running_state.power_mode` |
| `speed` | SPEED | km/h | `running_state.speed` |
| `last_trip_distance` | DISTANCE | km | `last_trip.distance` |
| `last_trip_duration` | DURATION | s | `last_trip.duration` |
| `last_trip_energy` | ENERGY | kWh | `last_trip.energy_consumption` |
| `charging_schedule_start` | TIMESTAMP | — | `charging_reservation.start_time` |
| `charging_schedule_status` | ENUM | — | `charging_reservation.active` |
| `climate_schedule_time` | TIMESTAMP | — | `climate_schedule.scheduled_time` |
| `geofence_count` | — | — | `geofence.count` |
| `energy_ranking` | — | — | `energy_ranking.my_ranking` |

### New Binary Sensors (~10 entities per vehicle, shown when data is non-None)

| Entity Key | Device Class | Source Field |
|------------|-------------|-------------|
| `tyre_warning_fl` | PROBLEM | `status.tyre_warning_fl` |
| `tyre_warning_fr` | PROBLEM | `status.tyre_warning_fr` |
| `tyre_warning_rl` | PROBLEM | `status.tyre_warning_rl` |
| `tyre_warning_rr` | PROBLEM | `status.tyre_warning_rr` |
| `telematics_connected` | CONNECTIVITY | `telematics.connected` |
| `fridge_active` | RUNNING | `fridge.active` |
| `fragrance_active` | — | `status.fragrance_active` or `fragrance.active` |
| `locker_open` | OPENING | `locker.open` |
| `vtm_enabled` | — | `vtm.enabled` |
| `brake_fluid_ok` | PROBLEM | `status.brake_fluid_ok` (inverted) |

---

## Relationships

```
Account 1──* Vehicle
Vehicle 1──1 VehicleStatus (extended with tyre/maintenance)
Vehicle 1──1 OTAInfo (existing)
Vehicle 1──1? TelematicsStatus
Vehicle 1──1? VehicleRunningState
Vehicle 1──1? TripJournal
Vehicle 1──1? ChargingReservation
Vehicle 1──1? ClimateSchedule
Vehicle 1──1? FridgeStatus
Vehicle 1──1? LockerStatus
Vehicle 1──1? VtmSettings
Vehicle 1──1? FragranceDetails
Vehicle 1──1? GeofenceInfo
Vehicle 1──1? VehicleCapabilities
Vehicle 1──1? DiagnosticEntry
Vehicle 1──1? EnergyRanking
```

`?` = Optional — `None` when endpoint unavailable or returns error.
