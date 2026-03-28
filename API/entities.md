# Entity Mapping

How API data maps to Home Assistant entities.

[← Back to API Reference](README.md) · [Data Models](models.md)

> **Capability Filtering**: Entities with a `Required Capability` value are only created when the vehicle's capability API reports that function as enabled (`valueEnable: true`). Entities marked `—` are always created.

---

## Sensors (53 entities)

| Entity Key | Device Class | Unit | Source | Required Capability |
|------------|-------------|------|--------|---------------------|
| `battery_level` | battery | % | `status.battery_level` | — |
| `range_remaining` | distance | km | `status.range_remaining` | — |
| `charging_status` | enum | — | `status.charging_state` | `FUNCTION_ID_CHARGING` |
| `charge_voltage` | voltage | V | `status.charge_voltage` | `FUNCTION_ID_CHARGING` |
| `charge_current` | current | A | `status.charge_current` | `FUNCTION_ID_CHARGING` |
| `time_to_full` | duration | min | `status.time_to_full` | `FUNCTION_ID_CHARGING` |
| `current_firmware_version` | — | — | `ota.current_version` | — |
| `target_firmware_version` | — | — | `ota.target_version` | — |
| `tyre_pressure_fl` | pressure | kPa | `status.tyre_pressure_fl` | `FUNCTION_ID_TYRE_PRESSURE` |
| `tyre_pressure_fr` | pressure | kPa | `status.tyre_pressure_fr` | `FUNCTION_ID_TYRE_PRESSURE` |
| `tyre_pressure_rl` | pressure | kPa | `status.tyre_pressure_rl` | `FUNCTION_ID_TYRE_PRESSURE` |
| `tyre_pressure_rr` | pressure | kPa | `status.tyre_pressure_rr` | `FUNCTION_ID_TYRE_PRESSURE` |
| `tyre_temp_fl` | temperature | °C | `status.tyre_temp_fl` | `FUNCTION_ID_TYRE_PRESSURE` |
| `tyre_temp_fr` | temperature | °C | `status.tyre_temp_fr` | `FUNCTION_ID_TYRE_PRESSURE` |
| `tyre_temp_rl` | temperature | °C | `status.tyre_temp_rl` | `FUNCTION_ID_TYRE_PRESSURE` |
| `tyre_temp_rr` | temperature | °C | `status.tyre_temp_rr` | `FUNCTION_ID_TYRE_PRESSURE` |
| `odometer` | distance | km | `status.odometer` | `FUNCTION_ID_TOTAL_MILEAGE` |
| `days_to_service` | duration | days | `status.days_to_service` | — |
| `distance_to_service` | distance | km | `status.distance_to_service` | — |
| `battery_12v_voltage` | voltage | V | `status.battery_12v_voltage` | — |
| `battery_12v_level` | battery | % | `status.battery_12v_level` | — |
| `interior_temp` | temperature | °C | `status.interior_temp` | — |
| `exterior_temp` | temperature | °C | `status.exterior_temp` | — |
| `power_mode` | enum | — | `running_state.power_mode` | — |
| `speed` | speed | km/h | `running_state.speed` | — |
| `charging_schedule_status` | enum | — | `charging_reservation.active` | `FUNCTION_ID_CHARGING_RESERVATION` |
| `charging_schedule_start` | — | — | `charging_reservation.start_time` | `FUNCTION_ID_CHARGING_RESERVATION` |
| `charging_schedule_end` | — | — | `charging_reservation.end_time` | `FUNCTION_ID_CHARGING_RESERVATION` |
| `charging_target_soc` | battery | % | `charging_reservation.target_soc` | `FUNCTION_ID_CHARGING_RESERVATION` |
| `climate_schedule_status` | enum | — | `climate_schedule.enabled` | `FUNCTION_ID_CLIMATE_STATUS` |
| `climate_schedule_time` | — | — | `climate_schedule.scheduled_time` | `FUNCTION_ID_CLIMATE_STATUS` |
| `climate_schedule_temp` | temperature | °C | `climate_schedule.temperature` | `FUNCTION_ID_CLIMATE_STATUS` |
| `climate_schedule_duration` | duration | s | `climate_schedule.duration` | `FUNCTION_ID_CLIMATE_STATUS` |
| `last_trip_distance` | distance | km | `last_trip.distance` | — |
| `last_trip_duration` | duration | s | `last_trip.duration` | — |
| `last_trip_energy` | energy | kWh | `last_trip.energy_consumption` | — |
| `last_trip_avg_consumption` | — | kWh/100km | `last_trip.avg_energy_consumption` | — |
| `last_trip_avg_speed` | speed | km/h | `last_trip.avg_speed` | — |
| `last_trip_max_speed` | speed | km/h | `last_trip.max_speed` | — |
| `total_distance` | distance | km | `total_distance` | — |
| `energy_ranking` | — | — | `energy_ranking.my_ranking` | — |
| `fridge_temperature` | temperature | °C | `fridge.temperature` | — |
| `fridge_mode` | enum | — | `fridge.mode` | — |
| `fragrance_level` | — | — | `fragrance.level` | `FUNCTION_ID_FRAGRANCE` |
| `geofence_count` | — | — | `geofence.count` | — |
| `diagnostic_status` | — | — | `diagnostic.status` | — |
| `diagnostic_code` | — | — | `diagnostic.dtc_code` | — |
| `backup_battery_voltage` | voltage | V | `telematics.backup_battery_voltage` | — |
| `backup_battery_level` | battery | % | `telematics.backup_battery_level` | — |
| `capability_count` | — | — | `len(capabilities.service_ids)` | — |
| `washer_fluid_low` | — | — | `status.washer_fluid_low` | — |
| `fota_pending_count` | — | — | `fota_notification.pending_count` | — |
| `vehicle_image_path` | — | — | Local path to downloaded side-view image | — |
| `driver_seat_heating` | — | — | `status.driver_seat_heating` | `FUNCTION_ID_SEAT_HEAT` |
| `passenger_seat_heating` | — | — | `status.passenger_seat_heating` | `FUNCTION_ID_SEAT_HEAT` |
| `rear_left_seat_heating` | — | — | `status.rear_left_seat_heating` | `FUNCTION_ID_SEAT_HEAT` |
| `rear_right_seat_heating` | — | — | `status.rear_right_seat_heating` | `FUNCTION_ID_SEAT_HEAT` |
| `driver_seat_ventilation` | — | — | `status.driver_seat_ventilation` | `FUNCTION_ID_SEAT_VENT` |
| `passenger_seat_ventilation` | — | — | `status.passenger_seat_ventilation` | `FUNCTION_ID_SEAT_VENT` |
| `rear_left_seat_ventilation` | — | — | `status.rear_left_seat_ventilation` | `FUNCTION_ID_SEAT_VENT` |
| `rear_right_seat_ventilation` | — | — | `status.rear_right_seat_ventilation` | `FUNCTION_ID_SEAT_VENT` |
| `dc_charge_current` | current | A | `status.dc_charge_current` | `FUNCTION_ID_CHARGING` |
| `charging_power` | power | kW | `status.charging_power` | `FUNCTION_ID_CHARGING` |

---

## Binary Sensors (28+ entities)

| Entity Key | Device Class | Source | Required Capability |
|------------|-------------|--------|---------------------|
| `driver_door` | door | `status.doors["driver"]` | `FUNCTION_ID_DOORS_STATUS` |
| `passenger_door` | door | `status.doors["passenger"]` | `FUNCTION_ID_DOORS_STATUS` |
| `rear_left_door` | door | `status.doors["rear_left"]` | `FUNCTION_ID_DOORS_STATUS` |
| `rear_right_door` | door | `status.doors["rear_right"]` | `FUNCTION_ID_DOORS_STATUS` |
| `trunk` | door | `status.doors["trunk"]` | `FUNCTION_ID_TRUNK_STATUS` |
| `driver_window` | window | `status.windows["driver"]` | `FUNCTION_ID_WINDOW_STATUS` |
| `passenger_window` | window | `status.windows["passenger"]` | `FUNCTION_ID_WINDOW_STATUS` |
| `rear_left_window` | window | `status.windows["rear_left"]` | `FUNCTION_ID_WINDOW_STATUS` |
| `rear_right_window` | window | `status.windows["rear_right"]` | `FUNCTION_ID_WINDOW_STATUS` |
| `charger_connected` | plug | `status.charger_connected` | — |
| `update_available` | update | `ota.update_available` | — |
| `tyre_warning_fl` | problem | `status.tyre_warning_fl` | `FUNCTION_ID_TYRE_PRESSURE` |
| `tyre_warning_fr` | problem | `status.tyre_warning_fr` | `FUNCTION_ID_TYRE_PRESSURE` |
| `tyre_warning_rl` | problem | `status.tyre_warning_rl` | `FUNCTION_ID_TYRE_PRESSURE` |
| `tyre_warning_rr` | problem | `status.tyre_warning_rr` | `FUNCTION_ID_TYRE_PRESSURE` |
| `telematics_connected` | connectivity | `telematics.connected` | — |
| `brake_fluid_ok` | problem | `!status.brake_fluid_ok` | — |
| `washer_fluid_low` | problem | `status.washer_fluid_low` | — |
| `fridge_active` | running | `fridge.active` | — |
| `fragrance_active` | — | `fragrance.active` | `FUNCTION_ID_FRAGRANCE` |
| `locker_open` | opening | `locker.open` | — |
| `vtm_enabled` | — | `vtm.enabled` | — |
| `vtm_notification_enabled` | — | `vtm.notification_enabled` | — |
| `vtm_geofence_alert` | — | `vtm.geofence_alert_enabled` | — |
| `locker_locked` | lock | `!locker.locked` | — |
| `diagnostic_active` | problem | `diagnostic.status == "active"` | — |
| `locker_secret_set` | — | `locker_secret.secret_set` | — |
| `fota_available` | update | `fota_notification.has_notification` | — |
| `door_lock_driver` | lock | `status.door_lock_driver` | `FUNCTION_ID_DOOR_STATUS` |
| `door_lock_passenger` | lock | `status.door_lock_passenger` | `FUNCTION_ID_DOOR_STATUS` |
| `door_lock_rear_left` | lock | `status.door_lock_driver_rear` | `FUNCTION_ID_DOOR_STATUS` |
| `door_lock_rear_right` | lock | `status.door_lock_passenger_rear` | `FUNCTION_ID_DOOR_STATUS` |
| `trunk_locked` | lock | `status.trunk_locked` | `FUNCTION_ID_TRUNK_STATUS` |
| `engine_hood` | opening | `status.engine_hood_open` | `FUNCTION_ID_HOOD_STATUS` |
| `charge_lid_ac` | opening | `status.charge_lid_ac_open` | `FUNCTION_ID_CHARGE_PORT_STATUS` |
| `charge_lid_dc` | opening | `status.charge_lid_dc_open` | `FUNCTION_ID_CHARGE_PORT_STATUS` |
| `sunroof_open` | opening | `status.sunroof_open` | `FUNCTION_ID_SKYLIGHT_STATUS` |
| `sun_curtain_rear_open` | opening | `status.sun_curtain_rear_open` | `FUNCTION_ID_CURTAIN_STATUS` |
| `curtain_open` | opening | `status.curtain_open` | `FUNCTION_ID_CURTAIN_STATUS` |

---

## Locks (2 entities)

| Entity Key | Source | Required Capability |
|------------|--------|---------------------|
| `smart_door_lock` | `status.door_lock_*` | `FUNCTION_ID_REMOTE_LOCK` |
| `smart_trunk_locker` | `locker.locked` | — |

---

## Switches (5 entities)

| Entity Key | Source | Required Capability |
|------------|--------|---------------------|
| `smart_charging` | `status.charging_state` | — |
| `smart_fridge` | `fridge.active` | — |
| `smart_fragrance` | `fragrance.active` | `FUNCTION_ID_FRAGRANCE` |
| `smart_vtm` | `vtm.enabled` | — |
| `smart_climate_schedule` | `climate_schedule.enabled` | `FUNCTION_ID_CHARGING_RESERVATION` |

---

## Buttons (4 entities)

| Entity Key | Action | Required Capability |
|------------|--------|---------------------|
| `smart_horn` | Honk horn | `FUNCTION_ID_HONK_FLASH` |
| `smart_flash_lights` | Flash lights | `FUNCTION_ID_HONK_FLASH` |
| `smart_find_my_car` | Horn + flash | `FUNCTION_ID_HONK_FLASH` |
| `smart_close_windows` | Close all windows | `FUNCTION_ID_WINDOW_CLOSE` |

---

## Selects (4 entities)

| Entity Key | Options | Required Capability |
|------------|---------|---------------------|
| `driver_seat_heating_control` | off/low/medium/high | `FUNCTION_ID_SEAT_HEAT` |
| `passenger_seat_heating_control` | off/low/medium/high | `FUNCTION_ID_SEAT_HEAT` |
| `steering_wheel_heating_control` | off/low/medium/high | `FUNCTION_ID_SEAT_HEAT` |
| `driver_seat_ventilation_control` | off/low/medium/high | `FUNCTION_ID_SEAT_VENT` |

---

## Climate (1 entity)

| Entity Key | Source | Required Capability |
|------------|--------|---------------------|
| `climate` | Pre-conditioning control | `FUNCTION_ID_CLIMATE` |

---

## Number (1 entity)

| Entity Key | Range | Required Capability |
|------------|-------|---------------------|
| `target_soc` | 20-100% | `FUNCTION_ID_CHARGING_RESERVATION` |

---

## Time (3 entities)

| Entity Key | Source | Required Capability |
|------------|--------|---------------------|
| `smart_charging_start` | `charging_reservation.start_time` | `FUNCTION_ID_CHARGING_RESERVATION` |
| `smart_charging_end` | `charging_reservation.end_time` | `FUNCTION_ID_CHARGING_RESERVATION` |
| `smart_climate_schedule_time` | `climate_schedule.scheduled_time` | — |

---

## Device Tracker (1 entity)

| Entity Key | Source |
|------------|--------|
| `location` | `status.latitude`, `status.longitude` |

---

## Capability Filtering

Entities are filtered at setup time based on vehicle capability flags from the [Capabilities API](endpoints/capabilities.md):

- **Fail-open**: If the capability API is unavailable or returns no data, all entities are created (default `True`)
- **Per-entity control**: Only entities with a `required_capability` value are filtered; entities without one are always created
- **One-time**: Filtering happens only during entity setup, not on each poll
- **Logged**: Skipped entities are logged at `DEBUG` level; per-vehicle filter counts at `INFO` level

---

## Dynamic Visibility

Entities are **dynamically hidden** when their data source returns `None`. The `async_setup_entry` function in each platform skips entities where the `value_fn` returns `None` for the current vehicle data. This means:

- Vehicles without a fridge won't show fridge entities
- Vehicles without VTM won't show VTM entities
- Endpoints that fail (403, 1405, 8153) result in their entities being hidden
