# Implementation Plan: APK GET Endpoint Extraction & Integration

**Branch**: `002-apk-get-endpoints` | **Date**: 2026-03-08 | **Spec**: [spec.md](spec.md)
**Input**: Feature specification from `/specs/002-apk-get-endpoints/spec.md`

## Summary

Extend the existing Hello Smart HA integration to consume all GET API endpoints discovered via reverse-engineering both APK files. Adds ~20 new API client methods, ~15 new data model dataclasses, and ~30+ new sensor/binary sensor entity descriptions. Implements silent per-endpoint failure (no cascade), dynamic entity visibility (only show entities with valid data), 60-second default polling, and enhanced vehicle DeviceInfo (serial number, HW/SW versions, suggested area). All new endpoints use the existing HMAC-signed request infrastructure; no new dependencies.

## Technical Context

**Language/Version**: Python 3.13+ (matching Home Assistant Core 2025.x minimum)
**Primary Dependencies**: `aiohttp` (via HA's `async_get_clientsession`), `homeassistant` core APIs (config_flow, DataUpdateCoordinator, entity platforms, device registry, diagnostics)
**Storage**: HA `config_entry` for credentials/settings; no new storage needed
**Testing**: `pytest` with `pytest-homeassistant-custom-component` and `pytest-aiohttp`
**Target Platform**: Home Assistant Core (any OS — HassOS, Docker, venv)
**Project Type**: HA custom integration (custom_components)
**Performance Goals**: Polling cycle completes in <15s for up to 10 vehicles with all endpoints; individual endpoint timeout <5s
**Constraints**: No blocking I/O in the event loop; no dependencies outside HA's Python environment; aiohttp only (no httpx/requests); silent failure per endpoint
**Scale/Scope**: Single account per config entry, up to 10 vehicles per account; ~45+ entities per vehicle (up from ~15)

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

| Principle | Status | Evidence |
|-----------|--------|----------|
| **I. HA Compatibility** | ✅ PASS | Python 3.13+, asyncio only, aiohttp via HA session, no external deps. All new endpoints use existing `_signed_request` and `async_get_clientsession`. |
| **II. Security-First** | ✅ PASS | All URLs validated against URL_ALLOWLIST, HTTPS enforced, no hardcoded secrets. New sensitive fields (PINs, locker secrets) added to `SENSITIVE_FIELDS`. Log redaction maintained. |
| **III. Minimal Footprint** | ✅ PASS | Only modifies existing production files in `custom_components/hello_smart/`. No new runtime files needed — extensions go into existing `api.py`, `models.py`, `sensor.py`, `binary_sensor.py`, `coordinator.py`, `const.py`, `strings.json`. |
| **IV. Organized Testing** | ✅ PASS | New tests go into existing test files under `tests/`. Shared mock responses in `tests/helpers/`. No new test files unless the scope of an existing file is exceeded. |
| **V. Simplicity** | ✅ PASS | Follows existing patterns exactly — `SmartSensorEntityDescription` with `value_fn`, `SmartBinarySensorEntityDescription` with `is_on_fn`, `CoordinatorEntity` mixin. No new abstractions, wrappers, or factories. Each new endpoint is a simple async method that calls `_signed_request`. |

**Gate result**: PASS — proceed to Phase 0.

## Project Structure

### Documentation (this feature)

```text
specs/002-apk-get-endpoints/
├── plan.md              # This file
├── research.md          # Phase 0 output
├── data-model.md        # Phase 1 output
├── quickstart.md        # Phase 1 output
├── contracts/           # Phase 1 output
│   └── smart-api-extended.md
└── tasks.md             # Phase 2 output (/speckit.tasks command)
```

### Source Code (repository root)

```text
custom_components/hello_smart/
├── __init__.py          # No changes needed (PLATFORMS already correct)
├── const.py             # MODIFIED: DEFAULT_SCAN_INTERVAL → 60, new SENSITIVE_FIELDS
├── models.py            # MODIFIED: Add ~15 new dataclasses for endpoint responses
├── api.py               # MODIFIED: Add ~20 new async_get_* methods to SmartAPI
├── coordinator.py       # MODIFIED: Wire new endpoints into _async_fetch_all_vehicles, enhance DeviceInfo
├── sensor.py            # MODIFIED: Add ~20 new SmartSensorEntityDescription entries, dynamic filtering
├── binary_sensor.py     # MODIFIED: Add ~10 new SmartBinarySensorEntityDescription entries, dynamic filtering
├── device_tracker.py    # No changes needed (already uses DeviceInfo from coordinator)
├── diagnostics.py       # No changes needed (already redacts SENSITIVE_FIELDS)
├── strings.json         # MODIFIED: Add translation keys for all new entities
├── manifest.json        # No changes needed (no new dependencies)
├── auth.py              # No changes needed
└── config_flow.py       # No changes needed

tests/
├── test_api.py          # MODIFIED: Tests for new async_get_* methods
├── test_coordinator.py  # MODIFIED: Tests for extended fetch, silent failure, DeviceInfo
├── test_sensor.py       # MODIFIED: Tests for new sensor entities, dynamic visibility
└── test_binary_sensor.py # MODIFIED: Tests for new binary sensor entities, dynamic visibility
```

**Structure Decision**: No new files — all additions go into existing files following the established patterns from feature 001. This maintains minimal footprint per Constitution Principle III.

---

## Phase 0: Research

**Output**: [research.md](research.md)

### Key Research Findings

| # | Topic | Decision |
|---|-------|----------|
| 1 | API response envelope | Standard `{code: 1000, data, success, message}` — confirmed |
| 2 | Tyre pressure source | Already in existing vehicle status response (`maintenanceStatus`), units are **kPa** (not bar) |
| 3 | Maintenance data source | Also in existing vehicle status response — odometer, service intervals, 12V battery, fluids |
| 4 | Schema confidence | 3 endpoints partially confirmed, 16 speculative — all parsing must be defensive |
| 5 | Endpoint deduplication | 19 net new endpoints after removing 5 duplicates/subsets from the original 36 |
| 6 | Dynamic entity visibility | Use `None` sentinel + filter at entity registration time |
| 7 | Vehicle DeviceInfo | Extended with `model_id`, `hw_version`, `sw_version`, `serial_number`, `suggested_area` |
| 8 | Rate limiting | No evidence, but sequential calls are safer than parallel fan-out |
| 9 | Fragrance system | Confirmed via `climateStatus.fragActive` in pySmartHashtag fixture |
| 10 | No-VIN endpoints | Use selected vehicle session (existing `async_select_vehicle` call) |

### Spec Corrections

- **FR-014**: Tyre pressure unit changed from "bar" to "kPa" (pySmartHashtag confirms kPa)
- **Tyre/maintenance data**: Extracted from existing vehicle status response, not separate endpoints — reduces net new API calls

---

## Phase 1: Design & Contracts

### Outputs

- [data-model.md](data-model.md) — 1 new enum (`PowerMode`), 13 new dataclasses, extended `VehicleStatus` (23 new fields) and `VehicleData` (15 new optional fields)
- [contracts/smart-api-extended.md](contracts/smart-api-extended.md) — 19 new GET endpoint contracts with response schemas and confidence levels
- [quickstart.md](quickstart.md) — ~25 new sensors, ~10 new binary sensors, 7 modified files

### Design Decisions

1. **All code in existing files** — no new production files (`models.py`, `api.py`, `sensor.py`, `binary_sensor.py`, `coordinator.py`, `const.py`, `strings.json`)
2. **Sequential API calls** — endpoints called one-by-one within `_async_fetch_all_vehicles`, each in its own try/except
3. **Defensive parsing** — all `.get()` with defaults, `float()`/`int()` wrapped in try/except, `None` for missing data
4. **kPa tyre pressure** — HA's unit conversion handles display in user-preferred units (bar, PSI)
5. **Prefer Tier 1** — when Tier 1 and Tier 2 provide same data, use Tier 1 (`/remote-control/`)
6. **Trip journal V4** — preferred over V1 for richer data (max speed, regen energy, addresses)
7. **17 skipped endpoints** — user/auth management, weather (HA has dedicated integrations), and duplicates

### Agent Context

Updated `.github/agents/copilot-instructions.md` via `update-agent-context.sh copilot`.

---

## Post-Design Constitution Re-Check

| Principle | Status | Evidence |
|-----------|--------|----------|
| **I. HA Compatibility** | ✅ PASS | All additions use asyncio, aiohttp via HA session, no external deps. New entities follow `CoordinatorEntity` + `SensorEntityDescription` pattern. `DeviceInfo` uses only HA-supported fields. |
| **II. Security-First** | ✅ PASS | All URLs go through `_validate_url` + `URL_ALLOWLIST`. No new hosts needed — all endpoints use `api.ecloudeu.com`. New sensitive fields (IMEI, locker secret) added to `SENSITIVE_FIELDS`. No credentials in logs. |
| **III. Minimal Footprint** | ✅ PASS | Zero new production files. 7 modified files. No new dependencies. 13 small dataclasses (not 15 — deduplication reduced count). |
| **IV. Organized Testing** | ✅ PASS | Tests in existing test files. Mock responses in `tests/helpers/`. Each new endpoint gets a success test + failure test (silent skip). |
| **V. Simplicity** | ✅ PASS | No new abstractions. Each endpoint → one `async_get_*` method → one dataclass → one or more `EntityDescription` entries. Same pattern repeated. Dynamic visibility is a 3-line filter, not a framework. |

**Post-design gate result**: PASS — ready for task generation via `/speckit.tasks`.
