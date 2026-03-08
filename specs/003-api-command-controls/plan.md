# Implementation Plan: API Command Controls

**Branch**: `003-api-command-controls` | **Date**: 2025-07-24 | **Spec**: [spec.md](spec.md)
**Input**: Feature specification from `/specs/003-api-command-controls/spec.md`

## Summary

Add interactive vehicle command controls to the Hello Smart HA integration by implementing PUT-based commands to the Smart cloud API's telematics endpoint. All commands are multiplexed through a single `PUT /remote-control/vehicle/telematics/{vin}` endpoint with different `serviceId` values. Adds 6 new HA entity platforms (lock, climate, switch, button, number, time) providing ~16 command entities per vehicle. Uses optimistic state updates with delayed refresh, per-vehicle command cooldown, and dynamic entity visibility based on vehicle capabilities. Confirmed command payload structures via pySmartHashtag library cross-reference and APK reverse engineering.

## Technical Context

**Language/Version**: Python 3.13+ (matching Home Assistant Core 2025.x minimum)  
**Primary Dependencies**: `aiohttp` (via HA's `async_get_clientsession`), `homeassistant` core APIs (config_flow, DataUpdateCoordinator, entity platforms, device registry)  
**Storage**: HA `config_entry` for credentials/settings; no new storage needed  
**Testing**: `pytest` with `pytest-homeassistant-custom-component` and `pytest-aiohttp`  
**Target Platform**: Home Assistant Core (any OS — HassOS, Docker, venv)  
**Project Type**: HA custom integration (custom_components)  
**Performance Goals**: Command round-trip (send → confirmed state) <30s for 95th percentile; individual PUT timeout <10s  
**Constraints**: No blocking I/O in event loop; aiohttp only (no httpx/requests); 5s min cooldown between commands per vehicle; HMAC-signed PUT requests  
**Scale/Scope**: Single account per config entry, up to 10 vehicles; ~16 command entities per vehicle (in addition to existing ~45 sensor entities)

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

| Principle | Status | Evidence |
|-----------|--------|----------|
| **I. HA Compatibility** | ✅ PASS | Python 3.13+, asyncio only, aiohttp via HA session, no external deps. Commands use existing `_signed_request` infrastructure. New platforms use standard HA entity platform patterns (`LockEntity`, `ClimateEntity`, `SwitchEntity`, `ButtonEntity`, `NumberEntity`, `TimeEntity`). |
| **II. Security-First** | ✅ PASS | All command URLs validated against `URL_ALLOWLIST`, HTTPS enforced, no hardcoded secrets. HMAC-SHA1 signing covers PUT body. Door unlock uses HA's standard lock platform (requires explicit user intent). Window close only (no remote open). Command cooldown prevents flooding. |
| **III. Minimal Footprint** | ✅ PASS | 6 new platform files in `custom_components/hello_smart/` — required by HA platform architecture (one file per platform type). Modifications to existing `api.py`, `coordinator.py`, `models.py`, `const.py`, `__init__.py`, `strings.json`. No unnecessary abstractions. |
| **IV. Organized Testing** | ✅ PASS | New test files under `tests/` for each new platform. Shared command mock helpers in `tests/helpers/`. Existing test fixtures extended, not duplicated. |
| **V. Simplicity** | ✅ PASS | Commands follow a single pattern: build payload dict → serialize JSON → PUT to telematics endpoint. No factory pattern, no command queue abstraction, no state machine. Payload construction is inline per entity platform. Optimistic updates use HA's built-in `async_write_ha_state()`. |

**Gate result**: PASS — all principles satisfied.

### Post-Phase 1 Re-evaluation

| Principle | Status | Evidence |
|-----------|--------|----------|
| **I. HA Compatibility** | ✅ PASS | All 6 new entity platforms follow HA's documented platform patterns. `ClimateEntity` with `HVACMode`, `LockEntity` with lock/unlock, `SwitchEntity` with on/off, `ButtonEntity` with press, `NumberEntity` with set_native_value, `TimeEntity` with set_value. |
| **II. Security-First** | ✅ PASS | Contract C-001 confirms HMAC signature includes PUT body. All command URLs are within existing allowlist hosts. No new credentials or secrets introduced. |
| **III. Minimal Footprint** | ✅ PASS | 6 new files justified — HA requires one `.py` per platform type. No optional/speculative files. Each file follows the established `SmartXxxEntityDescription` + `SmartXxx` entity class pattern. |
| **IV. Organized Testing** | ✅ PASS | Test structure mirrors production: one test file per platform. Mock command responses use shared fixtures. |
| **V. Simplicity** | ✅ PASS | Data model adds only `CommandResult` dataclass and `ServiceId` enum to `models.py`. `last_command_time` added to `VehicleData` for cooldown. No command queue, no state machine, no pub/sub. |

**Gate result**: PASS — design confirmed compliant.

## Project Structure

### Documentation (this feature)

```text
specs/003-api-command-controls/
├── plan.md              # This file
├── research.md          # Phase 0 output — endpoint discovery & payload research
├── data-model.md        # Phase 1 output — entity models & state transitions
├── quickstart.md        # Phase 1 output — developer quickstart guide
├── contracts/           # Phase 1 output
│   └── smart-api-commands.md  # All command payload contracts
└── tasks.md             # Phase 2 output (/speckit.tasks command)
```

### Source Code (repository root)

```text
custom_components/hello_smart/
├── __init__.py          # MODIFIED: Add LOCK, CLIMATE, SWITCH, BUTTON, NUMBER, TIME to PLATFORMS
├── const.py             # MODIFIED: Add SERVICE_ID_*, COMMAND_COOLDOWN_SECONDS, command URL constants
├── models.py            # MODIFIED: Add CommandResult, ServiceId enum, last_command_time to VehicleData
├── api.py               # MODIFIED: Add async_send_command() PUT method, schedule PUT methods
├── coordinator.py       # MODIFIED: Add async_send_vehicle_command() orchestrator with cooldown/optimistic/delayed refresh
├── lock.py              # NEW: Door lock + trunk locker entities
├── climate.py           # NEW: Climate pre-conditioning entity
├── switch.py            # NEW: Charging, fridge, fragrance, VTM, climate schedule toggle entities
├── button.py            # NEW: Horn, flash, find-my-car, close-windows entities
├── number.py            # NEW: Target SOC slider entity
├── time.py              # NEW: Charging schedule start/end, climate schedule time entities
├── strings.json         # MODIFIED: Add translation keys for all new entities
├── manifest.json        # No changes needed (no new dependencies)
├── auth.py              # No changes needed
├── config_flow.py       # No changes needed
├── sensor.py            # No changes needed
├── binary_sensor.py     # No changes needed
├── device_tracker.py    # No changes needed
└── diagnostics.py       # No changes needed

tests/
├── test_api.py          # MODIFIED: Tests for async_send_command() PUT method
├── test_coordinator.py  # MODIFIED: Tests for command orchestrator, cooldown, optimistic updates
├── test_lock.py         # NEW: Door lock entity tests
├── test_climate.py      # NEW: Climate entity tests
├── test_switch.py       # NEW: Switch entity tests (charging, fridge, fragrance, VTM)
├── test_button.py       # NEW: Button entity tests (horn, flash, find, window close)
├── test_number.py       # NEW: Number entity tests (target SOC)
└── test_time.py         # NEW: Time entity tests (schedule times)
```

**Structure Decision**: 6 new platform files required — HA mandates one `.py` per entity platform type registered in `PLATFORMS`. This is not optional; it is how HA discovers and loads entity platforms. All other changes go into existing files.

| Violation | Why Needed | Simpler Alternative Rejected Because |
|-----------|------------|-------------------------------------|
| [e.g., 4th project] | [current need] | [why 3 projects insufficient] |
| [e.g., Repository pattern] | [specific problem] | [why direct DB access insufficient] |
