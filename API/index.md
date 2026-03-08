# Smart Vehicle Cloud API Reference

Complete documentation of all GET API endpoints consumed by the Hello Smart Home Assistant integration. These endpoints are reverse-engineered from the Smart mobile app APKs (EU and INTL variants) and validated against the live API.

> **Read-only endpoints only.** POST/PUT command endpoints (lock, unlock, climate control, etc.) are not yet implemented.

---

## Quick Reference

- [Common Patterns](common-patterns.md) — Base URLs, request signing, response envelope, error codes, data types

---

## Endpoints

### Authentication

| Endpoint | Method | Description |
|----------|--------|-------------|
| [EU Login (Gigya)](endpoints/authentication.md#eu-login-gigya) | POST | Multi-step OAuth via Gigya identity provider |
| [INTL Login (3-Step)](endpoints/authentication.md#intl-login-3-step) | POST | Direct login flow for international regions |

### Vehicle Management

| Endpoint | Method | Path | Description |
|----------|--------|------|-------------|
| [List Vehicles](endpoints/list-vehicles.md) | GET | `/device-platform/user/vehicle/secure` | Fetch all linked vehicles |
| [Select Vehicle](endpoints/select-vehicle.md) | POST | `/device-platform/user/session/update` | Set active vehicle for session |

### Vehicle Status

| Endpoint | Method | Path | Description |
|----------|--------|------|-------------|
| [Full Vehicle Status](endpoints/vehicle-status.md) | GET | `/remote-control/vehicle/status/{vin}` | Battery, doors, windows, tyres, GPS, climate |
| [SOC / Charging Detail](endpoints/soc.md) | GET | `/remote-control/vehicle/status/soc/{vin}` | Voltage, current, time to full |
| [Vehicle Running State](endpoints/vehicle-state.md) | GET | `/remote-control/vehicle/status/state/{vin}` | Power mode, speed |

### Telematics & Diagnostics

| Endpoint | Method | Path | Description |
|----------|--------|------|-------------|
| [Telematics Status](endpoints/telematics.md) | GET | `/remote-control/vehicle/telematics/{vin}` | Connectivity, backup battery |
| [Diagnostic History](endpoints/diagnostics.md) | GET | `/remote-control/vehicle/status/history/diagnostic/{vin}` | Recent DTCs |

### Charging & Climate Schedules

| Endpoint | Method | Path | Description |
|----------|--------|------|-------------|
| [Charging Reservation](endpoints/charging-reservation.md) | GET | `/remote-control/charging/reservation/{vin}` | Scheduled charging config |
| [Climate Schedule](endpoints/climate-schedule.md) | GET | `/remote-control/schedule/{vin}` | Climate pre-conditioning schedule |

### Accessories

| Endpoint | Method | Path | Description |
|----------|--------|------|-------------|
| [Mini-Fridge Status](endpoints/fridge-status.md) | GET | `/remote-control/getFridge/status/{vin}` | Fridge on/off, temp, mode |
| [Locker Status](endpoints/locker-status.md) | GET | `/remote-control/getLocker/status/{vin}` | Storage locker open/locked |
| [Locker Secret](endpoints/locker-secret.md) | GET | `/remote-control/locker/secret/{vin}` | Locker PIN configuration |
| [Fragrance System](endpoints/fragrance.md) | GET | `/remote-control/vehicle/fragrance/{vin}` | Fragrance diffuser status |

### Security & Geofencing

| Endpoint | Method | Path | Description |
|----------|--------|------|-------------|
| [VTM Settings](endpoints/vtm-settings.md) | GET | `/remote-control/getVtmSettingStatus` | Vehicle Theft Monitoring config |
| [Geofences](endpoints/geofences.md) | GET | `/geelyTCAccess/tcservices/vehicle/geofence/all/{vin}` | All configured geofences |

### Trip & Distance

| Endpoint | Method | Path | Description |
|----------|--------|------|-------------|
| [Trip Journal V4](endpoints/trip-journal.md) | GET | `/geelyTCAccess/tcservices/vehicle/status/journalLogV4/{vin}` | Trip data with energy metrics |
| [Total Distance](endpoints/total-distance.md) | GET | `/geelyTCAccess/tcservices/vehicle/status/getTotalDistanceByLabel/{vin}` | Cumulative odometer |

### Vehicle Metadata

| Endpoint | Method | Path | Description |
|----------|--------|------|-------------|
| [Capabilities](endpoints/capabilities.md) | GET | `/geelyTCAccess/tcservices/capability/{vin}` | Feature flags / enabled services |
| [Energy Ranking](endpoints/energy-ranking.md) | GET | `/geelyTCAccess/.../ranking/aveEnergyConsumption/vehicleModel/{vin}` | Consumption ranking |
| [Factory Plant Number](endpoints/plant-no.md) | GET | `/geelyTCAccess/tcservices/customer/vehicle/plantNo/{vin}` | Factory identification |

### Firmware Updates

| Endpoint | Method | Path | Description |
|----------|--------|------|-------------|
| [OTA Info](endpoints/ota-info.md) | GET | `https://ota.srv.smart.com/app/info/{vin}` | Firmware versions (different host) |
| [FOTA Notification](endpoints/fota-notification.md) | GET | `/fota/geea/assignment/notification` | Pending update notifications |

---

## Reference

- [Data Models](models.md) — Enumerations, dataclasses, and type definitions
- [Entity Mapping](entities.md) — How API data maps to Home Assistant entities
