# Tasks: API Command Controls

**Input**: Design documents from `/specs/003-api-command-controls/`
**Prerequisites**: plan.md (required), spec.md (required for user stories), research.md, data-model.md, contracts/smart-api-commands.md, quickstart.md

**Tests**: Not explicitly requested in the feature specification. Test tasks are omitted.

**Organization**: Tasks are grouped by user story to enable independent implementation and testing of each story.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (e.g., US1, US2, US3)
- Include exact file paths in descriptions

---

## Phase 1: Setup

**Purpose**: Project initialization — add new platform registrations, constants, and model foundations

- [x] T001 Add service ID constants (`SERVICE_ID_DOOR_LOCK`, `SERVICE_ID_DOOR_UNLOCK`, `SERVICE_ID_CLIMATE`, `SERVICE_ID_CHARGING`, `SERVICE_ID_HORN_LIGHT`, `SERVICE_ID_WINDOW_SET`, `SERVICE_ID_FRIDGE`, `SERVICE_ID_SEAT_HEAT`), `COMMAND_COOLDOWN_SECONDS = 5`, and `API_TELEMATICS_URL` command path constant in `custom_components/hello_smart/const.py`
- [x] T002 [P] Add `CommandResult` dataclass and `ServiceId` string enum to `custom_components/hello_smart/models.py`
- [x] T003 [P] Add `last_command_time: datetime | None = None` field to `VehicleData` dataclass in `custom_components/hello_smart/models.py`
- [x] T004 Add `Platform.LOCK`, `Platform.CLIMATE`, `Platform.SWITCH`, `Platform.BUTTON`, `Platform.NUMBER`, `Platform.TIME` to the `PLATFORMS` list in `custom_components/hello_smart/__init__.py`

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Core command infrastructure that ALL user stories depend on — the PUT transport, orchestrator, and payload builder

**⚠️ CRITICAL**: No user story platform work can begin until this phase is complete

- [x] T005 Add `async_send_command(self, vin: str, payload: dict) -> CommandResult` method to `SmartAPI` in `custom_components/hello_smart/api.py` — sends PUT to `/remote-control/vehicle/telematics/{vin}` with HMAC-signed headers including the JSON body, serialized with no spaces via `json.dumps(payload, separators=(",", ":"))`. Returns `CommandResult` based on success/failure response. Handle token expiry (1402) with re-auth retry.
- [x] T006 Add `async_send_vehicle_command(self, vin: str, service_id: str, command: str, service_parameters: list[dict], duration: int = 6) -> CommandResult` orchestrator method to `SmartDataCoordinator` in `custom_components/hello_smart/coordinator.py` — enforces per-VIN cooldown (5s), calls `async_select_vehicle()`, builds the standard payload envelope (creator, command, serviceId, timestamp, operationScheduling, serviceParameters), calls `api.async_send_command()`, and schedules a delayed `async_request_refresh()` 8 seconds after success. Raises `HomeAssistantError` on cooldown violation or command failure.
- [x] T007 [P] Add `async_set_charging_reservation(self, vin: str, data: dict) -> CommandResult` method to `SmartAPI` in `custom_components/hello_smart/api.py` — sends PUT to `/remote-control/charging/reservation/{vin}` with signed headers and JSON body
- [x] T008 [P] Add `async_set_climate_schedule(self, vin: str, data: dict) -> CommandResult` method to `SmartAPI` in `custom_components/hello_smart/api.py` — sends PUT to `/remote-control/schedule/{vin}` with signed headers and JSON body

**Checkpoint**: Command infrastructure ready — platform files can now be created

---

## Phase 3: User Story 1 — Door Lock and Unlock Control (Priority: P1) 🎯 MVP

**Goal**: Provide a lock entity for vehicle door lock/unlock with optimistic updates and dynamic visibility

**Independent Test**: From the HA UI, tap "Unlock" on the vehicle lock entity. Verify the entity optimistically switches to "unlocked" immediately, then confirm the vehicle's doors actually unlock within 15 seconds. Repeat with "Lock" and verify the reverse.

### Implementation for User Story 1

- [x] T009 [US1] Create `custom_components/hello_smart/lock.py` with `SmartLockEntityDescription` dataclass (extending `EntityDescription` with `lock_fn`, `unlock_fn`, `is_locked_fn`, `available_fn`), `SmartLock` entity class (extending `CoordinatorEntity` and `LockEntity`), and `async_setup_entry()` that registers a door lock entity per vehicle. The `SmartLock.async_lock()` calls `coordinator.async_send_vehicle_command(vin, SERVICE_ID_DOOR_LOCK, "start", [])`, optimistically sets door state to locked, and calls `self.async_write_ha_state()`. The `async_unlock()` does the same with `SERVICE_ID_DOOR_UNLOCK`. The `is_locked` property reads from `coordinator.data[vin].status.doors`. Entity is only created when `coordinator.data[vin].status` is not None and door data is available.
- [x] T010 [US1] Add translation keys for the door lock entity (`lock.smart_door_lock`) in `custom_components/hello_smart/strings.json` and `custom_components/hello_smart/translations/en.json`

**Checkpoint**: Door lock/unlock works end-to-end. This validates the full command pipeline (cooldown → select vehicle → build payload → PUT → optimistic update → delayed refresh).

---

## Phase 4: User Story 2 — Climate Pre-Conditioning Start and Stop (Priority: P2)

**Goal**: Provide a climate entity for starting/stopping climate pre-conditioning with target temperature control

**Independent Test**: Set the climate entity to 22°C and turn it on. Verify the vehicle starts pre-conditioning within 15 seconds. Turn it off and verify the vehicle stops.

### Implementation for User Story 2

- [x] T011 [US2] Create `custom_components/hello_smart/climate.py` with `SmartClimate` entity class (extending `CoordinatorEntity` and `ClimateEntity`). Supports `HVACMode.HEAT_COOL` and `HVACMode.OFF`. `async_set_hvac_mode()` sends start/stop command via `coordinator.async_send_vehicle_command(vin, SERVICE_ID_CLIMATE, "start"/"stop", service_parameters)` where service_parameters include `[{"key": "rce.conditioner", "value": "1"}, {"key": "rce.temp", "value": "<temp>"}]`. Uses `operationScheduling.duration` of 180. `async_set_temperature()` updates the target temp and restarts climate if active. Temperature clamped to 16–30°C via `min_temp`/`max_temp` properties. `hvac_mode` reads from `coordinator.data[vin].status.climate_active`. `async_setup_entry()` registers one climate entity per vehicle. Entity only created when climate data is available from telematics.
- [x] T012 [US2] Add translation keys for the climate entity (`climate.smart_climate`) in `custom_components/hello_smart/strings.json` and `custom_components/hello_smart/translations/en.json`

**Checkpoint**: Climate pre-conditioning start/stop with temperature control works independently.

---

## Phase 5: User Story 3 — Charging Start, Stop, and Target SOC (Priority: P3)

**Goal**: Provide a charging switch and target SOC number slider for charging control

**Independent Test**: Toggle the charging switch to "on" and verify charging begins. Adjust the target SOC slider to 80% and verify the update.

### Implementation for User Story 3

- [x] T013 [US3] Create `custom_components/hello_smart/switch.py` with `SmartSwitchEntityDescription` dataclass (extending `SwitchEntityDescription` with `turn_on_fn`, `turn_off_fn`, `is_on_fn`, `available_fn`), `SmartSwitch` entity class (extending `CoordinatorEntity` and `SwitchEntity`), and `async_setup_entry()`. Add the charging switch entity description: `async_turn_on()` calls `coordinator.async_send_vehicle_command(vin, SERVICE_ID_CHARGING, "start", [{"key": "operation", "value": "1"}, {"key": "rcs.restart", "value": "1"}])` with duration=6 and NOTE: charging uses `timeStamp` (capital S) and `command` is always `"start"` even for stop. `async_turn_off()` sends `[{"key": "operation", "value": "0"}, {"key": "rcs.terminate", "value": "1"}]`. `is_on` reads from `coordinator.data[vin].status.charging_state`. Entity only created when charging data is available.
- [x] T014 [P] [US3] Create `custom_components/hello_smart/number.py` with `SmartNumber` entity class (extending `CoordinatorEntity` and `NumberEntity`). Add target SOC entity with `native_min_value=50`, `native_max_value=100`, `native_step=5`, `native_unit_of_measurement="%"`. `async_set_native_value()` calls `api.async_set_charging_reservation(vin, {"targetSoc": int(value)})` via the coordinator. `native_value` reads from `coordinator.data[vin].charging_reservation.target_soc`. Entity only created when `charging_reservation` is not None.
- [x] T015 [US3] Add translation keys for charging switch (`switch.smart_charging`) and target SOC (`number.smart_target_soc`) in `custom_components/hello_smart/strings.json` and `custom_components/hello_smart/translations/en.json`

**Checkpoint**: Charging start/stop and target SOC control work independently.

---

## Phase 6: User Story 4 — Horn, Flash Lights, and Find My Car (Priority: P4)

**Goal**: Provide momentary button entities for horn, flash lights, and find-my-car

**Independent Test**: Press the "Horn" button and verify the vehicle honks. Press "Flash Lights" and verify lights flash. Press "Find My Car" and verify both occur.

### Implementation for User Story 4

- [x] T016 [US4] Create `custom_components/hello_smart/button.py` with `SmartButtonEntityDescription` dataclass (extending `ButtonEntityDescription` with `press_fn`), `SmartButton` entity class (extending `CoordinatorEntity` and `ButtonEntity`), and `async_setup_entry()`. Add three entity descriptions: Horn (`async_press()` sends `SERVICE_ID_HORN_LIGHT` with `[{"key": "rhl.horn", "value": "1"}]`), Flash Lights (`[{"key": "rhl.flash", "value": "1"}]`), and Find My Car (`[{"key": "rhl.horn", "value": "1"}, {"key": "rhl.flash", "value": "1"}]`). All use `command="start"`, `duration=6`. Button entities are always created for configured vehicles (horn/flash are universally supported).
- [x] T017 [US4] Add translation keys for horn (`button.smart_horn`), flash lights (`button.smart_flash_lights`), and find my car (`button.smart_find_my_car`) in `custom_components/hello_smart/strings.json` and `custom_components/hello_smart/translations/en.json`

**Checkpoint**: Horn, flash, and find-my-car buttons work independently.

---

## Phase 7: User Story 5 — Accessory Controls: Fridge, Fragrance, and Locker (Priority: P5)

**Goal**: Provide switch entities for fridge and fragrance, and a lock entity for the trunk locker — only for vehicles with those accessories

**Independent Test**: For a vehicle with a mini-fridge, toggle the fridge switch to "on" and verify the fridge activates. For a vehicle without a fridge, verify no fridge switch entity exists.

### Implementation for User Story 5

- [x] T018 [US5] Add fridge switch entity description to `custom_components/hello_smart/switch.py`: `async_turn_on()` sends `SERVICE_ID_FRIDGE` with `[{"key": "ufr.status", "value": "1"}]`, `async_turn_off()` sends `[{"key": "ufr.status", "value": "0"}]`. `is_on` reads from `coordinator.data[vin].fridge.active`. Entity only created when `coordinator.data[vin].fridge` is not None.
- [x] T019 [P] [US5] Add fragrance switch entity description to `custom_components/hello_smart/switch.py`: toggle the fragrance diffuser on/off. `is_on` reads from `coordinator.data[vin].fragrance.active`. Entity only created when `coordinator.data[vin].fragrance` is not None.
- [x] T020 [P] [US5] Add trunk locker lock entity description to `custom_components/hello_smart/lock.py`: lock/unlock the front trunk locker. `is_locked` reads from `coordinator.data[vin].locker.locked`. Entity only created when `coordinator.data[vin].locker` is not None.
- [x] T021 [US5] Add translation keys for fridge switch (`switch.smart_fridge`), fragrance switch (`switch.smart_fragrance`), and trunk locker lock (`lock.smart_trunk_locker`) in `custom_components/hello_smart/strings.json` and `custom_components/hello_smart/translations/en.json`

**Checkpoint**: Accessory entities appear only for vehicles with the relevant hardware and respond to commands.

---

## Phase 8: User Story 6 — Window Close Command (Priority: P6)

**Goal**: Provide a close-windows button entity (close-only for safety — no remote open)

**Independent Test**: With a window open, press the "Close Windows" button and verify all windows close within 30 seconds.

### Implementation for User Story 6

- [x] T022 [US6] Add close-windows button entity description to `custom_components/hello_smart/button.py`: `async_press()` sends `SERVICE_ID_WINDOW_SET` with `[{"key": "rws.close", "value": "1"}]`, `command="start"`, `duration=6`. No "Open Windows" entity is ever created (FR-061). Entity is always created for configured vehicles.
- [x] T023 [US6] Add translation key for close windows button (`button.smart_close_windows`) in `custom_components/hello_smart/strings.json` and `custom_components/hello_smart/translations/en.json`

**Checkpoint**: Close-windows button works. No open-windows entity exists anywhere (verify FR-061 safety requirement).

---

## Phase 9: User Story 7 — Vehicle Theft Monitoring Toggle (Priority: P7)

**Goal**: Provide a VTM switch entity to enable/disable Vehicle Theft Monitoring

**Independent Test**: Toggle the VTM switch to "on" and verify the VTM GET endpoint reflects the change on the next poll.

### Implementation for User Story 7

- [x] T024 [US7] Add VTM switch entity description to `custom_components/hello_smart/switch.py`: toggle VTM enabled/disabled via the telematics command endpoint. `is_on` reads from `coordinator.data[vin].vtm.enabled`. Entity only created when `coordinator.data[vin].vtm` is not None.
- [x] T025 [US7] Add translation key for VTM switch (`switch.smart_vtm`) in `custom_components/hello_smart/strings.json` and `custom_components/hello_smart/translations/en.json`

**Checkpoint**: VTM switch works independently.

---

## Phase 10: User Story 8 — Charging and Climate Schedule Configuration (Priority: P8)

**Goal**: Provide time-picker entities for charging schedule and climate schedule, plus a climate schedule on/off switch

**Independent Test**: Set the charging start time to 22:00 via the time entity and verify the charging reservation reflects the new time on the next poll.

### Implementation for User Story 8

- [x] T026 [US8] Create `custom_components/hello_smart/time.py` with `SmartTimeEntityDescription` dataclass (extending `TimeEntityDescription` with `set_value_fn`, `native_value_fn`, `available_fn`), `SmartTime` entity class (extending `CoordinatorEntity` and `TimeEntity`), and `async_setup_entry()`. Add three entity descriptions: charging start time (`async_set_value()` calls `api.async_set_charging_reservation(vin, {"startTime": value})`, reads from `coordinator.data[vin].charging_reservation.start_time`), charging end time (reads from `end_time`), and climate schedule time (`async_set_value()` calls `api.async_set_climate_schedule(vin, {"scheduledTime": value})`, reads from `coordinator.data[vin].climate_schedule.scheduled_time`). Entities only created when corresponding reservation/schedule data is not None.
- [x] T027 [P] [US8] Add climate schedule switch entity description to `custom_components/hello_smart/switch.py`: toggle the climate schedule enabled/disabled via `api.async_set_climate_schedule(vin, {"enabled": True/False})`. `is_on` reads from `coordinator.data[vin].climate_schedule.enabled`. Entity only created when `coordinator.data[vin].climate_schedule` is not None.
- [x] T028 [US8] Add translation keys for charging start time (`time.smart_charging_start`), charging end time (`time.smart_charging_end`), climate schedule time (`time.smart_climate_schedule_time`), and climate schedule switch (`switch.smart_climate_schedule`) in `custom_components/hello_smart/strings.json` and `custom_components/hello_smart/translations/en.json`

**Checkpoint**: Schedule time pickers and climate schedule toggle work independently.

---

## Phase 11: Polish & Cross-Cutting Concerns

**Purpose**: Final validation and improvements that affect multiple user stories

- [x] T029 Verify all command entities have correct `device_info` linking them to the vehicle device — ensure they group under the same HA device as existing sensor/binary_sensor entities in `custom_components/hello_smart/coordinator.py`
- [x] T030 [P] Verify dynamic entity visibility across all platforms — load integration with a vehicle missing fridge, fragrance, locker, VTM, and schedules; confirm zero entities are created for missing features
- [x] T031 [P] Verify no "Open Windows" entity or action exists anywhere in the codebase (FR-061 safety audit)
- [x] T032 Add any new command-related URL paths to `URL_ALLOWLIST` in `custom_components/hello_smart/const.py` if `/remote-control/vehicle/telematics/` is not already covered by existing allowlist patterns
- [x] T033 Run `quickstart.md` validation — walk through the architecture flow end-to-end with one command (e.g., door lock) and verify each step matches the documented flow

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: No dependencies — can start immediately
- **Foundational (Phase 2)**: Depends on Setup completion — BLOCKS all user stories
- **User Stories (Phases 3–10)**: All depend on Foundational phase completion
  - User stories can proceed in parallel (if staffed) — they modify different files
  - Or sequentially in priority order (P1 → P2 → … → P8)
- **Polish (Phase 11)**: Depends on all user stories being complete

### User Story Dependencies

- **US1 (P1 — Door Lock)**: Can start after Foundational (Phase 2) — creates `lock.py`
- **US2 (P2 — Climate)**: Can start after Foundational (Phase 2) — creates `climate.py`. No dependency on US1.
- **US3 (P3 — Charging)**: Can start after Foundational (Phase 2) — creates `switch.py` and `number.py`. No dependency on US1/US2.
- **US4 (P4 — Horn/Flash)**: Can start after Foundational (Phase 2) — creates `button.py`. No dependency on prior stories.
- **US5 (P5 — Accessories)**: Depends on US1 (adds to `lock.py`) and US3 (adds to `switch.py`). Must follow Phases 3 and 5.
- **US6 (P6 — Window Close)**: Depends on US4 (adds to `button.py`). Must follow Phase 6.
- **US7 (P7 — VTM)**: Depends on US3 (adds to `switch.py`). Must follow Phase 5.
- **US8 (P8 — Schedules)**: Depends on US3 (adds to `switch.py`) and creates `time.py`. Must follow Phase 5.

### Within Each User Story

- Entity platform file created/modified first
- Translation keys added after entity file is ready
- Optimistic update logic inline within the entity class (not separated)

### Parallel Opportunities

- T002 and T003 can run in parallel (both modify `models.py` but different sections)
- T007 and T008 can run in parallel (both add methods to `api.py` but independent)
- US1 (lock.py), US2 (climate.py), US3 (switch.py + number.py), and US4 (button.py) can all run in parallel after Phase 2 — they create different files
- T018, T019, T020 within US5 can run in parallel — they add to existing files in independent sections
- T026 and T027 within US8 can run in parallel — they modify different files
- T029, T030, T031 in Polish can run in parallel

---

## Parallel Example: After Phase 2 Completes

```bash
# All four MVP stories can launch simultaneously:
Task: T009 — Create lock.py (US1)
Task: T011 — Create climate.py (US2)
Task: T013 — Create switch.py with charging (US3)
Task: T016 — Create button.py with horn/flash/find (US4)

# Once US1 and US3 are done, US5 can start:
Task: T018 — Add fridge switch to switch.py (US5)
Task: T020 — Add locker lock to lock.py (US5)
```

---

## Implementation Strategy

### MVP First (User Story 1 Only)

1. Complete Phase 1: Setup (T001–T004)
2. Complete Phase 2: Foundational (T005–T008)
3. Complete Phase 3: User Story 1 — Door Lock (T009–T010)
4. **STOP and VALIDATE**: Test door lock/unlock end-to-end
5. Deploy/demo if ready — this alone provides high user value

### Incremental Delivery

1. Setup + Foundational → Command infrastructure ready
2. Add US1 (Door Lock) → Test independently → **MVP Release**
3. Add US2 (Climate) → Test independently → Release
4. Add US3 (Charging + SOC) → Test independently → Release
5. Add US4 (Horn/Flash/Find) → Test independently → Release
6. Add US5–US8 → Test each → Release
7. Polish phase → Final release

### Parallel Strategy

With capacity for parallel work:

1. Complete Setup + Foundational together
2. Once Foundational is done:
   - Stream A: US1 (lock.py) → US5 adds to lock.py
   - Stream B: US2 (climate.py)
   - Stream C: US3 (switch.py, number.py) → US5/US7/US8 add to switch.py
   - Stream D: US4 (button.py) → US6 adds to button.py
3. All streams merge at Polish phase

---

## Notes

- Charging payload has quirks: `serviceId` is lowercase `"rcs"`, timestamp field is `"timeStamp"` (capital S), and `command` is always `"start"` even for stop — see contract C-004
- JSON body must be serialized with no spaces: `json.dumps(payload, separators=(",", ":"))`
- `async_select_vehicle(vin)` must precede every command PUT call
- Command response may return `{"success": true}` directly OR wrapped in `{"code": 1000, "data": {"success": true}}` — handle both in T005
- Horn/flash/find service parameters use inferred key names (`rhl.horn`, `rhl.flash`) — verify during implementation of T016
- Window close and fridge/fragrance/VTM payloads are low-confidence (see contracts C-006, C-007) — verify during implementation
- All entity platforms follow the same pattern: `SmartXxxEntityDescription` dataclass → `SmartXxx(CoordinatorEntity, XxxEntity)` class → `async_setup_entry()` function
