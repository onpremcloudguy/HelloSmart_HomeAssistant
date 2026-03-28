# Changelog

All notable changes to this project will be documented in this file.

## [0.5.1] — 2026-03-29

### Fixed

- **Static cache capability retry** — when the capabilities API call fails on initial boot (transient error), the coordinator no longer permanently caches `None`; subsequent poll cycles retry the fetch until capabilities are successfully loaded, preventing ~50 capability-gated entities (doors, windows, trunk, tyres, charge lids, hood, door locks) from being silently filtered out
- **Card entity map rebuild** — `_buildDeviceEntityMap` in both custom cards now tracks entity count and rebuilds the map when the HA entity registry grows, fixing partial entity maps when `hass.entities` loads progressively

### Changed

- **Diagnostics output** — added `capabilities.available` and `capabilities.flag_count` to the diagnostics config entry dump for easier remote debugging

---

## [0.5.0] — 2026-03-29

### Feature: Capability-Based Entity Filtering (`006-capability-entity-filtering`)

Intelligent entity filtering based on vehicle hardware capabilities, trim level, and equipment detection. Vehicles only show entities for features they actually have — no more phantom sensors for sunroofs on cars without sunroofs, or seat heating controls on base-trim vehicles.

### Added

- **Capability-based entity filtering** — all 9 entity platforms (sensor, binary_sensor, lock, climate, switch, button, select, number, time) now check vehicle capability flags before creating entities; unsupported features are silently excluded
- **Sentinel value detection** — position fields returning `101` ("not equipped" hardware) are normalised to `None` in the API layer; sunroof, curtain, and rear sun curtain positions correctly report as unavailable on non-equipped vehicles
- **V2→V1 capability alias mapping** — API returns v2 function IDs; 10-entry mapping dict translates to the v1 constants used by entity descriptions; 3 inferred capabilities for IDs with no direct v2 equivalent
- **Vehicle model detection** — `VehicleModel` enum (Smart #1/#3/#5) derived from `matCode` prefix (HX1/HC1/HY1)
- **Vehicle edition detection** — `VehicleEdition` enum (Pure/Pro/Pulse/Premium/BRABUS/Launch) derived from `matCode` positions [5:7], with feature-gate properties (`has_driver_seat_heating`, `has_pm25`) matching APK logic
- **Edition-based entity filtering** — `edition_check` callback on sensor/select entity descriptions excludes PM2.5 sensors (Pure/Pro only) and seat heating controls (Pure only) based on trim level
- **Hardware equipment filtering** — `equipped_fn` callback on sensor/binary_sensor descriptions excludes entities when hardware reports "not equipped" via sentinel values
- **Stale entity cleanup** — entity registry cleanup in `async_setup_entry` for sensor, binary_sensor, and select platforms; removes orphaned entity entries after filtering changes
- **Vehicle model/edition diagnostic sensors** — two new diagnostic sensors showing detected model (#1/#3/#5) and edition (Pure/Pro/Pulse/Premium/BRABUS/Launch)
- **Static data caching** — capabilities, vehicle ability, and plant number endpoints cached after first fetch; eliminates 3 API calls per poll cycle per vehicle
- **Lovelace resource registration** — custom card JS files registered as proper Lovelace storage resources (same mechanism as HACS) instead of deferred script injection; eliminates intermittent "configuration error" on page refresh
- **Card loading resilience** — `connectedCallback` lifecycle hook and loading placeholder in both custom cards; cards show "Loading…" state instead of empty DOM while waiting for `hass`
- **Frontend early registration** — `async_setup()` hook registers static paths at platform level before entry setup, ensuring JS files are servable before any dashboard renders

### Changed

- **Capability default changed** — `cap_flags.get(key, True)` → `cap_flags.get(key, False)` across all 9 entity platforms; unknown capabilities now default to disabled (safe-by-default)
- **Coordinator DeviceInfo** — model label now shows "Smart #3 BRABUS" style device names derived from matCode
- **Dashboard sunroof cards** — wrapped in `conditional` cards that hide when entity is unavailable (both enhanced and basic dashboards)
- **Frontend registration order** — moved from `async_setup_entry` (after 19s API refresh) to `async_setup` (before any entry loads); version-aware cleanup removes stale resource entries on upgrade

### Fixed

- **Phantom sunroof entities** — sunroof, curtain, and rear sun curtain sensors/binary sensors no longer created on vehicles without sunroof hardware
- **Custom card race condition** — "configuration error" on hard refresh caused by JS loaded via `add_extra_js_url` (deferred script) racing against card instantiation; fixed by registering as Lovelace resources which load before card rendering

### API Documentation

- **capabilities.md** — V2→V1 function ID mapping table, inferred capabilities, default behaviour docs
- **list-vehicles.md** — full response JSON, matCode decoding (model prefix table, edition code table, feature matrix)
- **vehicle-status.md** — climate detail fields, sentinel value 101 section
- **models.md** — VehicleModel/VehicleEdition enums, expanded Vehicle/VehicleStatus dataclasses
- **common-patterns.md** — vehicle commands PUT section with all 12 service IDs and parameters
- **index.md** — vehicle commands quick reference
- **README.md** — removed "read-only only" notice

---

## [0.4.4] — 2026-03-09

### Fixed

- **Charge lid polarity inverted** — charge lid AC/DC sensors always showed "closed"; APK `controlChargeLib()` confirms `"1"` = open, not `"0"` (`api.py`)
- **Charger connected too restrictive** — only accepted `statusOfChargerConnection == "1"`; APK `getChargingPlugged()` shows values 1, 2, and 3 all mean plugged in (`api.py`)
- **Charger state enum completely wrong** — used guessed sequential ranges (0, 1–3, 4–6, etc.); APK `TspEdgeRepository.ChargerState` has specific values: 0=not charging, 2=AC, 15=DC, 24=super, 25=plugged not charging, 28=boost, 30=wireless (`models.py`, `switch.py`, `hello-smart-charge-card.js`)
- **Washer fluid exposed as meaningless raw integer** — `washerFluidLevelStatus` is a status code (0=normal, 1=low, 2=too low, 7=unknown) matching the tyre warning convention from APK `tyreStatusTranslate()`; changed from `sensor` to `binary_sensor` with `PROBLEM` device class (`sensor.py` → `binary_sensor.py`, `models.py`, `api.py`)
- **Brake fluid always showing problem** — `_safe_bool("3")` returned False since only `"1"`/`"true"` = True; API returns `"3"` (= OK/high); switched to integer status interpretation matching washer fluid convention (`api.py`)

---

## [0.4.3] — 2026-03-09

### Fixed

- **hassfest validation** — added `frontend` and `http` to `dependencies` in `manifest.json` (required because the integration imports from `homeassistant.components.frontend` and `homeassistant.components.http` for custom Lovelace card registration)

---

## [0.4.2] — 2026-03-09

### Fixed

- **Integration icon** — copied brand assets (`icon.png`, `logo.png` + @2x variants) to integration root directory where Home Assistant expects them

### Added

- **My Home Assistant badge** — one-click "Add to HACS" button in README
- **Acknowledgements section** — credit to [smarthashtag](https://github.com/DasBasti/smarthashtag) by @DasBasti as project inspiration

---

## [0.4.1] — 2026-03-09

### Feature: HACS Packaging (`005-hacs-packaging`)

Added all required metadata and CI workflows for HACS (Home Assistant Community Store) compatibility. Users can now install the integration via HACS custom repository.

### Added

- **hacs.json** — HACS store configuration with integration name and minimum Home Assistant version (2024.1.0)
- **LICENSE** — MIT license file (required by HACS)
- **CI workflow** (`.github/workflows/validate.yml`) — automated HACS validation (`hacs/action`) and Home Assistant manifest validation (`hassfest`) on push, pull request, weekly schedule, and manual dispatch; minimal permissions (`permissions: {}`)

### Changed

- **manifest.json** — populated `codeowners` field (`@onpremcloudguy`), updated `documentation` URL to actual repository, added `issue_tracker` field

---

## [0.4.0] — 2026-03-08

### Feature: Lovelace Vehicle Dashboard & Custom Cards (`004-lovelace-dashboard`)

Added two custom Lovelace cards bundled with the integration (no HACS dependency), pre-built YAML dashboards for quick setup, and interactive lock/charge controls directly from the cards.

### Added

- **Vehicle HUD card** (`custom:hello-smart-vehicle-card`) — top-down vehicle image with door, window, trunk, hood, and sunroof overlays at physical positions; lock status row with per-door icons; interactive lock/unlock via header button and clickable lock icons; auto-detects vehicle (zero config for single-vehicle setups); device-registry-based entity lookup with compressed key support and SUFFIX_TO_TKEY fallback
- **Charge Status card** (`custom:hello-smart-charge-card`) — battery level gauge with animated fill bar and color thresholds (green/orange/red); charging state header with icon/label for 6 states (not charging, preparing, AC, DC fast, paused, fully charged); info strip showing range, average consumption, and charger connection; live charging metrics section (power, voltage, current, time to full, range at full) shown only while charging; scheduled charging section with start/end times and target SOC; optional 12V battery section; pulse-glow animation on gauge while charging
- **Frontend registration** — `async_register_static_paths` + `add_extra_js_url` auto-registers both card JS files from the `frontend/` directory; guard prevents duplicate registration across config entries
- **Visual card editors** — both cards include `getConfigElement()` editors with auto-detection, vehicle picker (multi-vehicle only), and toggle options
- **Enhanced dashboard** (`dashboards/smart-vehicle.yaml`) — Mushroom-based dashboard with 7 card groups: Hero, Battery & Range, Charging Status with interactive controls (SOC slider, schedule pickers, start/stop toggle), Lock & Security with picture-elements HUD diagram, Tyre Status in spatial wheel layout, Windows with close-all button, Service Information (odometer, maintenance, fluids, firmware, diagnostics). Smart brand CSS theming (#0078D4 accent) with dark-theme support
- **Basic dashboard** (`dashboards/smart-vehicle-basic.yaml`) — standard HA entities/gauge cards covering all 7 card groups, no HACS dependencies required
- **Dashboard assets** — extracted vehicle images from APK: `image_big_car_3x.png` (981×484), `vehicle_hud_1.png` (1112×668), `gsv_dev_ic_vehicle_main.png` (522×255), plus rendered vehicle previews
- **Dashboard guide** (`dashboards/README.md`) — installation prerequisites, image setup, YAML import instructions, VIN customization, troubleshooting

### Changed

- **Lock entity availability** — `available_fn` now checks individual `door_lock_driver`/`passenger`/`driver_rear`/`passenger_rear` fields instead of empty `data.status.doors` dict; lock entity now created for vehicles with door lock binary sensors
- **Lock state detection** — `_doors_locked()` reads individual door lock fields (1=locked, 0=unlocked) instead of the `doors` dict
- **Brand icons** — updated all brand icon variants (icon.png, icon@2x.png, logo.png, logo@2x.png) with HelloSmartLogo.png resized to 256×256 and 512×512
- **API documentation** — added vehicle ability endpoint docs, APK API audit notes

### Fixed

- Lock entity not created when `data.status.doors` was empty despite individual door lock sensors being available

---

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
