# Tasks: Capability-Based Entity Filtering

**Input**: Design documents from `/specs/006-capability-entity-filtering/`
**Prerequisites**: plan.md, spec.md, research.md, data-model.md, contracts/

**Tests**: Not explicitly requested in the feature specification. Omitted per SpecKit convention.

**Organization**: Tasks are grouped by user story to enable independent implementation and testing of each story.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (e.g., US1, US2, US3)
- Include exact file paths in descriptions

## Phase 1: Setup

**Purpose**: Foundation data model changes and function ID constants needed by all user stories

- [x] T001 Add `capability_flags: dict[str, bool]` field to `VehicleCapabilities` dataclass in `custom_components/hello_smart/models.py`
- [x] T002 Add `StaticVehicleData` dataclass with `capabilities`, `ability`, and `plant_no` fields in `custom_components/hello_smart/models.py`
- [x] T003 [P] Add `FUNCTION_ID_*` constants to `custom_components/hello_smart/const.py` (24 constants from data-model.md mapping: `FUNCTION_ID_REMOTE_LOCK`, `FUNCTION_ID_REMOTE_UNLOCK`, `FUNCTION_ID_CLIMATE`, `FUNCTION_ID_WINDOW_CLOSE`, `FUNCTION_ID_WINDOW_OPEN`, `FUNCTION_ID_TRUNK_OPEN`, `FUNCTION_ID_HONK_FLASH`, `FUNCTION_ID_SEAT_HEAT`, `FUNCTION_ID_SEAT_VENT`, `FUNCTION_ID_FRAGRANCE`, `FUNCTION_ID_CHARGING`, `FUNCTION_ID_DOOR_STATUS`, `FUNCTION_ID_TRUNK_STATUS`, `FUNCTION_ID_WINDOW_STATUS`, `FUNCTION_ID_SKYLIGHT_STATUS`, `FUNCTION_ID_TYRE_PRESSURE`, `FUNCTION_ID_VEHICLE_POSITION`, `FUNCTION_ID_TOTAL_MILEAGE`, `FUNCTION_ID_HOOD_STATUS`, `FUNCTION_ID_CHARGE_PORT_STATUS`, `FUNCTION_ID_CURTAIN_STATUS`, `FUNCTION_ID_DOORS_STATUS`, `FUNCTION_ID_CLIMATE_STATUS`, `FUNCTION_ID_CHARGING_RESERVATION`)

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Update the capability API parser and coordinator caching — MUST complete before entity platform work begins

**⚠️ CRITICAL**: All user story phases depend on these tasks

- [x] T004 Update `async_get_capabilities()` in `custom_components/hello_smart/api.py` to parse `functionId`/`valueEnable` from `data.list[]` (APK model format), falling back to `data.capabilities[]` with `serviceId`/`enabled` (legacy format). Populate both `capability_flags` dict and `service_ids` list on the returned `VehicleCapabilities`. Log raw response structure at debug level on first call to verify schema (see research.md Topic 1 and contracts/capability-api-response.md)
- [x] T005 Add `_static_cache: dict[str, StaticVehicleData]` instance variable to `SmartDataCoordinator.__init__()` in `custom_components/hello_smart/coordinator.py`. Modify `_async_fetch_all_vehicles()` to check `_static_cache[vin]` before calling `async_get_capabilities()`, `async_get_vehicle_ability()`, and `async_get_plant_no()`. On first fetch, store results in cache. On subsequent polls, use cached values. Build `VehicleData` using cached `capabilities`, `ability`, and `plant_no` instead of re-fetched values

**Checkpoint**: Capability flags are parsed and cached. Entity platforms can now be updated.

---

## Phase 3: User Story 1 — Only See Entities My Vehicle Supports (Priority: P1) 🎯 MVP

**Goal**: Filter read-only sensor and binary sensor entities based on vehicle capability flags so phantom entities are eliminated

**Independent Test**: Configure integration with a vehicle lacking certain features and verify only supported entities are created. Compare entity counts with a fully-capable vehicle to confirm zero regression.

### Implementation for User Story 1

- [x] T006 [P] [US1] Add `required_capability: str | None = None` field to `SmartSensorEntityDescription` dataclass in `custom_components/hello_smart/sensor.py`. Add capability filtering logic to `async_setup_entry()`: for each description with a non-None `required_capability`, check `vehicle_data.capabilities.capability_flags.get(required_capability, True)` — skip entity if `False`. Log skipped entities at debug level and total filtered count at info level per contracts/entity-filtering.md
- [x] T007 [P] [US1] Add `required_capability: str | None = None` field to `SmartBinarySensorEntityDescription` dataclass in `custom_components/hello_smart/binary_sensor.py`. Add the same capability filtering logic to `async_setup_entry()` as in T006
- [x] T008 [US1] Assign `required_capability` values to sensor entity descriptions in `custom_components/hello_smart/sensor.py` using `FUNCTION_ID_*` constants from const.py. Map: tyre pressure sensors → `FUNCTION_ID_TYRE_PRESSURE`, charging sensors (voltage, current, time_to_full, charging_status) → `FUNCTION_ID_CHARGING`, seat heat sensors → `FUNCTION_ID_SEAT_HEAT`, seat ventilation sensors → `FUNCTION_ID_SEAT_VENT`, odometer → `FUNCTION_ID_TOTAL_MILEAGE`. Leave all other sensors as `required_capability=None` (always created)
- [x] T009 [US1] Assign `required_capability` values to binary sensor entity descriptions in `custom_components/hello_smart/binary_sensor.py` using constants from const.py. Map: door lock status → `FUNCTION_ID_DOOR_STATUS`, trunk status → `FUNCTION_ID_TRUNK_STATUS`, window statuses → `FUNCTION_ID_WINDOW_STATUS`, sunroof/skylight → `FUNCTION_ID_SKYLIGHT_STATUS`, hood → `FUNCTION_ID_HOOD_STATUS`, charge port → `FUNCTION_ID_CHARGE_PORT_STATUS`, curtain → `FUNCTION_ID_CURTAIN_STATUS`, individual doors → `FUNCTION_ID_DOORS_STATUS`. Leave all other binary sensors as `required_capability=None`

**Checkpoint**: Sensor and binary_sensor entities are filtered by capability. A vehicle missing features shows no phantom read-only entities. Vehicles with all features show identical entity counts (zero regression).

---

## Phase 4: User Story 2 — Command Controls Respect Capabilities (Priority: P2)

**Goal**: Filter command-based entities (lock, climate, buttons, switches, selects) based on capability flags so unsupported commands are never exposed

**Independent Test**: Verify that a vehicle missing window control capability has no window button entities, while lock/climate still work for vehicles with those capabilities.

### Implementation for User Story 2

- [x] T010 [P] [US2] Add `required_capability: str | None = None` field to `SmartLockEntityDescription` dataclass in `custom_components/hello_smart/lock.py`. Add capability filtering logic to `async_setup_entry()` (before the existing `available_fn` check). Assign `required_capability=FUNCTION_ID_REMOTE_LOCK` to the lock entity description
- [x] T011 [P] [US2] Add `required_capability: str | None = None` field to `SmartSwitchEntityDescription` dataclass in `custom_components/hello_smart/switch.py`. Add capability filtering logic to `async_setup_entry()` (before the existing `available_fn` check). Assign `required_capability` to switch descriptions: fragrance → `FUNCTION_ID_FRAGRANCE`, charging schedule switch → `FUNCTION_ID_CHARGING_RESERVATION`. Leave fridge switch as `required_capability=None` (fridge uses existing `available_fn` pattern per research.md Topic 5)
- [x] T012 [P] [US2] Add `required_capability: str | None = None` field to `SmartButtonEntityDescription` dataclass in `custom_components/hello_smart/button.py`. Add capability filtering logic to `async_setup_entry()`. Assign: window close → `FUNCTION_ID_WINDOW_CLOSE`, window open → `FUNCTION_ID_WINDOW_OPEN`, trunk open → `FUNCTION_ID_TRUNK_OPEN`, horn/flash → `FUNCTION_ID_HONK_FLASH`
- [x] T013 [P] [US2] Add `required_capability: str | None = None` field to `SmartSelectEntityDescription` dataclass in `custom_components/hello_smart/select.py`. Add capability filtering logic to `async_setup_entry()`. Assign: seat heating level → `FUNCTION_ID_SEAT_HEAT`, seat ventilation → `FUNCTION_ID_SEAT_VENT`
- [x] T014 [US2] Add capability check to `async_setup_entry()` in `custom_components/hello_smart/climate.py` before creating the climate entity. Check `vehicle_data.capabilities.capability_flags.get(FUNCTION_ID_CLIMATE, True)` — skip if `False`. Import `FUNCTION_ID_CLIMATE` from const
- [x] T015 [US2] Add `required_capability: str | None = None` field to entity descriptions in `custom_components/hello_smart/number.py` and `custom_components/hello_smart/time.py`. Add capability filtering logic to their `async_setup_entry()` functions. Assign `required_capability` values where applicable (charging schedule time → `FUNCTION_ID_CHARGING_RESERVATION`). Leave others as `None`

**Checkpoint**: All command-based entities are filtered by capability. Unsupported remote operations no longer appear as HA entities.

---

## Phase 5: User Story 3 — Reduced API Calls for Static Data (Priority: P3)

**Goal**: Verify caching is working correctly by deploying to dev container and confirming static data endpoints are only called once

**Independent Test**: Monitor API call logs across multiple poll cycles — capability, vehicle ability, and plant number endpoints should appear only on first poll.

### Implementation for User Story 3

- [x] T016 [US3] Deploy to dev container and capture debug logs across 3+ poll cycles. Verify: (1) capability endpoint called exactly once per VIN on first poll, (2) vehicle ability endpoint called exactly once per VIN on first poll, (3) plant number endpoint called exactly once per VIN on first poll, (4) none of the three endpoints called on subsequent polls. Log the raw capability API response to verify the response schema matches `data.list[]` format from contracts/capability-api-response.md. If the response uses a different format, update `async_get_capabilities()` in `custom_components/hello_smart/api.py` accordingly

**Checkpoint**: API call reduction confirmed. 3 fewer API calls per poll cycle per vehicle.

---

## Phase 6: User Story 4 — Accurate API Documentation (Priority: P4)

**Goal**: Update API documentation to reflect actual capability response structure and entity-to-capability mappings

**Independent Test**: Review documentation files and confirm they contain full capability response schema, function ID mappings, and entity-capability relationships.

### Implementation for User Story 4

- [x] T017 [P] [US4] Update `API/endpoints/capabilities.md`: replace the speculative `serviceId`/`enabled`/`version` response schema with the actual `functionId`/`valueEnable` schema from `Capability.java`. Include full field reference table (functionId, valueEnable, functionCategory, name, showType, tips, valueEnum, valueRange, paramsJson, configCode, platform, priority). Add note about dual-format parsing (primary `data.list[]`, fallback `data.capabilities[]`). Update the Data Model section to reference the enhanced `VehicleCapabilities` with `capability_flags`
- [x] T018 [P] [US4] Update `API/entities.md`: add a `Required Capability` column to all entity tables (Sensors, Binary Sensors, Switches, Locks, Buttons, Selects, Climate, Number, Time). Populate with the corresponding `FUNCTION_ID_*` value or "—" for entities with no capability requirement. Add a note explaining that entities without a required capability are always created
- [x] T019 [P] [US4] Update `API/models.md`: add `capability_flags: dict[str, bool]` field to the `VehicleCapabilities` model documentation. Add the new `StaticVehicleData` model with its three fields. Update any references to the old `VehicleCapabilities` model to note both `service_ids` (backward compat) and `capability_flags` (new)

**Checkpoint**: Documentation accurately reflects the implementation. Contributors can look up capability requirements for any entity.

---

## Phase 7: Polish & Cross-Cutting Concerns

**Purpose**: Final validation and cleanup

- [x] T020 Verify zero regression by comparing full entity list for a vehicle with all features enabled against the entity list from the previous integration version. Confirm identical entity count and identical entity keys
- [x] T021 Run quickstart.md validation steps: deploy to dev container, check logs for capability parsing output, verify filtered entity counts match expectations

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: No dependencies — can start immediately
- **Foundational (Phase 2)**: Depends on Phase 1 completion (needs models and constants) — BLOCKS all user stories
- **US1 (Phase 3)**: Depends on Phase 2 — sensor/binary_sensor filtering
- **US2 (Phase 4)**: Depends on Phase 2 — command entity filtering (can run in parallel with US1)
- **US3 (Phase 5)**: Depends on Phases 2 + 3 or 4 — deployment verification
- **US4 (Phase 6)**: Depends on Phase 2 — documentation (can run in parallel with US1/US2)
- **Polish (Phase 7)**: Depends on all prior phases

### Within Each User Story

- Entity description dataclass change before capability assignment
- T006/T007 (dataclass + filtering logic) must complete before T008/T009 (assigning values)
- T010-T013 can all run in parallel (different files)
- T017-T019 can all run in parallel (different doc files)

### Parallel Opportunities

```
Phase 1:  T001, T002 (sequential in same file) + T003 (parallel, different file)
Phase 2:  T004, T005 (sequential — T005 depends on T004's return type)
Phase 3:  T006 ∥ T007 (parallel — different files)
          T008  T009 (after T006, T007 respectively — same files)
Phase 4:  T010 ∥ T011 ∥ T012 ∥ T013 (all parallel — different files)
          T014, T015 (after any of T010-T013, different files, can parallel)
Phase 5:  T016 (sequential — deployment verification)
Phase 6:  T017 ∥ T018 ∥ T019 (all parallel — different doc files)
Phase 7:  T020, T021 (sequential — final validation)
```

---

## Implementation Strategy

**MVP**: Phase 1 + Phase 2 + Phase 3 (User Story 1) — delivers the core value of eliminating phantom entities for read-only sensors and binary sensors.

**Incremental delivery**:
1. MVP (Phases 1-3): Sensor/binary sensor filtering — immediate user-visible improvement
2. +Phase 4 (US2): Command entity filtering — prevents sending unsupported commands
3. +Phase 5 (US3): Cache verification — confirms API call reduction
4. +Phase 6 (US4): Documentation — contributor onboarding improvement
5. +Phase 7: Final validation and cleanup
