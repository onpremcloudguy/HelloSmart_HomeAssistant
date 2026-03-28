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
| `ac_charging` | 2 | AC charging active |
| `dc_charging` | 15 | DC fast charging active |
| `super_charging` | 24 | Super charging (DC fast) |
| `plugged_not_charging` | 25 | Plugged in but not charging |
| `boost_charging` | 28 | Boost charging active |
| `wireless_charging` | 30 | Wireless charging active |

### PowerMode

Vehicle ignition power state.

| Value | powerMode | Description |
|-------|-----------|-------------|
| `off` | `"0"` | Vehicle off |
| `accessory` | `"1"` | Accessory mode |
| `on` | `"2"` | Ignition on / ready to drive |
| `cranking` | `"3"` | Engine starting |

### VehicleModel

Smart vehicle model line, derived from `matCode[0:3]` or `seriesCodeVs`.

Source: APK `VehicleModel.java`, `VehicleInfoConstants.java`

| Value | matCode Prefix | Series Code | Marketing Name |
|-------|---------------|-------------|----------------|
| `#1` | `HX1` | `HX11` | Smart #1 (compact SUV) |
| `#3` | `HC1` | `HC11` | Smart #3 (mid-size SUV) |
| `#5` | `HY1` | `HY11` | Smart #5 (full-size SUV) |
| `Unknown` | — | — | Unrecognised model |

### VehicleEdition

Vehicle trim/edition level, derived from `matCode[5:7]`.

Source: APK `VehicleEdition.java`, `ClimateFragment.java`

| Value | matCode[5:7] | Description |
|-------|-------------|-------------|
| `Pure` | `80` | Entry-level |
| `Pro` | `D1` | Mid-range |
| `Pulse` | `GN` | Mid-range (EU naming) |
| `Premium` | `D2` | Upper-range |
| `BRABUS` | `D3` | Performance / top-range |
| `Launch Edition` | `01` | Limited launch variant |
| `Unknown` | — | Unrecognised trim code |

#### Feature Availability by Edition

| Property | Method | Pure | Pro | Pulse | Premium | BRABUS | Launch |
|----------|--------|------|-----|-------|---------|--------|--------|
| Driver seat heating | `has_driver_seat_heating` | No | Yes | Yes | Yes | Yes | Yes |
| PM2.5 sensor | `has_pm25` | No | No | Yes | Yes | Yes | Yes |

> These gates are used by the integration to automatically exclude entities that the vehicle hardware doesn't support.

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
| `model_name` | `str` | Full model name (e.g., `CM590_HC11_Performance_4WD_RHD_APAC`) |
| `model_year` | `str` | Model year |
| `series_code` | `str` | Series/variant code with region suffix (e.g., `HC11_IL`) |
| `color_name` | `str` | Paint colour name |
| `color_code` | `str` | Paint colour code |
| `model_code` | `str` | Full model code (used by VC endpoint) |
| `factory_code` | `str` | Factory / production plant code |
| `mat_code` | `str` | Material code — encodes model and trim |
| `series_name` | `str` | Series name (e.g., `HC11`) |
| `vehicle_type` | `str` | Vehicle type identifier |
| `fuel_tank_capacity` | `str` | Fuel tank capacity (always `"0"` for BEV) |
| `ihu_platform` | `str` | IHU (infotainment) platform type |
| `tbox_platform` | `str` | T-Box (telematics) platform type |
| `plate_no` | `str` | Registration plate number |
| `engine_no` | `str` | Motor/engine serial number |
| `default_vehicle` | `bool` | Whether this is the user's primary vehicle |
| `share_status` | `str` | Share status: `"N"` / `"Y"` |

#### Derived Properties

| Property | Type | Description |
|----------|------|-------------|
| `edition` | `VehicleEdition` | Trim level derived from `mat_code[5:7]` |
| `smart_model` | `VehicleModel` | Model line derived from `mat_code[0:3]` / `series_code` |

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
| `washer_fluid_low` | `bool` | — | Yes |
| `brake_fluid_ok` | `bool` | — | Yes |
| `battery_12v_voltage` | `float` | V | Yes |
| `battery_12v_level` | `float` | % | Yes |
| `power_mode` | `PowerMode` | — | Yes |
| `last_updated` | `datetime` | — | Yes |
| `window_position_driver` | `int \| None` | % | Yes |
| `window_position_passenger` | `int \| None` | % | Yes |
| `window_position_driver_rear` | `int \| None` | % | Yes |
| `window_position_passenger_rear` | `int \| None` | % | Yes |
| `sunroof_position` | `int \| None` | % | Yes |
| `sunroof_open` | `bool \| None` | — | Yes |
| `curtain_position` | `int \| None` | % | Yes |
| `curtain_open` | `bool \| None` | — | Yes |
| `sun_curtain_rear_position` | `int \| None` | % | Yes |
| `sun_curtain_rear_open` | `bool \| None` | — | Yes |
| `driver_seat_heating` | `int \| None` | level | Yes |
| `passenger_seat_heating` | `int \| None` | level | Yes |
| `rear_left_seat_heating` | `int \| None` | level | Yes |
| `rear_right_seat_heating` | `int \| None` | level | Yes |
| `driver_seat_ventilation` | `int \| None` | level | Yes |
| `passenger_seat_ventilation` | `int \| None` | level | Yes |
| `rear_left_seat_ventilation` | `int \| None` | level | Yes |
| `rear_right_seat_ventilation` | `int \| None` | level | Yes |
| `steering_wheel_heating` | `int \| None` | level | Yes |
| `pre_climate_active` | `bool \| None` | — | Yes |
| `defrost_active` | `bool \| None` | — | Yes |
| `air_blower_active` | `bool \| None` | — | Yes |
| `climate_overheat_protection` | `bool \| None` | — | Yes |

> **Note on `None` values**: Position fields (`sunroof_position`, `curtain_position`, `sun_curtain_rear_position`, window positions) return `None` when the API reports the sentinel value `101`, indicating the hardware is not equipped. The corresponding boolean fields (e.g., `sunroof_open`) are also set to `None`. See [Sentinel Values](endpoints/vehicle-status.md#sentinel-value-101-not-equipped).

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
| `ability` | `VehicleAbility` | Yes |
| `vehicle_image_path` | `str` | Yes |
| `total_distance` | `float` | Yes |
| `plant_no` | `str` | Yes |

---

### `VehicleAbility`

Vehicle visual configuration and remote control capabilities from the VC service.

| Field | Type | Optional | Description |
|-------|------|----------|-------------|
| `images_path` | `str` | No | CDN URL for side-view image |
| `top_images_path` | `str` | No | CDN URL for top-down image |
| `battery_images_path` | `str` | No | CDN URL for battery image |
| `interior_images_path` | `str` | No | CDN URL for interior image (may be empty) |
| `color_code` | `str` | No | Exterior color code |
| `color_name_mss` | `str` | No | Exterior color name |
| `contrast_color_code` | `str` | No | Accent color code |
| `contrast_color_name` | `str` | No | Accent color name |
| `interior_color_name` | `str` | No | Interior color name |
| `hub_code` | `str` | No | Hub/dealer code |
| `hub_name` | `str` | No | Hub/dealer name |
| `model_code_mss` | `str` | No | MSS model code |
| `model_code_vdp` | `str` | No | VDP model code |
| `model_name` | `str` | No | Model name |
| `vehicle_name` | `str` | No | Internal vehicle name |
| `vehicle_nickname` | `str` | No | User-assigned nickname |
| `side_logo_light_name` | `str` | No | Side logo light style |
| `license_plate_number` | `str` | No | Registration plate |

---

### VehicleCapabilities

Vehicle capability flags from the [Capabilities API](endpoints/capabilities.md).

| Field | Type | Description |
|-------|------|-------------|
| `service_ids` | `list[str]` | Legacy service identifiers where `enabled == true` (backward compat) |
| `capability_flags` | `dict[str, bool]` | Function ID → enabled mapping from `data.list[].functionId`/`valueEnable` |

The `capability_flags` dict is used by entity platforms to filter entities at setup time. Keys are `functionId` strings (e.g., `"remote_control_lock"`, `"charging_status"`). Values are `True` (enabled) or `False` (disabled).

---

### StaticVehicleData

Cached static vehicle data fetched once per session. Used by `SmartDataCoordinator._static_cache` to avoid re-fetching data that doesn't change between polls.

| Field | Type | Description |
|-------|------|-------------|
| `capabilities` | `VehicleCapabilities \| None` | Vehicle capability flags |
| `ability` | `VehicleAbility \| None` | Vehicle visual config and images |
| `plant_no` | `str` | Plant number for device info |
| `vehicle_image_path` | `str` | Local path to downloaded vehicle image |
