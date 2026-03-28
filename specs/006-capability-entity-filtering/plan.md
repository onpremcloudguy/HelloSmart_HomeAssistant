# Implementation Plan: Capability-Based Entity Filtering

**Branch**: `006-capability-entity-filtering` | **Date**: 2026-03-28 | **Spec**: [spec.md](spec.md)
**Input**: Feature specification from `/specs/006-capability-entity-filtering/spec.md`

## Summary

Implement capability-based entity filtering so the Hello Smart integration only creates HA entities for features the vehicle actually supports, based on `functionId`/`valueEnable` flags from the capability API. Additionally, cache static data (capabilities, vehicle ability, plant number) to eliminate redundant API calls on every 60-second poll cycle. Update API documentation to reflect the full capability response schema.

## Technical Context

**Language/Version**: Python 3.13+ (Home Assistant 2025.x minimum)
**Primary Dependencies**: `aiohttp` (HA-bundled HTTP client), `homeassistant` core APIs (`DataUpdateCoordinator`, `Entity`, `ConfigEntry`)
**Storage**: In-memory caching on `SmartDataCoordinator` instance; no persistent storage needed
**Testing**: `pytest` (test framework exists at `tests/` but no tests are written yet)
**Target Platform**: Home Assistant (Linux/Docker/HassOS), HACS custom component
**Project Type**: Home Assistant custom integration (cloud-polling IoT)
**Performance Goals**: No increase in per-poll latency; reduce API calls by 3 per poll cycle per vehicle
**Constraints**: Must run in HA's single-threaded asyncio event loop; no blocking I/O; aiohttp only
**Scale/Scope**: Single integration, ~10 entity platform files, ~15 files modified total

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

| Principle | Status | Notes |
|-----------|--------|-------|
| **I. HA Compatibility** | PASS | Python 3.13+, asyncio patterns, no new dependencies, `manifest.json` requirements unchanged |
| **II. Security-First** | PASS | No new external endpoints; capability data is read-only from existing signed API; no credentials affected; no new URL construction beyond existing allowlisted base URLs |
| **III. Minimal Production Footprint** | PASS | Adds a `required_capability` field to entity description dataclasses and a capability-check helper; removes redundant API calls per poll cycle; no new files in `custom_components/` |
| **IV. Organized Testing & Reuse** | PASS | New tests will be under `tests/` mirroring production structure; no new debug scripts needed |
| **V. Simplicity & Code Quality** | PASS | Uses HA's built-in `DataUpdateCoordinator` caching pattern; capability map is a simple dict constant in `const.py`; no wrapper layers or factory patterns |

**Gate result: PASS** — no violations. Proceeding to Phase 0.

## Project Structure

### Documentation (this feature)

```text
specs/006-capability-entity-filtering/
├── plan.md              # This file
├── research.md          # Phase 0 output
├── data-model.md        # Phase 1 output
├── quickstart.md        # Phase 1 output
├── contracts/           # Phase 1 output
└── tasks.md             # Phase 2 output (/speckit.tasks command - NOT created by /speckit.plan)
```

### Source Code (repository root)

```text
custom_components/hello_smart/
├── __init__.py          # Integration setup (unchanged)
├── api.py               # MODIFIED: async_get_capabilities() enhanced to parse functionId/valueEnable
├── const.py             # MODIFIED: Add CAPABILITY_MAP dict and function ID constants
├── coordinator.py       # MODIFIED: Cache static data, fetch once on setup
├── models.py            # MODIFIED: VehicleCapabilities gets capability_flags dict
├── sensor.py            # MODIFIED: Add required_capability to descriptions, filter in async_setup_entry
├── binary_sensor.py     # MODIFIED: Add required_capability to descriptions, filter in async_setup_entry
├── switch.py            # MODIFIED: Add required_capability to descriptions (already has available_fn)
├── lock.py              # MODIFIED: Add required_capability to descriptions (already has available_fn)
├── button.py            # MODIFIED: Add required_capability to descriptions, filter in async_setup_entry
├── select.py            # MODIFIED: Add required_capability to descriptions, filter in async_setup_entry
├── climate.py           # MODIFIED: Add capability check before entity creation
├── device_tracker.py    # UNCHANGED (always created - vehicle position is universal)
├── diagnostics.py       # UNCHANGED
├── number.py            # MODIFIED: Add required_capability if applicable
└── time.py              # MODIFIED: Add required_capability if applicable

API/
├── endpoints/
│   └── capabilities.md  # MODIFIED: Full response schema with functionId/valueEnable
├── entities.md          # MODIFIED: Add capability function ID column
└── models.md            # MODIFIED: Updated VehicleCapabilities model

tests/
├── unit/
│   └── test_capability_filtering.py  # NEW: Unit tests for capability map and filtering
└── helpers/
    └── (existing)
```

**Structure Decision**: Existing single-project structure. All changes are modifications to existing files in `custom_components/hello_smart/`. One new test file. Three API doc files updated. No new production files created.

## Complexity Tracking

No constitution violations — this section is not applicable.
