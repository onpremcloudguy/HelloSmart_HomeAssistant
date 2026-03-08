# Quickstart: APK GET Endpoint Extraction & Integration

**Branch**: `002-apk-get-endpoints` | **Date**: 2026-03-08

## What This Feature Adds

Extends the Hello Smart HA integration from ~15 entities per vehicle to ~45+ entities by consuming all GET API endpoints discovered in the Smart mobile app APK files.

## Key Changes

### 1. Polling Interval: 5 min → 60 sec
- `DEFAULT_SCAN_INTERVAL` changes from 300 to 60 in `const.py`
- User-configurable via options flow (minimum 60 seconds)

### 2. Enhanced Vehicle Device Card
Each vehicle now shows:
- **Manufacturer**: Smart
- **Model**: From API (e.g., "Smart #1")
- **Model ID**: Series code
- **HW Version**: Model year
- **SW Version**: Current firmware (updates each poll)
- **Serial Number**: VIN
- **Suggested Area**: Garage

### 3. New Entities Per Vehicle

#### Sensors (~25 new)

| Entity | Device Class | Unit | Notes |
|--------|-------------|------|-------|
| Tyre Pressure FL | PRESSURE | kPa | From existing vehicle status response |
| Tyre Pressure FR | PRESSURE | kPa | |
| Tyre Pressure RL | PRESSURE | kPa | |
| Tyre Pressure RR | PRESSURE | kPa | |
| Tyre Temperature FL | TEMPERATURE | °C | |
| Tyre Temperature FR | TEMPERATURE | °C | |
| Tyre Temperature RL | TEMPERATURE | °C | |
| Tyre Temperature RR | TEMPERATURE | °C | |
| Odometer | DISTANCE | km | From maintenance or TC endpoint |
| Days to Service | — | days | |
| Distance to Service | DISTANCE | km | |
| 12V Battery Voltage | VOLTAGE | V | |
| 12V Battery Level | BATTERY | % | |
| Interior Temperature | TEMPERATURE | °C | From climateStatus |
| Exterior Temperature | TEMPERATURE | °C | From climateStatus |
| Power Mode | ENUM | — | off/accessory/on/cranking |
| Speed | SPEED | km/h | From running state endpoint |
| Last Trip Distance | DISTANCE | km | |
| Last Trip Duration | DURATION | s | |
| Last Trip Energy | ENERGY | kWh | |
| Charging Schedule Start | — | HH:mm | |
| Charging Schedule Status | ENUM | — | active/inactive |
| Climate Schedule Time | — | HH:mm | |
| Geofence Count | — | — | |
| Energy Ranking | — | — | Position among same model |

#### Binary Sensors (~10 new)

| Entity | Device Class | Notes |
|--------|-------------|-------|
| Tyre Warning FL | PROBLEM | Low pressure alert |
| Tyre Warning FR | PROBLEM | |
| Tyre Warning RL | PROBLEM | |
| Tyre Warning RR | PROBLEM | |
| Telematics Connected | CONNECTIVITY | |
| Fridge Active | RUNNING | Smart #1 only |
| Fragrance Active | — | |
| Locker Open | OPENING | Frunk/locker |
| VTM Enabled | — | Theft monitoring |
| Brake Fluid OK | PROBLEM | Inverted (on = problem) |

### 4. Dynamic Entity Visibility
- Entities are only registered when the API returns valid, non-null data
- EU and INTL users may see different entity sets
- Vehicles without accessories (fridge, fragrance, locker) won't show those entities

### 5. Silent Per-Endpoint Failure
- Each endpoint has its own try/except in the coordinator
- A failing endpoint logs at debug level and is skipped
- Other endpoints continue normally
- No single endpoint failure cascades to other entities

## Files Modified

| File | Changes |
|------|---------|
| `const.py` | `DEFAULT_SCAN_INTERVAL=60`, new `SENSITIVE_FIELDS` |
| `models.py` | `PowerMode` enum, ~13 new dataclasses, extended `VehicleStatus` & `VehicleData` |
| `api.py` | ~17 new `async_get_*` methods on `SmartAPI`, extended `_parse_vehicle_status` |
| `coordinator.py` | Wire new endpoints into `_async_fetch_all_vehicles`, enhanced `DeviceInfo` |
| `sensor.py` | ~25 new `SmartSensorEntityDescription` entries, dynamic filtering in `async_setup_entry` |
| `binary_sensor.py` | ~10 new `SmartBinarySensorEntityDescription` entries, dynamic filtering |
| `strings.json` | Translation keys for all new entities |

## Architecture Decisions

1. **No new files** — all code goes into existing files per Constitution Principle III
2. **No parallel API calls** — sequential endpoint calls to avoid rate limiting
3. **kPa for tyre pressure** — not bar (corrects spec assumption; HA handles unit conversion)
4. **Prefer Tier 1 over Tier 2** — when both provide same data, use `/remote-control/` path
5. **Speculative schemas** — most endpoint schemas are inferred; all parsing is defensive with `.get()` and defaults
