# Entity Mapping

How API data maps to Home Assistant entities.

[← Back to API Reference](README.md) · [Data Models](models.md)

---

## Sensors (53 entities)

| Entity Key | Device Class | Unit | Source |
|------------|-------------|------|--------|
| `battery_level` | battery | % | `status.battery_level` |
| `range_remaining` | distance | km | `status.range_remaining` |
| `charging_status` | enum | — | `status.charging_state` |
| `charge_voltage` | voltage | V | `status.charge_voltage` |
| `charge_current` | current | A | `status.charge_current` |
| `time_to_full` | duration | min | `status.time_to_full` |
| `current_firmware_version` | — | — | `ota.current_version` |
| `target_firmware_version` | — | — | `ota.target_version` |
| `tyre_pressure_fl` | pressure | kPa | `status.tyre_pressure_fl` |
| `tyre_pressure_fr` | pressure | kPa | `status.tyre_pressure_fr` |
| `tyre_pressure_rl` | pressure | kPa | `status.tyre_pressure_rl` |
| `tyre_pressure_rr` | pressure | kPa | `status.tyre_pressure_rr` |
| `tyre_temp_fl` | temperature | °C | `status.tyre_temp_fl` |
| `tyre_temp_fr` | temperature | °C | `status.tyre_temp_fr` |
| `tyre_temp_rl` | temperature | °C | `status.tyre_temp_rl` |
| `tyre_temp_rr` | temperature | °C | `status.tyre_temp_rr` |
| `odometer` | distance | km | `status.odometer` |
| `days_to_service` | duration | days | `status.days_to_service` |
| `distance_to_service` | distance | km | `status.distance_to_service` |
| `battery_12v_voltage` | voltage | V | `status.battery_12v_voltage` |
| `battery_12v_level` | battery | % | `status.battery_12v_level` |
| `interior_temp` | temperature | °C | `status.interior_temp` |
| `exterior_temp` | temperature | °C | `status.exterior_temp` |
| `power_mode` | enum | — | `running_state.power_mode` |
| `speed` | speed | km/h | `running_state.speed` |
| `charging_schedule_status` | enum | — | `charging_reservation.active` |
| `charging_schedule_start` | — | — | `charging_reservation.start_time` |
| `charging_schedule_end` | — | — | `charging_reservation.end_time` |
| `charging_target_soc` | battery | % | `charging_reservation.target_soc` |
| `climate_schedule_status` | enum | — | `climate_schedule.enabled` |
| `climate_schedule_time` | — | — | `climate_schedule.scheduled_time` |
| `climate_schedule_temp` | temperature | °C | `climate_schedule.temperature` |
| `climate_schedule_duration` | duration | s | `climate_schedule.duration` |
| `last_trip_distance` | distance | km | `last_trip.distance` |
| `last_trip_duration` | duration | s | `last_trip.duration` |
| `last_trip_energy` | energy | kWh | `last_trip.energy_consumption` |
| `last_trip_avg_consumption` | — | kWh/100km | `last_trip.avg_energy_consumption` |
| `last_trip_avg_speed` | speed | km/h | `last_trip.avg_speed` |
| `last_trip_max_speed` | speed | km/h | `last_trip.max_speed` |
| `total_distance` | distance | km | `total_distance` |
| `energy_ranking` | — | — | `energy_ranking.my_ranking` |
| `fridge_temperature` | temperature | °C | `fridge.temperature` |
| `fridge_mode` | enum | — | `fridge.mode` |
| `fragrance_level` | — | — | `fragrance.level` |
| `geofence_count` | — | — | `geofence.count` |
| `diagnostic_status` | — | — | `diagnostic.status` |
| `diagnostic_code` | — | — | `diagnostic.dtc_code` |
| `backup_battery_voltage` | voltage | V | `telematics.backup_battery_voltage` |
| `backup_battery_level` | battery | % | `telematics.backup_battery_level` |
| `capability_count` | — | — | `len(capabilities.service_ids)` |
| `washer_fluid_level` | — | — | `status.washer_fluid_level` |
| `fota_pending_count` | — | — | `fota_notification.pending_count` |

---

## Binary Sensors (28 entities)

| Entity Key | Device Class | Source | Notes |
|------------|-------------|--------|-------|
| `driver_door` | door | `status.doors["driver"]` | |
| `passenger_door` | door | `status.doors["passenger"]` | |
| `rear_left_door` | door | `status.doors["rear_left"]` | |
| `rear_right_door` | door | `status.doors["rear_right"]` | |
| `trunk` | door | `status.doors["trunk"]` | |
| `driver_window` | window | `status.windows["driver"]` | |
| `passenger_window` | window | `status.windows["passenger"]` | |
| `rear_left_window` | window | `status.windows["rear_left"]` | |
| `rear_right_window` | window | `status.windows["rear_right"]` | |
| `charger_connected` | plug | `status.charger_connected` | |
| `update_available` | update | `ota.update_available` | |
| `tyre_warning_fl` | problem | `status.tyre_warning_fl` | |
| `tyre_warning_fr` | problem | `status.tyre_warning_fr` | |
| `tyre_warning_rl` | problem | `status.tyre_warning_rl` | |
| `tyre_warning_rr` | problem | `status.tyre_warning_rr` | |
| `telematics_connected` | connectivity | `telematics.connected` | |
| `brake_fluid_ok` | problem | `!status.brake_fluid_ok` | Inverted — on = problem |
| `fridge_active` | running | `fridge.active` | |
| `fragrance_active` | — | `fragrance.active` | |
| `locker_open` | opening | `locker.open` | |
| `vtm_enabled` | — | `vtm.enabled` | |
| `vtm_notification_enabled` | — | `vtm.notification_enabled` | |
| `vtm_geofence_alert` | — | `vtm.geofence_alert_enabled` | |
| `locker_locked` | lock | `!locker.locked` | Inverted — on = unlocked |
| `diagnostic_active` | problem | `diagnostic.status == "active"` | |
| `locker_secret_set` | — | `locker_secret.secret_set` | |
| `fota_available` | update | `fota_notification.has_notification` | |

---

## Device Tracker (1 entity)

| Entity Key | Source |
|------------|--------|
| `location` | `status.latitude`, `status.longitude` |

---

## Dynamic Visibility

Entities are **dynamically hidden** when their data source returns `None`. The `async_setup_entry` function in each platform skips entities where the `value_fn` returns `None` for the current vehicle data. This means:

- Vehicles without a fridge won't show fridge entities
- Vehicles without VTM won't show VTM entities
- Endpoints that fail (403, 1405, 8153) result in their entities being hidden

---

## Summary

| Platform | Count |
|----------|-------|
| Sensor | 53 |
| Binary Sensor | 28 |
| Device Tracker | 1 |
| **Total** | **82** |
