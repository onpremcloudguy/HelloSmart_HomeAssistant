# Tasks: APK GET Endpoint Extraction & Integration

**Input**: Design documents from `/specs/002-apk-get-endpoints/`
**Prerequisites**: plan.md (required), spec.md (required), research.md, data-model.md, contracts/smart-api-extended.md, quickstart.md

**Tests**: Not explicitly requested in the feature specification. Test tasks are omitted.

**Organization**: Tasks are grouped by user story to enable independent implementation and testing of each story.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (e.g., US1, US2, US3)
- Include exact file paths in descriptions

## Path Conventions

- **Custom integration**: `custom_components/hello_smart/`
- **Specs/design**: `specs/002-apk-get-endpoints/`

---

## Phase 1: Setup

**Purpose**: Configuration constants and shared infrastructure changes that all user stories depend on

- [X] T001 Update `DEFAULT_SCAN_INTERVAL` from 300 to 60 in `custom_components/hello_smart/const.py`
- [X] T002 [P] Add new sensitive fields (`imei`, `locker_secret`, `secret_set`) to `SENSITIVE_FIELDS` tuple in `custom_components/hello_smart/const.py`

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Data models, API methods, and coordinator wiring that MUST be complete before any user story entities can be created

**⚠️ CRITICAL**: No user story work can begin until this phase is complete

- [X] T003 Add `PowerMode` enum and `power_mode_from_api()` mapping function to `custom_components/hello_smart/models.py`
- [X] T004 [P] Add 23 new fields to `VehicleStatus` dataclass (tyre pressure×4, tyre temp×4, tyre warning×4, odometer, days_to_service, distance_to_service, washer_fluid_level, brake_fluid_ok, battery_12v_voltage, battery_12v_level, fragrance_active, power_mode, interior_temp, exterior_temp) in `custom_components/hello_smart/models.py`
- [X] T005 [P] Add `TelematicsStatus` dataclass to `custom_components/hello_smart/models.py`
- [X] T006 [P] Add `VehicleRunningState` dataclass to `custom_components/hello_smart/models.py`
- [X] T007 [P] Add `TripJournal` dataclass to `custom_components/hello_smart/models.py`
- [X] T008 [P] Add `ChargingReservation` dataclass to `custom_components/hello_smart/models.py`
- [X] T009 [P] Add `ClimateSchedule` dataclass to `custom_components/hello_smart/models.py`
- [X] T010 [P] Add `FridgeStatus`, `LockerStatus`, `FragranceDetails` dataclasses to `custom_components/hello_smart/models.py`
- [X] T011 [P] Add `VtmSettings`, `GeofenceInfo` dataclasses to `custom_components/hello_smart/models.py`
- [X] T012 [P] Add `VehicleCapabilities`, `DiagnosticEntry`, `EnergyRanking` dataclasses to `custom_components/hello_smart/models.py`
- [X] T013 Extend `VehicleData` dataclass with 15 new optional fields (telematics, running_state, last_trip, charging_reservation, climate_schedule, fridge, locker, vtm, fragrance, geofence, capabilities, diagnostic, energy_ranking, total_distance) in `custom_components/hello_smart/models.py`
- [X] T014 Extend `_parse_vehicle_status()` to extract tyre pressure (×4 kPa), tyre temp (×4 °C), tyre warnings (×4), odometer, days/distance to service, washer fluid, brake fluid, 12V battery voltage/level, fragrance_active, interior/exterior temp, and power_mode from existing `additionalVehicleStatus.maintenanceStatus`, `climateStatus`, and `basicVehicleStatus` blocks in `custom_components/hello_smart/api.py`
- [X] T015 Add `async_get_vehicle_state()` method (GET `/remote-control/vehicle/status/state/{vin}`) returning `VehicleRunningState` to `SmartAPI` in `custom_components/hello_smart/api.py`
- [X] T016 [P] Add `async_get_telematics()` method (GET `/remote-control/vehicle/telematics/{vin}`) returning `TelematicsStatus` to `SmartAPI` in `custom_components/hello_smart/api.py`
- [X] T017 [P] Add `async_get_diagnostic_history()` method (GET `/remote-control/vehicle/status/history/diagnostic/{vin}`) returning `DiagnosticEntry` to `SmartAPI` in `custom_components/hello_smart/api.py`
- [X] T018 [P] Add `async_get_charging_reservation()` method (GET `/remote-control/charging/reservation/{vin}`) returning `ChargingReservation` to `SmartAPI` in `custom_components/hello_smart/api.py`
- [X] T019 [P] Add `async_get_climate_schedule()` method (GET `/remote-control/schedule/{vin}`) returning `ClimateSchedule` to `SmartAPI` in `custom_components/hello_smart/api.py`
- [X] T020 [P] Add `async_get_fridge_status()` method (GET `/remote-control/getFridge/status/{vin}`) returning `FridgeStatus` to `SmartAPI` in `custom_components/hello_smart/api.py`
- [X] T021 [P] Add `async_get_locker_status()` method (GET `/remote-control/getLocker/status/{vin}`) returning `LockerStatus` to `SmartAPI` in `custom_components/hello_smart/api.py`
- [X] T022 [P] Add `async_get_vtm_settings()` method (GET `/remote-control/getVtmSettingStatus`) returning `VtmSettings` to `SmartAPI` in `custom_components/hello_smart/api.py`
- [X] T023 [P] Add `async_get_fragrance()` method (GET `/remote-control/vehicle/fragrance/{vin}`) returning `FragranceDetails` to `SmartAPI` in `custom_components/hello_smart/api.py`
- [X] T024 [P] Add `async_get_trip_journal()` method (GET `/geelyTCAccess/tcservices/vehicle/status/journalLogV4/{vin}`) returning `TripJournal` to `SmartAPI` in `custom_components/hello_smart/api.py`
- [X] T025 [P] Add `async_get_total_distance()` method (GET `/geelyTCAccess/tcservices/vehicle/status/getTotalDistanceByLabel/{vin}`) returning `float | None` to `SmartAPI` in `custom_components/hello_smart/api.py`
- [X] T026 [P] Add `async_get_geofences()` method (GET `/geelyTCAccess/tcservices/vehicle/geofence/all/{vin}`) returning `GeofenceInfo` to `SmartAPI` in `custom_components/hello_smart/api.py`
- [X] T027 [P] Add `async_get_capabilities()` method (GET `/geelyTCAccess/tcservices/capability/{vin}`) returning `VehicleCapabilities` to `SmartAPI` in `custom_components/hello_smart/api.py`
- [X] T028 [P] Add `async_get_energy_ranking()` method (GET `/geelyTCAccess/tcservices/vehicle/status/ranking/aveEnergyConsumption/vehicleModel/{vin}?topn=100`) returning `EnergyRanking` to `SmartAPI` in `custom_components/hello_smart/api.py`
- [X] T029 [P] Add `async_get_fota_notification()` method (GET `/fota/geea/assignment/notification`) returning `dict` to `SmartAPI` in `custom_components/hello_smart/api.py`
- [X] T030 [P] Add `async_get_plant_no()` method (GET `/geelyTCAccess/tcservices/customer/vehicle/plantNo/{vin}`) returning `str` to `SmartAPI` in `custom_components/hello_smart/api.py`
- [X] T031 Wire all new `async_get_*` methods into `_async_fetch_all_vehicles()` in `custom_components/hello_smart/coordinator.py` — each in its own `try/except SmartAPIError` block logging at debug level, populating the corresponding `VehicleData` fields
- [X] T032 Enhance `DeviceInfo` in `_async_fetch_all_vehicles()` to include `model_id=vehicle.series_code`, `hw_version=vehicle.model_year`, `sw_version=ota.current_version`, `serial_number=vin`, `suggested_area="Garage"` in `custom_components/hello_smart/coordinator.py`
- [X] T033 Add dynamic entity visibility filter to `async_setup_entry()` in `custom_components/hello_smart/sensor.py` — only add entity if `description.value_fn(vehicle_data) is not None`
- [X] T034 [P] Add dynamic entity visibility filter to `async_setup_entry()` in `custom_components/hello_smart/binary_sensor.py` — only add entity if `description.is_on_fn(vehicle_data) is not None`

**Checkpoint**: Foundation ready — all data models, API client methods, coordinator wiring, and dynamic filtering are in place. User story entity definitions can now be added.

---

## Phase 3: User Story 1 — Extended Vehicle Status (Priority: P1) 🎯 MVP

**Goal**: Expose tyre pressure (×4), tyre temperature (×4), tyre warnings (×4), odometer, maintenance data, 12V battery, interior/exterior temp, power mode, speed, telematics connectivity, and diagnostic status as HA entities.

**Independent Test**: After integration reload, verify tyre pressure FL/FR/RL/RR sensors appear with kPa values, power mode sensor shows "off"/"on", and telematics binary sensor shows connected/disconnected.

### Implementation for User Story 1

- [X] T035 [P] [US1] Add tyre pressure sensor descriptions (×4: tyre_pressure_fl, tyre_pressure_fr, tyre_pressure_rl, tyre_pressure_rr) with `device_class=PRESSURE`, `native_unit=kPa`, `state_class=MEASUREMENT` to `SENSOR_DESCRIPTIONS` in `custom_components/hello_smart/sensor.py`
- [X] T036 [P] [US1] Add tyre temperature sensor descriptions (×4: tyre_temp_fl, tyre_temp_fr, tyre_temp_rl, tyre_temp_rr) with `device_class=TEMPERATURE`, `native_unit=°C`, `state_class=MEASUREMENT` to `SENSOR_DESCRIPTIONS` in `custom_components/hello_smart/sensor.py`
- [X] T037 [P] [US1] Add maintenance sensor descriptions (odometer with `device_class=DISTANCE` in km, days_to_service, distance_to_service with `device_class=DISTANCE` in km) to `SENSOR_DESCRIPTIONS` in `custom_components/hello_smart/sensor.py`
- [X] T038 [P] [US1] Add 12V battery sensor descriptions (battery_12v_voltage with `device_class=VOLTAGE` in V, battery_12v_level with `device_class=BATTERY` in %) to `SENSOR_DESCRIPTIONS` in `custom_components/hello_smart/sensor.py`
- [X] T039 [P] [US1] Add climate temp sensor descriptions (interior_temp and exterior_temp with `device_class=TEMPERATURE` in °C) to `SENSOR_DESCRIPTIONS` in `custom_components/hello_smart/sensor.py`
- [X] T040 [P] [US1] Add power_mode sensor description with `device_class=ENUM`, options from `PowerMode` enum values, `value_fn` returning `data.status.power_mode.value if data.status.power_mode else (data.running_state.power_mode.value if data.running_state else None)` to `SENSOR_DESCRIPTIONS` in `custom_components/hello_smart/sensor.py`
- [X] T041 [P] [US1] Add speed sensor description with `device_class=SPEED`, `native_unit=km/h`, `value_fn=lambda data: data.running_state.speed if data.running_state else None` to `SENSOR_DESCRIPTIONS` in `custom_components/hello_smart/sensor.py`
- [X] T042 [P] [US1] Add tyre warning binary sensor descriptions (×4: tyre_warning_fl, tyre_warning_fr, tyre_warning_rl, tyre_warning_rr) with `device_class=PROBLEM` to `BINARY_SENSOR_DESCRIPTIONS` in `custom_components/hello_smart/binary_sensor.py`
- [X] T043 [P] [US1] Add telematics_connected binary sensor description with `device_class=CONNECTIVITY`, `is_on_fn=lambda data: data.telematics.connected if data.telematics else None` to `BINARY_SENSOR_DESCRIPTIONS` in `custom_components/hello_smart/binary_sensor.py`
- [X] T044 [P] [US1] Add brake_fluid_ok binary sensor description with `device_class=PROBLEM` (inverted: on=problem), `is_on_fn` checking `data.status.brake_fluid_ok is not None and not data.status.brake_fluid_ok` to `BINARY_SENSOR_DESCRIPTIONS` in `custom_components/hello_smart/binary_sensor.py`
- [X] T045 [US1] Add translation keys for all US1 entities (tyre_pressure_fl/fr/rl/rr, tyre_temp_fl/fr/rl/rr, odometer, days_to_service, distance_to_service, battery_12v_voltage, battery_12v_level, interior_temp, exterior_temp, power_mode, speed, tyre_warning_fl/fr/rl/rr, telematics_connected, brake_fluid_ok) to `custom_components/hello_smart/strings.json`

**Checkpoint**: User Story 1 complete — tyre, maintenance, climate, and vehicle state entities are visible under the vehicle device card.

---

## Phase 4: User Story 2 — Charging & Climate Schedule (Priority: P2)

**Goal**: Expose charging reservation status/times and climate pre-conditioning schedule as sensor entities.

**Independent Test**: Configure a charging schedule in the Smart app, reload HA, and verify charging_schedule_status shows "active" and charging_schedule_start shows the time.

### Implementation for User Story 2

- [X] T046 [P] [US2] Add charging_schedule_status sensor description with `device_class=ENUM`, options `["active", "inactive"]`, `value_fn=lambda data: "active" if data.charging_reservation and data.charging_reservation.active else ("inactive" if data.charging_reservation else None)` to `SENSOR_DESCRIPTIONS` in `custom_components/hello_smart/sensor.py`
- [X] T047 [P] [US2] Add charging_schedule_start sensor description, `value_fn=lambda data: data.charging_reservation.start_time if data.charging_reservation and data.charging_reservation.start_time else None` to `SENSOR_DESCRIPTIONS` in `custom_components/hello_smart/sensor.py`
- [X] T048 [P] [US2] Add charging_schedule_end sensor description, `value_fn=lambda data: data.charging_reservation.end_time if data.charging_reservation and data.charging_reservation.end_time else None` to `SENSOR_DESCRIPTIONS` in `custom_components/hello_smart/sensor.py`
- [X] T049 [P] [US2] Add charging_target_soc sensor description with `device_class=BATTERY`, unit `%`, `value_fn=lambda data: data.charging_reservation.target_soc if data.charging_reservation else None` to `SENSOR_DESCRIPTIONS` in `custom_components/hello_smart/sensor.py`
- [X] T050 [P] [US2] Add climate_schedule_status sensor description with `device_class=ENUM`, `value_fn` returning enabled/disabled from `data.climate_schedule` to `SENSOR_DESCRIPTIONS` in `custom_components/hello_smart/sensor.py`
- [X] T051 [P] [US2] Add climate_schedule_time sensor description, `value_fn=lambda data: data.climate_schedule.scheduled_time if data.climate_schedule and data.climate_schedule.scheduled_time else None` to `SENSOR_DESCRIPTIONS` in `custom_components/hello_smart/sensor.py`
- [X] T052 [US2] Add translation keys for all US2 entities (charging_schedule_status, charging_schedule_start, charging_schedule_end, charging_target_soc, climate_schedule_status, climate_schedule_time) to `custom_components/hello_smart/strings.json`

**Checkpoint**: User Story 2 complete — charging and climate schedule entities appear when schedules are configured.

---

## Phase 5: User Story 3 — Trip Journal & Distance (Priority: P3)

**Goal**: Expose last trip distance/duration/energy consumption and total odometer via TC endpoint as sensor entities.

**Independent Test**: After driving, verify last_trip_distance sensor shows a valid km value and odometer (from TC endpoint) reflects total distance.

### Implementation for User Story 3

- [X] T053 [P] [US3] Add last_trip_distance sensor description with `device_class=DISTANCE`, unit km, `value_fn=lambda data: data.last_trip.distance if data.last_trip else None` to `SENSOR_DESCRIPTIONS` in `custom_components/hello_smart/sensor.py`
- [X] T054 [P] [US3] Add last_trip_duration sensor description with `device_class=DURATION`, unit s, `value_fn=lambda data: data.last_trip.duration if data.last_trip else None` to `SENSOR_DESCRIPTIONS` in `custom_components/hello_smart/sensor.py`
- [X] T055 [P] [US3] Add last_trip_energy sensor description with `device_class=ENERGY`, unit kWh, `value_fn=lambda data: data.last_trip.energy_consumption if data.last_trip else None` to `SENSOR_DESCRIPTIONS` in `custom_components/hello_smart/sensor.py`
- [X] T056 [P] [US3] Add last_trip_avg_consumption sensor description, unit kWh/100km, `value_fn=lambda data: data.last_trip.avg_energy_consumption if data.last_trip else None` to `SENSOR_DESCRIPTIONS` in `custom_components/hello_smart/sensor.py`
- [X] T057 [P] [US3] Add total_distance sensor description with `device_class=DISTANCE`, unit km, `state_class=TOTAL_INCREASING`, `value_fn=lambda data: data.total_distance` to `SENSOR_DESCRIPTIONS` in `custom_components/hello_smart/sensor.py`
- [X] T058 [P] [US3] Add energy_ranking sensor description, `value_fn=lambda data: data.energy_ranking.my_ranking if data.energy_ranking else None` to `SENSOR_DESCRIPTIONS` in `custom_components/hello_smart/sensor.py`
- [X] T059 [US3] Add translation keys for all US3 entities (last_trip_distance, last_trip_duration, last_trip_energy, last_trip_avg_consumption, total_distance, energy_ranking) to `custom_components/hello_smart/strings.json`

**Checkpoint**: User Story 3 complete — trip and distance tracking entities appear when journal data is available.

---

## Phase 6: User Story 4 — Accessories: Fridge, Fragrance, Locker (Priority: P4)

**Goal**: Expose mini-fridge on/off, fragrance level/active, and locker open/closed as entities only for vehicles that have these accessories.

**Independent Test**: For a Smart #1 with a fridge, verify fridge_active binary sensor appears. For a vehicle without a fridge, verify no fridge entity exists.

### Implementation for User Story 4

- [X] T060 [P] [US4] Add fridge_active binary sensor description with `device_class=RUNNING`, `is_on_fn=lambda data: data.fridge.active if data.fridge else None` to `BINARY_SENSOR_DESCRIPTIONS` in `custom_components/hello_smart/binary_sensor.py`
- [X] T061 [P] [US4] Add fragrance_active binary sensor description, `is_on_fn=lambda data: data.fragrance.active if data.fragrance else (data.status.fragrance_active if data.status.fragrance_active is not None else None)` to `BINARY_SENSOR_DESCRIPTIONS` in `custom_components/hello_smart/binary_sensor.py`
- [X] T062 [P] [US4] Add locker_open binary sensor description with `device_class=OPENING`, `is_on_fn=lambda data: data.locker.open if data.locker else None` to `BINARY_SENSOR_DESCRIPTIONS` in `custom_components/hello_smart/binary_sensor.py`
- [X] T063 [P] [US4] Add fridge_temperature sensor description with `device_class=TEMPERATURE`, unit °C, `value_fn=lambda data: data.fridge.temperature if data.fridge else None` to `SENSOR_DESCRIPTIONS` in `custom_components/hello_smart/sensor.py`
- [X] T064 [P] [US4] Add fragrance_level sensor description, `value_fn=lambda data: data.fragrance.level if data.fragrance and data.fragrance.level else None` to `SENSOR_DESCRIPTIONS` in `custom_components/hello_smart/sensor.py`
- [X] T065 [US4] Add translation keys for all US4 entities (fridge_active, fridge_temperature, fragrance_active, fragrance_level, locker_open) to `custom_components/hello_smart/strings.json`

**Checkpoint**: User Story 4 complete — accessory entities appear only for vehicles with the relevant hardware.

---

## Phase 7: User Story 5 — VTM & Geofences (Priority: P5)

**Goal**: Expose vehicle theft monitoring enabled/disabled and geofence count as entities.

**Independent Test**: Enable VTM in the Smart app, reload HA, and verify vtm_enabled binary sensor appears as "on".

### Implementation for User Story 5

- [X] T066 [P] [US5] Add vtm_enabled binary sensor description, `is_on_fn=lambda data: data.vtm.enabled if data.vtm else None` to `BINARY_SENSOR_DESCRIPTIONS` in `custom_components/hello_smart/binary_sensor.py`
- [X] T067 [P] [US5] Add geofence_count sensor description, `value_fn=lambda data: data.geofence.count if data.geofence else None` to `SENSOR_DESCRIPTIONS` in `custom_components/hello_smart/sensor.py`
- [X] T068 [US5] Add translation keys for US5 entities (vtm_enabled, geofence_count) to `custom_components/hello_smart/strings.json`

**Checkpoint**: User Story 5 complete — VTM and geofence entities appear when the vehicle supports them.

---

## Phase 8: User Story 6 — 60-Second Auto-Refresh (Priority: P6)

**Goal**: Default polling interval is 60 seconds for all entities.

**Independent Test**: After setup, verify coordinator `update_interval` is 60 seconds and entity `last_updated` timestamps advance every ~60s.

### Implementation for User Story 6

- [X] T069 [US6] Verify `DEFAULT_SCAN_INTERVAL = 60` is applied (already changed in T001), and confirm that `MIN_SCAN_INTERVAL = 60` remains unchanged in `custom_components/hello_smart/const.py`

**Checkpoint**: User Story 6 complete — polling is 60 seconds by default. (This is effectively completed by T001 in Phase 1, but this phase serves as explicit verification.)

---

## Phase 9: User Story 7 — Vehicle Device Identity (Priority: P7)

**Goal**: Each vehicle's device card shows manufacturer, model, model_id, hw_version (year), sw_version (firmware), serial_number (VIN), and suggested_area ("Garage").

**Independent Test**: Navigate to the vehicle's device page in HA and verify all device info fields are populated. Verify all entities appear as sub-entities of the car.

### Implementation for User Story 7

- [X] T070 [US7] Verify enhanced `DeviceInfo` is applied (already implemented in T032), confirm `_attr_has_entity_name = True` is set on both `SmartSensorEntity` and `SmartBinarySensorEntity` in `custom_components/hello_smart/sensor.py` and `custom_components/hello_smart/binary_sensor.py`

**Checkpoint**: User Story 7 complete — vehicle device cards show rich identity info. (This is effectively completed by T032 in Phase 2, but this phase serves as explicit verification.)

---

## Phase 10: Polish & Cross-Cutting Concerns

**Purpose**: Final cleanup and validation across all user stories

- [X] T071 [P] Verify all new `value_fn` and `is_on_fn` lambdas handle `None` gracefully — no `AttributeError` when optional data sources are missing — across `custom_components/hello_smart/sensor.py` and `custom_components/hello_smart/binary_sensor.py`
- [X] T072 [P] Verify `SENSITIVE_FIELDS` in `custom_components/hello_smart/const.py` covers all new sensitive data (IMEI, locker secret status) and that `diagnostics.py` redaction still works
- [X] T073 [P] Verify all new imports are added to `custom_components/hello_smart/models.py`, `custom_components/hello_smart/api.py`, `custom_components/hello_smart/coordinator.py`, `custom_components/hello_smart/sensor.py`, `custom_components/hello_smart/binary_sensor.py`
- [X] T074 Run quickstart.md validation — confirm entity count in `custom_components/hello_smart/sensor.py` and `custom_components/hello_smart/binary_sensor.py` matches expectations (~25 new sensors + ~10 new binary sensors per vehicle)
- [X] T075 Verify `strings.json` has translation keys for ALL new entities and no orphaned keys in `custom_components/hello_smart/strings.json`

---

## Dependencies & Execution Order

### Phase Dependencies

- **Phase 1 (Setup)**: No dependencies — start immediately
- **Phase 2 (Foundational)**: Depends on Phase 1 (T001, T002). BLOCKS all user stories.
- **Phase 3–9 (User Stories)**: All depend on Phase 2 completion. Can proceed in priority order (P1 → P7) or in parallel.
- **Phase 10 (Polish)**: Depends on all user story phases being complete.

### User Story Dependencies

- **US1 (P1)**: After Phase 2 — no dependencies on other stories
- **US2 (P2)**: After Phase 2 — no dependencies on other stories
- **US3 (P3)**: After Phase 2 — no dependencies on other stories
- **US4 (P4)**: After Phase 2 — no dependencies on other stories
- **US5 (P5)**: After Phase 2 — no dependencies on other stories
- **US6 (P6)**: Completed inherently by T001 in Phase 1
- **US7 (P7)**: Completed inherently by T032 in Phase 2

### Within Phase 2 (Foundational)

- T003 (PowerMode enum) must complete before T004 (VehicleStatus uses PowerMode), T005–T006 (dataclasses use PowerMode)
- T004–T012 (all dataclasses) must complete before T013 (VehicleData references them)
- T013 (VehicleData) must complete before T014–T030 (API methods return these types)
- T014 (parse_vehicle_status) can run in parallel with T015–T030 (new API methods)
- T031 (coordinator wiring) depends on T014–T030 (all API methods)
- T032 (DeviceInfo) can run in parallel with T031
- T033–T034 (dynamic filtering) can run in parallel with T031–T032

### Within Each User Story Phase

- All entity description tasks marked [P] can run in parallel (they edit different sections of the same files)
- Translation key task depends on all entity descriptions being finalized

### Parallel Opportunities

```
Phase 2 parallel groups:
  Group A (can all run in parallel): T004, T005, T006, T007, T008, T009, T010, T011, T012
  Group B (after Group A): T013
  Group C (after T013, all parallel): T015, T016, T017, T018, T019, T020, T021, T022, T023, T024, T025, T026, T027, T028, T029, T030
  Group D (after Group C): T031
  Group E (parallel with D): T032, T033, T034

Phase 3–7 (all user story entity tasks marked [P] can run in parallel within each phase)
```

---

## Parallel Example: User Story 1

```bash
# Launch all sensor descriptions for US1 together:
T035: "Add tyre pressure sensor descriptions (×4) in sensor.py"
T036: "Add tyre temperature sensor descriptions (×4) in sensor.py"
T037: "Add maintenance sensor descriptions in sensor.py"
T038: "Add 12V battery sensor descriptions in sensor.py"
T039: "Add climate temp sensor descriptions in sensor.py"
T040: "Add power_mode sensor description in sensor.py"
T041: "Add speed sensor description in sensor.py"

# In parallel, launch all binary sensor descriptions:
T042: "Add tyre warning binary sensor descriptions (×4) in binary_sensor.py"
T043: "Add telematics_connected binary sensor description in binary_sensor.py"
T044: "Add brake_fluid_ok binary sensor description in binary_sensor.py"

# After all above complete:
T045: "Add translation keys for all US1 entities in strings.json"
```

---

## Implementation Strategy

### MVP First (User Story 1 Only)

1. Complete Phase 1: Setup (T001–T002)
2. Complete Phase 2: Foundational (T003–T034)
3. Complete Phase 3: User Story 1 (T035–T045)
4. **STOP and VALIDATE**: Reload integration, verify tyre/maintenance/telematics entities appear
5. Deploy/test with real vehicle

### Incremental Delivery

1. Phase 1 + Phase 2 → Foundation ready
2. Add US1 (Phase 3) → Tyre, maintenance, vehicle state → Test → **MVP!**
3. Add US2 (Phase 4) → Charging & climate schedules → Test
4. Add US3 (Phase 5) → Trip journal & distance → Test
5. Add US4 (Phase 6) → Accessories (fridge, fragrance, locker) → Test
6. Add US5 (Phase 7) → VTM & geofences → Test
7. Phase 10 → Polish & validate all entities
8. Each story adds value without breaking previous stories
