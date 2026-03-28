# Smart Vehicle Cloud API Reference

Complete documentation of all API endpoints consumed by the Hello Smart Home Assistant integration. These endpoints are reverse-engineered from the Smart mobile app APKs (EU and INTL variants) and validated against the live API.

---

## Documentation

| Document | Description |
|----------|-------------|
| [Common Patterns](common-patterns.md) | Base URLs, request signing, response envelope, error codes, command controls |
| [Endpoint Index](index.md) | Quick-reference table for all 22+ endpoints |
| [Data Models](models.md) | Enumerations, dataclasses, and type definitions |
| [Entity Mapping](entities.md) | How API data maps to Home Assistant entities |

## Endpoints

### Authentication
- [EU Login (Gigya)](endpoints/authentication.md#eu-login-gigya)
- [INTL Login (3-Step)](endpoints/authentication.md#intl-login-3-step)

### Vehicle Management
- [List Vehicles](endpoints/list-vehicles.md) — `GET /device-platform/user/vehicle/secure`
- [Select Vehicle](endpoints/select-vehicle.md) — `POST /device-platform/user/session/update`

### Vehicle Status
- [Full Vehicle Status](endpoints/vehicle-status.md) — `GET /remote-control/vehicle/status/{vin}`
- [SOC / Charging Detail](endpoints/soc.md) — `GET /remote-control/vehicle/status/soc/{vin}`
- [Vehicle Running State](endpoints/vehicle-state.md) — `GET /remote-control/vehicle/status/state/{vin}`

### Telematics & Diagnostics
- [Telematics Status](endpoints/telematics.md) — `GET /remote-control/vehicle/telematics/{vin}`
- [Diagnostic History](endpoints/diagnostics.md) — `GET /remote-control/vehicle/status/history/diagnostic/{vin}`

### Charging & Climate Schedules
- [Charging Reservation](endpoints/charging-reservation.md) — `GET /remote-control/charging/reservation/{vin}`
- [Climate Schedule](endpoints/climate-schedule.md) — `GET /remote-control/schedule/{vin}`

### Accessories
- [Mini-Fridge Status](endpoints/fridge-status.md) — `GET /remote-control/getFridge/status/{vin}`
- [Locker Status](endpoints/locker-status.md) — `GET /remote-control/getLocker/status/{vin}`
- [Locker Secret](endpoints/locker-secret.md) — `GET /remote-control/locker/secret/{vin}`
- [Fragrance System](endpoints/fragrance.md) — `GET /remote-control/vehicle/fragrance/{vin}`

### Security & Geofencing
- [VTM Settings](endpoints/vtm-settings.md) — `GET /remote-control/getVtmSettingStatus`
- [Geofences](endpoints/geofences.md) — `GET /geelyTCAccess/tcservices/vehicle/geofence/all/{vin}`

### Trip & Distance
- [Trip Journal V4](endpoints/trip-journal.md) — `GET /geelyTCAccess/.../journalLogV4/{vin}`
- [Total Distance](endpoints/total-distance.md) — `GET /geelyTCAccess/.../getTotalDistanceByLabel/{vin}`

### Vehicle Metadata
- [Capabilities](endpoints/capabilities.md) — `GET /geelyTCAccess/tcservices/capability/{vin}`
- [Energy Ranking](endpoints/energy-ranking.md) — `GET /geelyTCAccess/.../ranking/.../vehicleModel/{vin}`
- [Factory Plant Number](endpoints/plant-no.md) — `GET /geelyTCAccess/.../plantNo/{vin}`

### Firmware Updates
- [OTA Info](endpoints/ota-info.md) — `GET https://ota.srv.smart.com/app/info/{vin}`
- [FOTA Notification](endpoints/fota-notification.md) — `GET /fota/geea/assignment/notification`

