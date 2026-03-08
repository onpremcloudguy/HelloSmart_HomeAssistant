# Hello Smart — Home Assistant Integration

A custom Home Assistant integration for **Smart** electric vehicles (#1, #3, #5). Connects to the Smart cloud API to provide real-time vehicle status, charging data, trip history, and accessory information.

## Features

- **Battery & Charging** — SOC, range, voltage, current, time to full, charging schedule
- **Doors & Windows** — Open/closed state for all doors and windows
- **Tyres** — Pressure (kPa) and temperature (°C) for all four tyres with warning alerts
- **Climate** — Interior/exterior temperature, climate schedule, fragrance system
- **Maintenance** — Odometer, days/distance to service, 12V battery, washer fluid, brake fluid
- **Trip Data** — Last trip distance, duration, energy, average/max speed, total distance
- **Accessories** — Mini-fridge, storage locker, fragrance diffuser
- **Security** — Vehicle Theft Monitoring (VTM) settings, geofences
- **Device Tracker** — GPS location from vehicle telematics
- **Firmware** — OTA and FOTA update availability
- **Diagnostics** — Diagnostic trouble codes, telematics connectivity

### Entity Count

| Platform | Count |
|----------|-------|
| Sensor | 53 |
| Binary Sensor | 28 |
| Device Tracker | 1 |
| **Total** | **82** |

## Supported Regions

| Region | Auth Method | Status |
|--------|------------|--------|
| EU | Gigya OAuth (4-step) | Supported |
| INTL (Israel/APAC) | Direct login (3-step) | Supported & tested |

## Installation

### HACS (Recommended)

1. Add this repository as a custom repository in HACS
2. Search for "Hello Smart" and install
3. Restart Home Assistant
4. Go to **Settings → Devices & Services → Add Integration → Hello Smart**

### Manual

1. Copy `custom_components/hello_smart/` to your Home Assistant `config/custom_components/` directory
2. Restart Home Assistant
3. Go to **Settings → Devices & Services → Add Integration → Hello Smart**

## Configuration

The integration is configured through the Home Assistant UI:

| Field | Description |
|-------|-------------|
| **Email** | Your Smart account email |
| **Password** | Your Smart account password |
| **Region** | `EU` or `INTL` |

Data is polled every **60 seconds** (configurable via `DEFAULT_SCAN_INTERVAL`).

## Development

### Docker Debug Environment

A Docker Compose setup is provided for local development:

```bash
docker compose up -d
```

This starts a Home Assistant instance at `http://localhost:8123` with the integration mounted read-only.

### Project Structure

```
custom_components/hello_smart/
├── __init__.py          # Platform setup and entry points
├── api.py               # Smart cloud API client (21 endpoints)
├── auth.py              # Region-aware authentication & HMAC signing
├── binary_sensor.py     # 28 binary sensor entities
├── config_flow.py       # HA config flow UI
├── const.py             # Constants, URLs, signing secrets
├── coordinator.py       # DataUpdateCoordinator (orchestrates all API calls)
├── device_tracker.py    # GPS device tracker entity
├── diagnostics.py       # HA diagnostics download (redacts sensitive data)
├── manifest.json        # Integration manifest
├── models.py            # 18 dataclasses, 4 enums
├── sensor.py            # 53 sensor entities
└── strings.json         # Translation keys
```

## API Documentation

Full API reference with individual endpoint docs, authentication flows, request signing, response schemas, and data models:

| Document | Description |
|----------|-------------|
| [API Overview](API/README.md) | Index of all endpoints |
| [Common Patterns](API/common-patterns.md) | Base URLs, signing, response envelope, error codes |
| [Data Models](API/models.md) | Enumerations and dataclass definitions |
| [Entity Mapping](API/entities.md) | How API data maps to HA entities |
| [Endpoint Docs](API/endpoints/) | Individual endpoint documentation (22 files) |

## License

This project is provided as-is for personal use with Smart vehicles.
