# Data Models

All data models used by the Hello Smart integration.

[← Back to API Reference](README.md)

Source: [`models.py`](../custom_components/hello_smart/models.py)

---

## Enumerations

### Region

API region identifier.

| Value | Description |
|-------|-------------|
| `EU` | European region (Gigya auth) |
| `INTL` | International region (direct auth) |

### AuthState

Account authentication state.

| Value | Description |
|-------|-------------|
| `unauthenticated` | No active session |
| `authenticated` | Valid token |
| `token_expired` | Token needs refresh |
| `auth_failed` | Authentication error |

### ChargingState

Vehicle charging status, mapped from `chargerState` integer.

| Value | chargerState | Description |
|-------|-------------|-------------|
| `not_charging` | 0 | Not charging |
| `charge_preparation` | 1–3 | Preparing to charge |
| `ac_charging` | 4–6 | AC charging active |
| `dc_charging` | 7–9 | DC fast charging active |
| `charge_paused` | 10–14 | Charging paused |
| `fully_charged` | 15 | Battery fully charged |

### PowerMode

Vehicle ignition power state.

| Value | powerMode | Description |
|-------|-----------|-------------|
| `off` | `"0"` | Vehicle off |
| `accessory` | `"1"` | Accessory mode |
| `on` | `"2"` | Ignition on / ready to drive |
| `cranking` | `"3"` | Engine starting |

---

## Dataclasses

### Account

User authentication state and tokens.

| Field | Type | Description |
|-------|------|-------------|
| `username` | `str` | Account email |
| `region` | `Region` | EU or INTL |
| `auth_state` | `AuthState` | Current authentication state |
| `api_access_token` | `str \| None` | API access token |
| `api_refresh_token` | `str \| None` | API refresh token |
| `api_user_id` | `str \| None` | API user ID |
| `device_id` | `str` | Random device identifier |

### Vehicle

Vehicle identity information from [List Vehicles](endpoints/list-vehicles.md).

| Field | Type | Description |
|-------|------|-------------|
| `vin` | `str` | Vehicle Identification Number |
| `model_name` | `str` | Full model name |
| `model_year` | `str` | Model year |
| `series_code` | `str` | Series/variant code |

### VehicleStatus

Comprehensive vehicle state from [Full Vehicle Status](endpoints/vehicle-status.md) and [SOC](endpoints/soc.md).

| Field | Type | Unit | Optional |
|-------|------|------|----------|
| `battery_level` | `int` | % | Yes |
| `range_remaining` | `float` | km | Yes |
| `charging_state` | `ChargingState` | — | Yes |
| `charger_connected` | `bool` | — | Yes |
| `charge_voltage` | `float` | V | Yes |
| `charge_current` | `float` | A | Yes |
| `time_to_full` | `int` | min | Yes |
| `doors` | `dict[str, bool]` | — | Yes |
| `windows` | `dict[str, bool]` | — | Yes |
| `climate_active` | `bool` | — | Yes |
| `fragrance_active` | `bool` | — | Yes |
| `interior_temp` | `float` | °C | Yes |
| `exterior_temp` | `float` | °C | Yes |
| `latitude` | `float` | degrees | Yes |
| `longitude` | `float` | degrees | Yes |
| `tyre_pressure_fl` | `float` | kPa | Yes |
| `tyre_pressure_fr` | `float` | kPa | Yes |
| `tyre_pressure_rl` | `float` | kPa | Yes |
| `tyre_pressure_rr` | `float` | kPa | Yes |
| `tyre_temp_fl` | `float` | °C | Yes |
| `tyre_temp_fr` | `float` | °C | Yes |
| `tyre_temp_rl` | `float` | °C | Yes |
| `tyre_temp_rr` | `float` | °C | Yes |
| `tyre_warning_fl` | `bool` | — | Yes |
| `tyre_warning_fr` | `bool` | — | Yes |
| `tyre_warning_rl` | `bool` | — | Yes |
| `tyre_warning_rr` | `bool` | — | Yes |
| `odometer` | `float` | km | Yes |
| `days_to_service` | `int` | days | Yes |
| `distance_to_service` | `float` | km | Yes |
| `washer_fluid_level` | `int` | — | Yes |
| `brake_fluid_ok` | `bool` | — | Yes |
| `battery_12v_voltage` | `float` | V | Yes |
| `battery_12v_level` | `float` | % | Yes |
| `power_mode` | `PowerMode` | — | Yes |
| `last_updated` | `datetime` | — | Yes |

### OTAInfo

Firmware versions from [OTA Info](endpoints/ota-info.md).

| Field | Type | Description |
|-------|------|-------------|
| `current_version` | `str` | Installed firmware version |
| `target_version` | `str` | Available firmware version |
| `update_available` | `bool` (property) | `True` if versions differ |

### TelematicsStatus

Telematics unit from [Telematics Status](endpoints/telematics.md).

| Field | Type | Unit | Description |
|-------|------|------|-------------|
| `connected` | `bool` | — | Whether telematics is online |
| `sw_version` | `str` | — | Software version |
| `hw_version` | `str` | — | Hardware version |
| `imei` | `str` | — | IMEI number |
| `power_mode` | `PowerMode` | — | Unit power mode |
| `backup_battery_voltage` | `float \| None` | V | Backup battery voltage |
| `backup_battery_level` | `float \| None` | % | Backup battery charge |

### VehicleRunningState

Running state from [Vehicle Running State](endpoints/vehicle-state.md).

| Field | Type | Unit |
|-------|------|------|
| `power_mode` | `PowerMode` | — |
| `speed` | `float` | km/h |

### TripJournal

Last trip data from [Trip Journal](endpoints/trip-journal.md).

| Field | Type | Unit |
|-------|------|------|
| `trip_id` | `str` | — |
| `distance` | `float` | km |
| `duration` | `int` | seconds |
| `energy_consumption` | `float` | kWh |
| `avg_energy_consumption` | `float` | kWh/100km |
| `avg_speed` | `float` | km/h |
| `max_speed` | `float` | km/h |
| `start_time` | `datetime` | — |
| `end_time` | `datetime` | — |

### ChargingReservation

Charging schedule from [Charging Reservation](endpoints/charging-reservation.md).

| Field | Type | Unit |
|-------|------|------|
| `active` | `bool` | — |
| `start_time` | `str` | HH:mm |
| `end_time` | `str` | HH:mm |
| `target_soc` | `int` | % |

### ClimateSchedule

Climate schedule from [Climate Schedule](endpoints/climate-schedule.md).

| Field | Type | Unit |
|-------|------|------|
| `enabled` | `bool` | — |
| `scheduled_time` | `str` | HH:mm |
| `temperature` | `float` | °C |
| `duration` | `int` | seconds |

### FridgeStatus

Mini-fridge from [Fridge Status](endpoints/fridge-status.md).

| Field | Type | Unit |
|-------|------|------|
| `active` | `bool` | — |
| `temperature` | `float` | °C |
| `mode` | `str` | — |

### LockerStatus

Storage locker from [Locker Status](endpoints/locker-status.md).

| Field | Type |
|-------|------|
| `open` | `bool` |
| `locked` | `bool` |

### LockerSecret

Locker PIN config from [Locker Secret](endpoints/locker-secret.md).

| Field | Type |
|-------|------|
| `has_secret` | `bool` |
| `secret_set` | `bool` |

### VtmSettings

Theft monitoring from [VTM Settings](endpoints/vtm-settings.md).

| Field | Type |
|-------|------|
| `enabled` | `bool` |
| `notification_enabled` | `bool` |
| `geofence_alert_enabled` | `bool` |

### FragranceDetails

Fragrance system from [Fragrance](endpoints/fragrance.md).

| Field | Type |
|-------|------|
| `active` | `bool` |
| `level` | `str` |
| `fragrance_type` | `str` |

### GeofenceInfo

Geofence summary from [Geofences](endpoints/geofences.md).

| Field | Type |
|-------|------|
| `count` | `int` |
| `geofences` | `list[dict]` |

### DiagnosticEntry

Diagnostic trouble code from [Diagnostics](endpoints/diagnostics.md).

| Field | Type |
|-------|------|
| `dtc_code` | `str` |
| `severity` | `str` |
| `timestamp` | `datetime` |
| `status` | `str` |

### EnergyRanking

Energy ranking from [Energy Ranking](endpoints/energy-ranking.md).

| Field | Type | Unit |
|-------|------|------|
| `my_ranking` | `int` | — |
| `my_value` | `float` | kWh/100km |
| `total_participants` | `int` | — |

### FOTANotification

FOTA updates from [FOTA Notification](endpoints/fota-notification.md).

| Field | Type |
|-------|------|
| `has_notification` | `bool` |
| `pending_count` | `int` |

### VehicleData

Combined coordinator output — aggregates all of the above models.

| Field | Type | Optional |
|-------|------|----------|
| `vehicle` | `Vehicle` | No |
| `status` | `VehicleStatus` | Yes |
| `ota` | `OTAInfo` | Yes |
| `telematics` | `TelematicsStatus` | Yes |
| `running_state` | `VehicleRunningState` | Yes |
| `last_trip` | `TripJournal` | Yes |
| `charging_reservation` | `ChargingReservation` | Yes |
| `climate_schedule` | `ClimateSchedule` | Yes |
| `fridge` | `FridgeStatus` | Yes |
| `locker` | `LockerStatus` | Yes |
| `locker_secret` | `LockerSecret` | Yes |
| `vtm` | `VtmSettings` | Yes |
| `fragrance` | `FragranceDetails` | Yes |
| `geofence` | `GeofenceInfo` | Yes |
| `capabilities` | `VehicleCapabilities` | Yes |
| `diagnostic` | `DiagnosticEntry` | Yes |
| `energy_ranking` | `EnergyRanking` | Yes |
| `fota_notification` | `FOTANotification` | Yes |
| `total_distance` | `float` | Yes |
| `plant_no` | `str` | Yes |
