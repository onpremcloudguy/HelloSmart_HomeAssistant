# Changelog

All notable changes to this project will be documented in this file.

## [0.3.0] — 2026-03-08

### Feature: API Command Controls (`003-api-command-controls`)

Added full vehicle remote-control capabilities via PUT command endpoints, 7 new HA platforms, and SmartHashtag entity parity. Expanded entity count from 82 to 172.

### Added

- **Command infrastructure** — `async_send_command()` PUT transport with HMAC-signed payloads, `async_send_vehicle_command()` orchestrator with 5-second per-VIN cooldown, automatic vehicle selection, and 8-second delayed refresh after commands
- **Lock platform** — Door lock/unlock with optimistic state updates (`RDL_2`/`RDU_2`), trunk locker lock for equipped vehicles
- **Climate platform** — Pre-conditioning start/stop with target temperature control (16–30°C), `HVACMode.HEAT_COOL`/`OFF` (`RCE_2`)
- **Switch platform** — Charging start/stop (`rcs`), fridge toggle (`UFR`), fragrance toggle, VTM enable/disable, climate schedule on/off — 5 switch entities total
- **Button platform** — Horn (`RHL`), flash lights, find my car (horn + flash), close windows (`RWS_2`) — 4 button entities
- **Number platform** — Charging target SOC slider (50–100%, step 5) via charging reservation PUT endpoint
- **Time platform** — Charging start/end time pickers, climate schedule time picker via schedule PUT endpoints
- **Select platform** — Seat heating control (driver, passenger, steering wheel) via `RSH` with Off/Low/Medium/High levels, driver seat ventilation control via `RSV`
- **SmartHashtag entity parity** — Added ~90 new status fields, 33 new sensors, 50 new binary sensors to match SmartHashtag integration coverage
- **Data models** — `CommandResult` dataclass, seat heating/ventilation status fields, extended vehicle status fields for all SmartHashtag-equivalent data
- **API documentation** — Command endpoint contract specs in `contracts/smart-api-commands.md`

### Changed

- **Entity count** — 82 → 172 entities across 10 platforms (sensor: 83, binary_sensor: 74, device_tracker: 1, lock: 2, climate: 1, switch: 5, button: 4, number: 1, select: 4, time: 2)
- **Entity registration** — Unconditional registration for all sensor/binary_sensor entities (no longer skips when data is None)
- **Entity defaults** — All `value_fn`/`is_on_fn` lambdas return meaningful defaults (0, False, "off", "inactive") instead of None — zero unavailable entities
- **Battery device class** — Only main EV battery (`battery_level`) tagged as `SensorDeviceClass.BATTERY`; removed from 12V battery, backup battery, and target SOC sensors
- **Device tracker** — Always available when coordinator has data (no longer requires GPS coordinates to be non-None)
- **Last trip energy** — State class changed from `MEASUREMENT` to `TOTAL` to satisfy HA's `ENERGY` device class constraint

### Fixed

- Battery status defaulting to 12V battery instead of main EV battery level
- Stale recorder entities from previous naming schemes (45+ orphaned entries purged)

---

## [0.2.0] — 2026-03-08

### Feature: APK GET Endpoint Extraction & Integration (`002-apk-get-endpoints`)

Reverse-engineered 21 GET endpoints from the Smart mobile APK (EU + INTL) and integrated them as Home Assistant entities. Expanded entity count from 18 to 82.

### Added

- **API endpoints** — 15 new GET endpoints: vehicle state, telematics, trip journal, charging reservation, climate schedule, fridge, locker, fragrance, VTM settings, geofences, capabilities, diagnostics, energy ranking, total distance, FOTA notifications, plant number
- **Data models** — 18 dataclasses and 4 enums covering all endpoint response types (`models.py`)
- **Sensors (53)** — Tyre pressure/temperature (×4 each), odometer, maintenance countdown, 12V battery, interior/exterior temperature, power mode, speed, charging schedule, climate schedule, trip journal, total distance, energy ranking, fridge temperature, fragrance level, geofence count, firmware versions, capabilities
- **Binary sensors (28)** — Doors (×5), windows (×4), tyre warnings (×4), charger connected, telematics connected, brake fluid, firmware updates, fridge/fragrance/locker, VTM enabled, washer fluid
- **Device tracker** — GPS location from telematics endpoint
- **Brand icons** — Custom `brand/` directory with `icon.png`, `logo.png`, and `@2x` retina variants for HA integration card
- **Translations** — `translations/en.json` for all 82 entity names (required by HA for custom integrations)
- **API documentation** — 28 markdown files: per-endpoint docs, common patterns, data models, entity mapping
- **Dynamic entity visibility** — Entities only appear when their data source returns non-null (accessories auto-hide when unsupported)
- **Entity UX** — MDI icons, `EntityCategory.DIAGNOSTIC` for firmware/diagnostic entities, `entity_registry_enabled_default=False` for niche entities, `suggested_display_precision` for numeric values

### Changed

- **Polling interval** — Reduced from 300s to 60s (`DEFAULT_SCAN_INTERVAL`)
- **Coordinator** — Orchestrates 15 parallel API calls per poll cycle with individual error isolation
- **Device info** — Enhanced with `model_id`, `hw_version` (year), `sw_version` (firmware), `serial_number` (VIN), `suggested_area` ("Garage")
- **Entity names** — Human-friendly names ("Estimated range", "Cabin temperature", "Vehicle online", etc.)

### Fixed

- Entity naming: HA showed generic device_class names (Door ×5, Pressure ×4) — fixed by creating `translations/en.json`
- API parsers: Handle list-wrapped responses from geofences and climate schedule endpoints
- Error handling: Broadened `except SmartAPIError` to `except Exception` for resilient polling

## [0.1.0] — 2026-03-08

### Feature: Hello Smart Foundation (`001-hello-smart-foundation`)

Initial integration with core authentication, vehicle discovery, and basic entities.

### Added

- INTL 3-step and EU 4-step Gigya authentication flows
- HMAC-SHA1 request signing (region-aware)
- Vehicle discovery and status polling via `DataUpdateCoordinator`
- Config flow with duplicate detection and options flow
- Diagnostics download with sensitive field redaction
- Docker Compose development environment
