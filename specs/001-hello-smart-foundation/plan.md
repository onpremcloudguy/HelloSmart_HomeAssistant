# Implementation Plan: Hello-Smart Foundation

**Branch**: `001-hello-smart-foundation` | **Date**: 2026-03-07 | **Spec**: [spec.md](spec.md)
**Input**: Feature specification from `/specs/001-hello-smart-foundation/spec.md`

## Summary

A Home Assistant custom integration ("Hello Smart") that authenticates against the Smart vehicle cloud API (EU and INTL regions), discovers linked vehicles, and exposes vehicle status (battery, charging, doors, windows, climate, location, OTA firmware) as HA entities. Uses HA's native config flow for setup, `DataUpdateCoordinator` for periodic polling, and `aiohttp` for all HTTP communication. Region-aware authentication selects the correct login flow (EU Gigya-based vs. INTL three-step OAuth) and header-signing scheme automatically.

## Technical Context

**Language/Version**: Python 3.13+ (matching Home Assistant Core 2025.x minimum)  
**Primary Dependencies**: `aiohttp` (via HA's `async_get_clientsession`), `homeassistant` core APIs (config_flow, DataUpdateCoordinator, entity platforms, device registry, diagnostics)  
**Storage**: HA `config_entry` for credentials/settings; HA `Store` for any persistent token cache if needed  
**Testing**: `pytest` with `pytest-homeassistant-custom-component` and `pytest-aiohttp`  
**Target Platform**: Home Assistant Core (any OS — HassOS, Docker, venv)  
**Project Type**: HA custom integration (custom_components)  
**Performance Goals**: Config flow completes in <30s; polling cycle completes in <10s for up to 10 vehicles  
**Constraints**: No blocking I/O in the event loop; no dependencies outside HA's Python environment; aiohttp only (no httpx/requests)  
**Scale/Scope**: Single account per config entry, up to 10 vehicles per account; ~15 entities per vehicle

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

| Principle | Status | Evidence |
|-----------|--------|----------|
| **I. HA Compatibility** | ✅ PASS | Python 3.13+, asyncio only, aiohttp via HA session, no external deps beyond HA runtime |
| **II. Security-First** | ✅ PASS | Credentials in config_entry, HTTPS enforced, URL allowlist, log redaction, no hardcoded secrets |
| **III. Minimal Footprint** | ✅ PASS | Only runtime files in `custom_components/`; tests/scripts/docs outside production dir |
| **IV. Organized Testing** | ✅ PASS | All tests under `tests/` mirroring production structure; shared fixtures in `conftest.py` |
| **V. Simplicity** | ✅ PASS | Uses HA built-in helpers (coordinator, entity platforms, config_flow); YAGNI — no remote commands, no webhook, no Lovelace cards |

**Gate result**: PASS — proceed to Phase 0.

### Post-Design Re-Check (after Phase 1)

| Principle | Status | Post-Design Evidence |
|-----------|--------|---------------------|
| **I. HA Compatibility** | ✅ PASS | All HTTP via `async_get_clientsession(hass)`; async-only; HMAC uses stdlib `hmac`/`hashlib`; no external deps |
| **II. Security-First** | ✅ PASS | Signing secrets are public app identifiers; credentials in config_entry; URL allowlist to known Smart hosts; `async_redact_data` for logs/diagnostics |
| **III. Minimal Footprint** | ✅ PASS | 13 production files; no test/debug code shipped; single coordinator |
| **IV. Organized Testing** | ✅ PASS | Tests under `tests/`; shared fixtures in `conftest.py` + `helpers/`; debug in `scripts/debug/` |
| **V. Simplicity** | ✅ PASS | HA built-in coordinator/config_flow/entity platforms; region via simple conditional; no factories or abstractions |

**Post-design gate result**: PASS — no violations.

## Project Structure

### Documentation (this feature)

```text
specs/001-hello-smart-foundation/
├── plan.md              # This file
├── research.md          # Phase 0 output
├── data-model.md        # Phase 1 output
├── quickstart.md        # Phase 1 output
├── contracts/           # Phase 1 output
└── tasks.md             # Phase 2 output (/speckit.tasks command)
```

### Source Code (repository root)

```text
custom_components/hello_smart/
├── __init__.py          # Integration setup, async_setup_entry, async_unload_entry
├── const.py             # Constants: DOMAIN, API URLs, default scan interval
├── config_flow.py       # Config flow: user step (credentials + region), options flow (scan interval)
├── coordinator.py       # DataUpdateCoordinator subclass: auth, poll, token refresh
├── auth.py              # Region-aware authentication (EU + INTL login flows, header signing)
├── api.py               # Smart API client: vehicle list, vehicle status, OTA info
├── models.py            # Data classes: Account, Vehicle, VehicleStatus, OTAInfo
├── sensor.py            # Sensor entities: battery %, range, charging status, firmware versions
├── binary_sensor.py     # Binary sensor entities: doors, windows, charging connected, update available
├── device_tracker.py    # Device tracker entity: GPS location
├── diagnostics.py       # Diagnostics dump with redaction
├── manifest.json        # Integration metadata and dependencies
└── strings.json         # UI strings for config flow

tests/
├── conftest.py          # Shared fixtures: mock API responses, mock auth, mock coordinator
├── helpers/
│   └── mock_api.py      # Reusable Smart API mock responses (EU + INTL)
├── test_config_flow.py  # Config flow tests: valid/invalid creds, duplicate detection, options
├── test_auth.py         # Auth tests: EU flow, INTL flow, token refresh, error handling
├── test_coordinator.py  # Coordinator tests: polling, re-auth, unavailable handling
├── test_sensor.py       # Sensor entity tests
├── test_binary_sensor.py # Binary sensor entity tests
├── test_device_tracker.py # Device tracker entity tests
└── test_diagnostics.py  # Diagnostics redaction tests

scripts/
└── debug/
    └── test_smart_api.py  # Manual API test script (not shipped in production)
```

**Structure Decision**: Single-project HA custom integration layout following HA's standard `custom_components/<domain>/` convention. All production code under `custom_components/hello_smart/`. Tests mirror the production structure under `tests/`. Debug utilities isolated in `scripts/debug/`.

## Complexity Tracking

> No constitution violations — this section is intentionally empty.
