# Changelog

All notable changes to this project will be documented in this file.

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
