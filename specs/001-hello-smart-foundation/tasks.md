# Tasks: Hello-Smart Foundation

**Input**: Design documents from `/specs/001-hello-smart-foundation/`
**Prerequisites**: plan.md (required), spec.md (required for user stories), research.md, data-model.md, contracts/

**Tests**: Not included — tests were not explicitly requested in the feature specification. Test files listed in plan.md can be generated separately via a TDD pass if desired.

**Organization**: Tasks are grouped by user story to enable independent implementation and testing of each story.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (e.g., US1, US2, US3)
- Include exact file paths in descriptions

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Project scaffolding, metadata, constants, and UI strings

- [x] T001 Create project directory structure: `custom_components/hello_smart/`, `tests/`, `tests/helpers/`, `scripts/debug/`
- [x] T002 [P] Create integration manifest in `custom_components/hello_smart/manifest.json` with domain `hello_smart`, name `Hello Smart`, version `0.1.0`, documentation URL, `iot_class: cloud_polling`, `config_flow: true`, and empty `requirements` list (no external deps)
- [x] T003 [P] Create UI strings in `custom_components/hello_smart/strings.json` with config flow steps (user: email/password/region selector EU|INTL), options flow (scan_interval), error messages (invalid_auth, cannot_connect, already_configured), and abort reasons (already_configured)
- [x] T004 [P] Create constants in `custom_components/hello_smart/const.py`: DOMAIN (`hello_smart`), EU/INTL API base URLs (`api.ecloudeu.com`, `apiv2.ecloudeu.com`, `sg-app-api.smart.com`), Gigya API key, INTL X-Ca-Key (`204587190`), EU/INTL HMAC signing secrets (per research.md R3), OTA host (`ota.srv.smart.com`), default scan interval (300s), app IDs (`SmartAPPEU`, `SmartAPPGlobal`, `SMARTAPP-ISRAEL`), operator codes, URL allowlist set, and `SENSITIVE_FIELDS` tuple for redaction

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Core data models, request signing, and API client base that ALL user stories depend on

**⚠️ CRITICAL**: No user story work can begin until this phase is complete

- [x] T005 [P] Create data model dataclasses in `custom_components/hello_smart/models.py`: `Account` (username, region, device_id, tokens, expires_at, state enum), `Vehicle` (vin, model_name, model_year, series_code, base_url), `VehicleStatus` (battery_level, range_remaining, charging_state enum, charger_connected, charge_voltage, charge_current, time_to_full, doors dict, windows dict, climate_active, latitude, longitude, last_updated), `OTAInfo` (current_version, target_version, update_available derived property) — per data-model.md field definitions and validation rules
- [x] T006 [P] Implement HMAC-SHA1 request signing in `custom_components/hello_smart/auth.py`: `compute_signature(method, path, params, body, nonce, timestamp, secret)` function using stdlib `hmac`, `hashlib`, `base64`; `build_signed_headers(method, url, body, account)` function that assembles all required headers (x-app-id, x-operator-code, x-device-identifier, x-api-signature-version, x-api-signature-nonce, x-timestamp, x-signature, authorization Bearer, accept, content-type) with region-aware secret selection — per research.md R3 and contracts/smart-api.md Signing section
- [x] T007 Implement Smart API client class in `custom_components/hello_smart/api.py`: `SmartAPI` class accepting `aiohttp.ClientSession` (from `async_get_clientsession(hass)`), `_signed_request(method, url, body, account)` helper that calls `build_signed_headers`, validates URL against const.py `URL_ALLOWLIST` (FR-015), enforces HTTPS (FR-016), parses JSON response, checks API error codes (1000=success, 1402=token expired, 8006=vehicle not linked per contracts/smart-api.md Error Responses), and handles HTTP 429 rate limiting with `Retry-After` header (FR-023)

**Checkpoint**: Foundation ready — user story implementation can now begin

---

## Phase 3: User Story 1 — INTL Region Setup and Vehicle Discovery (Priority: P1) 🎯 MVP

**Goal**: INTL Smart account owners (Australia, Singapore, Israel, etc.) can add the integration, authenticate, discover vehicles, and see battery/range/charging sensors

**Independent Test**: Configure a real or mocked INTL Smart account → verify vehicles appear as HA devices with battery level, range, and charging status sensor entities

### Implementation for User Story 1

- [x] T008 [P] [US1] Implement INTL authentication flow in `custom_components/hello_smart/auth.py`: `async_login_intl(session, email, password)` method performing the 3-step flow — (1) POST login to `sg-app-api.smart.com/iam/service/api/v1/login` with email/password and X-Ca-Key/X-Ca-Nonce/X-Ca-Timestamp/X-App-Id headers, extract accessToken/idToken/userId, (2) GET authorize at `sg-app-api.smart.com/iam/service/api/v1/oauth20/authorize?accessToken={token}` with Xs-Auth-Token header, extract authCode, (3) POST session exchange to `apiv2.ecloudeu.com/auth/account/session/secure?identity_type=smart-israel` with authCode, obtain api_access_token/api_user_id/clientId — redact credentials in logs (FR-014) — per contracts/smart-api.md INTL endpoints
- [x] T009 [P] [US1] Add vehicle data endpoints to `custom_components/hello_smart/api.py`: `async_get_vehicles(account)` calling GET `/device-platform/user/vehicle/secure?needSharedCar=1&userId={id}` returning list of `Vehicle` objects, `async_select_vehicle(account, vin)` calling POST `/device-platform/user/session/update` with vehicle VIN (required before status fetch for multi-vehicle accounts per contracts/smart-api.md), `async_get_vehicle_status(account, vin)` calling GET `/remote-control/vehicle/status/{vin}?latest=false&target=basic,more&userId={id}` returning `VehicleStatus` parsed from nested `additionalVehicleStatus` response per contracts/smart-api.md (INTL uses `latest=false` per research.md R6)
- [x] T010 [US1] Implement config flow in `custom_components/hello_smart/config_flow.py`: `SmartConfigFlow` subclass of `ConfigFlow` with DOMAIN, `async_step_user` showing form (email, password, region vol_schema), `async_step_validate` calling `async_login_intl` or `async_login_eu` based on region, on success create config entry with title=email storing encrypted credentials+region+tokens, detect duplicate accounts by `unique_id` = `{email}_{region}` and abort with `already_configured` (FR-020), return `invalid_auth` error on credential failure, `cannot_connect` on network error; set INTL device_id length (32 chars)
- [x] T011 [US1] Implement DataUpdateCoordinator in `custom_components/hello_smart/coordinator.py`: `SmartDataCoordinator` subclass of `DataUpdateCoordinator[dict[str, VehicleStatus]]`, store `Account` from config entry data, in `_async_update_data`: authenticate if no valid token, call `async_get_vehicles` to discover vehicles, iterate each VIN calling `async_select_vehicle` then `async_get_vehicle_status`, register each vehicle in HA device registry with identifiers=`{(DOMAIN, vin)}` manufacturer=`Smart` model from API, return `{vin: VehicleStatus}` dict — use `update_interval` from config entry options (default from const.py)
- [x] T012 [P] [US1] Implement integration entry setup in `custom_components/hello_smart/__init__.py`: define `PLATFORMS = [Platform.SENSOR]`, `async_setup_entry` creates `SmartDataCoordinator`, calls `await coordinator.async_config_entry_first_refresh()`, stores coordinator in `hass.data[DOMAIN][entry.entry_id]`, forwards to platforms; `async_unload_entry` unloads platforms and removes hass.data entry
- [x] T013 [P] [US1] Implement core sensor entities in `custom_components/hello_smart/sensor.py`: `SmartSensorEntityDescription` extending `SensorEntityDescription` with `value_fn` key, entity descriptions for battery_level (device_class=BATTERY, native_unit=PERCENTAGE), range_remaining (device_class=DISTANCE, native_unit=KILOMETERS), charging_status (device_class=ENUM, options from charging_state mapping in data-model.md); `SmartSensorEntity` base class with `CoordinatorEntity` mixin reading from `coordinator.data[vin]`; `async_setup_entry` creating entities per vehicle per description with unique_id=`{vin}_{key}`

**Checkpoint**: User Story 1 complete — INTL auth, vehicle discovery, and core sensors functional. This is the MVP.

---

## Phase 4: User Story 2 — EU Region Setup and Vehicle Discovery (Priority: P2)

**Goal**: EU market users can authenticate with the Gigya-based EU flow and get identical vehicle entities to INTL users

**Independent Test**: Configure a real or mocked EU Smart account → verify vehicles appear as HA devices with the same entity types as INTL

### Implementation for User Story 2

- [x] T014 [US2] Implement EU authentication flow in `custom_components/hello_smart/auth.py`: `async_login_eu(session, email, password)` method performing the 4-step Gigya flow — (1) GET authorize context from `awsapi.future.smart.com`, extract `context` from redirect Location, (2) POST `accounts.login` to `auth.smart.com` with loginID/password/APIKey, extract `login_token`, (3) GET `authorize/continue` with context+login_token, extract `access_token` from redirect fragment, (4) POST session exchange to `api.ecloudeu.com/auth/account/session/secure` to obtain `api_access_token`/`api_user_id` — handle Gigya error codes (403042=invalid login), redact credentials in all log output (FR-014) — per contracts/smart-api.md EU endpoints
- [x] T015 [US2] Update config flow EU validation path in `custom_components/hello_smart/config_flow.py`: route `async_step_validate` to `async_login_eu` when region=EU, handle EU-specific Gigya error responses, ensure EU vehicle status uses `latest=true` parameter (per research.md R6), set EU-specific device_id length (16 chars)

**Checkpoint**: User Stories 1 and 2 both work — both INTL and EU users can set up the integration

---

## Phase 5: User Story 3 — Periodic Vehicle Status Updates (Priority: P3)

**Goal**: Entities automatically refresh via polling; binary sensors for doors/windows/charging; resilient to auth failures and API outages

**Independent Test**: Verify entity values update after one polling interval; simulate API auth failure and confirm automatic re-auth; simulate API outage and confirm entities marked unavailable then recover

### Implementation for User Story 3

- [x] T016 [P] [US3] Implement binary sensor entities in `custom_components/hello_smart/binary_sensor.py`: entity descriptions for driver_door/passenger_door/rear_left_door/rear_right_door/trunk (device_class=DOOR, is_on from `doors` dict), per-window sensors (device_class=WINDOW, is_on from `windows` dict), charger_connected (device_class=PLUG, is_on from `charger_connected`); `SmartBinarySensorEntity` with `CoordinatorEntity` mixin; `async_setup_entry` creating entities per vehicle; add `Platform.BINARY_SENSOR` to PLATFORMS list in `__init__.py`
- [x] T017 [US3] Add SOC/charging detail endpoint to `custom_components/hello_smart/api.py` (`async_get_soc(account, vin)` calling GET `/remote-control/vehicle/status/soc/{vin}?setting=charging` per contracts/smart-api.md) and add charging detail sensors (charge_voltage device_class=VOLTAGE, charge_current device_class=CURRENT, time_to_full device_class=DURATION) to `custom_components/hello_smart/sensor.py`
- [x] T018 [US3] Add re-authentication, token-expiry detection, and resilience to `custom_components/hello_smart/coordinator.py`: proactive `expires_at` check before requests, catch HTTP 401 and API code 1402 → re-login and retry (FR-012), on persistent auth failure raise `ConfigEntryAuthFailed` to trigger HA re-auth flow (FR-019), on API unreachable mark `last_update_success=False` so entities show unavailable (FR-021), add `_LOGGER` calls with `async_redact_data` for any logged data containing credentials or tokens (FR-014)
- [x] T019 [US3] Add options flow for configurable scan interval to `custom_components/hello_smart/config_flow.py`: `async_step_init` in `SmartOptionsFlowHandler` showing scan_interval input (default 300s, min 60s), wire options update listener in `custom_components/hello_smart/__init__.py` to reload coordinator with new interval

**Checkpoint**: User Stories 1–3 complete — continuous automatic monitoring with binary sensors and self-healing auth

---

## Phase 6: User Story 4 — Vehicle Location Tracking (Priority: P4)

**Goal**: Each vehicle has a device_tracker entity reporting GPS coordinates on the HA map

**Independent Test**: Verify device_tracker entity has valid latitude/longitude; verify entity shows unavailable when GPS data is absent from API response

### Implementation for User Story 4

- [x] T020 [US4] Implement device tracker entity in `custom_components/hello_smart/device_tracker.py`: `SmartDeviceTracker` extending `TrackerEntity` with `CoordinatorEntity` mixin, `latitude`/`longitude` properties reading from `coordinator.data[vin]`, `source_type = SourceType.GPS`, return `None` for lat/lon when GPS data absent (marks entity unavailable per FR-008); `async_setup_entry` creating one tracker per vehicle; add `Platform.DEVICE_TRACKER` to PLATFORMS list in `custom_components/hello_smart/__init__.py`

**Checkpoint**: User Stories 1–4 complete — vehicles trackable on HA map

---

## Phase 7: User Story 5 — OTA Update Information (Priority: P5)

**Goal**: Firmware version sensors and an update-available binary sensor per vehicle

**Independent Test**: Verify current/target firmware sensors display version strings; verify update-available binary sensor is true when versions differ, false when equal

### Implementation for User Story 5

- [x] T021 [US5] Add OTA info endpoint to `custom_components/hello_smart/api.py`: `async_get_ota_info(account, vin)` calling GET `https://ota.srv.smart.com/app/info/{vin}` with `id-token: {device_id}` and `access_token: {access_token}` headers (note: different host, no HMAC signing required per contracts/smart-api.md), returning `OTAInfo` model; integrate OTA fetch into coordinator's `_async_update_data` loop in `custom_components/hello_smart/coordinator.py`
- [x] T022 [P] [US5] Add firmware version sensors to `custom_components/hello_smart/sensor.py`: entity descriptions for current_firmware_version and target_firmware_version (no device_class, string values from `OTAInfo`) per FR-009
- [x] T023 [P] [US5] Add update-available binary sensor to `custom_components/hello_smart/binary_sensor.py`: entity description with device_class=UPDATE, is_on when `ota_info.update_available` is true (target_version != current_version) per FR-010

**Checkpoint**: User Stories 1–5 complete — full vehicle status including firmware information

---

## Phase 8: User Story 6 — Diagnostics Dump (Priority: P6)

**Goal**: Downloadable diagnostics with all sensitive fields redacted

**Independent Test**: Download diagnostics JSON → verify vehicle data is present and all tokens/passwords/user IDs/VINs are replaced with `**REDACTED**`

### Implementation for User Story 6

- [x] T024 [US6] Implement `async_get_config_entry_diagnostics` in `custom_components/hello_smart/diagnostics.py`: import `async_redact_data` from `homeassistant.helpers.redact`, define `TO_REDACT` keys (access_token, refresh_token, api_access_token, api_refresh_token, password, userId, api_user_id, vin, loginID — matching const.py `SENSITIVE_FIELDS`), return dict with `config_entry_data` (redacted), `coordinator_data` (redacted), and `account_state` per FR-022

**Checkpoint**: All 6 user stories complete

---

## Phase 9: Polish & Cross-Cutting Concerns

**Purpose**: Debug tooling and final validation

- [x] T025 [P] Create manual API test script in `scripts/debug/test_smart_api.py`: standalone async script using `aiohttp` to test Smart API connectivity (login EU/INTL, fetch vehicles, fetch status) with command-line args for email/password/region — for developer debugging only, not shipped in production
- [x] T026 Validate integration against `specs/001-hello-smart-foundation/quickstart.md` setup and verification steps: confirm config flow works end-to-end, entities appear in Developer Tools → States, values update after one polling interval, diagnostics download produces redacted output

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: No dependencies — can start immediately
- **Foundational (Phase 2)**: Depends on Setup (Phase 1) — **BLOCKS all user stories**
- **US1 (Phase 3)**: Depends on Foundational (Phase 2) — no dependencies on other stories
- **US2 (Phase 4)**: Depends on Foundational (Phase 2) — builds on auth.py and config_flow.py from US1 (adds EU Gigya flow) but can be tested independently
- **US3 (Phase 5)**: Depends on US1 (Phase 3) — extends coordinator, adds binary sensors and options flow
- **US4 (Phase 6)**: Depends on US1 (Phase 3) — reads GPS from coordinator data
- **US5 (Phase 7)**: Depends on US1 (Phase 3) — adds OTA endpoint and entities
- **US6 (Phase 8)**: Depends on US1 (Phase 3) — reads coordinator and config entry data
- **Polish (Phase 9)**: Depends on all desired user stories being complete

### User Story Dependencies

- **US1 (P1)**: Start after Foundational → delivers MVP (INTL auth)
- **US2 (P2)**: Start after US1 (shares auth.py and config_flow.py files) → adds EU Gigya auth
- **US3 (P3)**: Start after US1 → adds binary sensors, resilience, polling options
- **US4 (P4)**: Start after US1 → can run in parallel with US3 and US5 (independent files)
- **US5 (P5)**: Start after US1 → can run in parallel with US3 and US4 (independent files)
- **US6 (P6)**: Start after US3 (needs coordinator with full data) → short, single-file task

### Within Each User Story

- Models/signing before API client
- API endpoints before coordinator
- Coordinator before entity platforms
- Config flow needs auth but not coordinator
- Entity files (sensor, binary_sensor, device_tracker) are independent of each other

### Parallel Opportunities

**Setup (Phase 1)**: T002, T003, T004 can all run in parallel (independent files)

**Foundational (Phase 2)**: T005 (models.py) and T006 (auth.py signing) can run in parallel; T007 (api.py) depends on both

**US1 (Phase 3)**: T008 (INTL auth) and T009 (API endpoints) can run in parallel; T012 (__init__.py) and T013 (sensor.py) can run in parallel after T011

**After US1**: US3, US4, US5 can proceed in parallel (different primary files):
- US4 (device_tracker.py) is fully independent
- US5 (OTA in api.py + sensor.py + binary_sensor.py) partially overlaps US3 files
- Safest parallel: US4 with either US3 or US5

---

## Parallel Examples

### Phase 1 — All Setup Tasks

```
Parallel batch:
  T002: Create manifest.json
  T003: Create strings.json
  T004: Create const.py
```

### Phase 3 — US1 Implementation

```
Parallel batch 1 (after Foundational):
  T008: INTL auth flow in auth.py
  T009: Vehicle endpoints in api.py

Sequential (after batch 1):
  T010: Config flow in config_flow.py
  T011: Coordinator in coordinator.py

Parallel batch 2 (after T011):
  T012: Integration setup in __init__.py
  T013: Sensor entities in sensor.py
```

### After US1 — Independent Stories

```
Parallel option (after US1 complete):
  US4 (T020): device_tracker.py — fully independent
  US5 (T021-T023): OTA endpoints + sensors — independent files

Sequential after US3:
  US6 (T024): diagnostics.py — needs full coordinator data
```

---

## Implementation Strategy

### MVP First (User Story 1 Only)

1. Complete Phase 1: Setup (T001–T004)
2. Complete Phase 2: Foundational (T005–T007)
3. Complete Phase 3: User Story 1 (T008–T013)
4. **STOP and VALIDATE**: INTL auth works, vehicles discovered, battery/range/charging sensors visible
5. Deploy to HA for testing

### Incremental Delivery

1. Setup + Foundational → Foundation ready
2. US1 → INTL auth + sensors → **MVP** ✅
3. US2 → Add EU Gigya auth → both regions work ✅
4. US3 → Binary sensors + resilience + options → robust monitoring ✅
5. US4 → Location tracking → vehicles on map ✅
6. US5 → OTA info → firmware visibility ✅
7. US6 → Diagnostics → debug support ✅
8. Polish → Debug script + final validation ✅

Each story adds value without breaking previous stories.

---

## Notes

- All HTTP via `async_get_clientsession(hass)` — never create standalone aiohttp sessions
- No `httpx`, `requests`, or other HTTP libraries — aiohttp only (Constitution Principle I)
- Signing secrets are public app identifiers stored in const.py, not user secrets (per research.md R3)
- `config_entry.data` stores credentials; `config_entry.options` stores scan interval
- All entity unique_ids follow `{vin}_{entity_key}` pattern for stable entity registry
- Device identifiers use `{(DOMAIN, vin)}` tuple for HA device registry
- Commit after each task or logical group
- Stop at any checkpoint to validate the story independently
