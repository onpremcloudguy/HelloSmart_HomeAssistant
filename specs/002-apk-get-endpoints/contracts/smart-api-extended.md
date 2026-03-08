# Smart Vehicle API Contract — Extended GET Endpoints

**Branch**: `002-apk-get-endpoints` | **Date**: 2026-03-08

This document extends the foundation API contract (`001/contracts/smart-api.md`) with all new GET endpoints discovered via APK reverse engineering. These are **third-party contracts** — the integration must conform to them.

**Schema Confidence**: Unless marked CONFIRMED, response schemas are inferred from pySmartHashtag fixtures, APK strings, and Geely platform conventions. Field names and types may differ at runtime. All parsing must be defensive (use `.get()` with defaults).

---

## Common Patterns

### Response Envelope

All endpoints return:
```json
{
  "code": 1000,
  "data": { ... },
  "success": true,
  "message": "operation succeed"
}
```
- `code == 1000` → success
- Any other `code` → error (log and skip)

### Headers

All endpoints below use the same signed headers as the existing vehicle data endpoints:
```
Content-Type: application/json
Accept: application/json
Authorization: Bearer {api_access_token}
X-Operator-Code: {EU_OPERATOR_CODE | INTL_OPERATOR_CODE}
X-App-Id: {EU_APP_ID | INTL_APP_ID}
X-Request-Id: {uuid}
X-Timestamp: {epoch_millis}
X-Signature: {hmac_sha1_signature}
```

### Base URL

All endpoints use `{base_url}` = `https://api.ecloudeu.com` for both EU and INTL (vehicle data endpoints).

---

## Tier 1 — Vehicle Data Endpoints

### 1. Vehicle Running State

```
GET {base_url}/remote-control/vehicle/status/state/{vin}

Headers: [Signed]

Response: 200 JSON (SPECULATIVE)
  {
    "code": 1000,
    "data": {
      "engineStatus": "engine_off",      // "engine_off" | "engine_running" | "engine_cranking"
      "powerMode": "0",                  // "0"=off, "1"=accessory, "2"=on, "3"=cranking
      "speed": "0.0",                    // km/h as string
      "usageMode": "1",
      "carMode": "0"
    }
  }
```

### 2. Trip Journal

```
GET {base_url}/remote-control/vehicle/status/journalLog/{vin}

Headers: [Signed]

Response: 200 JSON (SPECULATIVE)
  {
    "code": 1000,
    "data": {
      "journalLogList": [
        {
          "tripId": "12345",
          "startTime": "1706028240000",       // epoch millis
          "endTime": "1706031840000",
          "distance": "25.3",                 // km
          "duration": "3600",                 // seconds
          "averageSpeed": "25.3",             // km/h
          "energyConsumption": "4.5",         // kWh
          "averageEnergyConsumption": "17.8"  // kWh/100km
        }
      ]
    }
  }
```

### 3. Diagnostic History

```
GET {base_url}/remote-control/vehicle/status/history/diagnostic/{vin}

Headers: [Signed]

Response: 200 JSON (SPECULATIVE)
  {
    "code": 1000,
    "data": {
      "diagnosticList": [
        {
          "dtcCode": "P0001",
          "severity": "1",
          "timestamp": "1706028240000",
          "status": "active"                  // "active" | "resolved"
        }
      ]
    }
  }
```

### 4. Telematics Status

```
GET {base_url}/remote-control/vehicle/telematics/{vin}

Headers: [Signed]

Response: 200 JSON (PARTIALLY CONFIRMED — field names from temStatus block)
  {
    "code": 1000,
    "data": {
      "swVersion": "v1.2.3",
      "hwVersion": "...",
      "imei": "...",
      "connectivityStatus": "connected",     // used for binary sensor
      "powerMode": "0",
      "backupBattery": {
        "voltage": "12.4",
        "stateOfCharge": "95"
      }
    }
  }
```

### 5. Charging Reservation

```
GET {base_url}/remote-control/charging/reservation/{vin}

Headers: [Signed]

Response: 200 JSON (SPECULATIVE)
  {
    "code": 1000,
    "data": {
      "reservationStatus": "active",         // "active" | "inactive"
      "startTime": "22:00",                  // HH:mm local
      "endTime": "06:00",
      "targetSoc": "80"                      // percent
    }
  }
```

### 6. Climate Schedule

```
GET {base_url}/remote-control/schedule/{vin}

Headers: [Signed]

Response: 200 JSON (SPECULATIVE)
  {
    "code": 1000,
    "data": {
      "scheduleList": [
        {
          "scheduleId": "1",
          "enabled": true,
          "scheduledTime": "07:00",
          "temperature": "21.0",
          "duration": 180                     // seconds
        }
      ]
    }
  }
```

### 7. Mini-Fridge Status

```
GET {base_url}/remote-control/getFridge/status/{vin}

Headers: [Signed]

Response: 200 JSON (SPECULATIVE)
  {
    "code": 1000,
    "data": {
      "fridgeStatus": "on",                  // "on" | "off"
      "temperature": "5",                    // °C
      "mode": "cooling"                      // "cooling" | "warming" | "off"
    }
  }
```

### 8. Locker Status

```
GET {base_url}/remote-control/getLocker/status/{vin}

Headers: [Signed]

Response: 200 JSON (SPECULATIVE)
  {
    "code": 1000,
    "data": {
      "lockerStatus": "closed",              // "open" | "closed"
      "lockStatus": "locked"                 // "locked" | "unlocked"
    }
  }
```

### 9. VTM Settings

```
GET {base_url}/remote-control/getVtmSettingStatus

Headers: [Signed]
Note: No {vin} — uses selected vehicle session. Call async_select_vehicle first.

Response: 200 JSON (SPECULATIVE)
  {
    "code": 1000,
    "data": {
      "vtmEnabled": true,
      "notificationEnabled": true,
      "geofenceAlertEnabled": true,
      "movementAlertEnabled": true
    }
  }
```

### 10. Fragrance System

```
GET {base_url}/remote-control/vehicle/fragrance/{vin}

Headers: [Signed]

Response: 200 JSON (LOW-SPECULATIVE — fragActive confirmed in climateStatus)
  {
    "code": 1000,
    "data": {
      "fragranceActive": false,
      "fragranceLevel": "high",              // "high" | "medium" | "low" | "empty"
      "fragranceType": "1"
    }
  }
```

### 11. Locker Secret Status

```
GET {base_url}/remote-control/locker/secret/{vin}

Headers: [Signed]

Response: 200 JSON (SPECULATIVE)
  {
    "code": 1000,
    "data": {
      "hasSecret": true,
      "secretSet": true                      // whether PIN configured (NOT the PIN itself)
    }
  }
```

### 12. Standalone Location

```
GET {base_url}/remote-control/vehicle/status/location

Headers: [Signed]
Note: No {vin} — uses selected vehicle session.

Response: 200 JSON (PARTIALLY CONFIRMED — same structure as basicVehicleStatus.position)
  {
    "code": 1000,
    "data": {
      "position": {
        "latitude": "123456789",
        "longitude": "987654321",
        "altitude": "105",
        "posCanBeTrusted": "true"
      },
      "updateTime": "1706028240000"
    }
  }
```

---

## Tier 2 — Telematics Cloud Endpoints

### 13. Vehicle Capabilities

```
GET {base_url}/geelyTCAccess/tcservices/capability/{vin}

Headers: [Signed]

Response: 200 JSON (SPECULATIVE — serviceId values confirmed in pySmartHashtag)
  {
    "code": 1000,
    "data": {
      "capabilities": [
        {
          "serviceId": "RCE_2",
          "enabled": true,
          "version": "1.0"
        }
      ]
    }
  }
```

### 14. Geofences

```
GET {base_url}/geelyTCAccess/tcservices/vehicle/geofence/all/{vin}

Headers: [Signed]

Response: 200 JSON (SPECULATIVE)
  {
    "code": 1000,
    "data": {
      "geofences": [
        {
          "geofenceId": "1",
          "name": "Home",
          "centerLatitude": "48.1234",
          "centerLongitude": "11.5678",
          "radius": "500",
          "enabled": true
        }
      ]
    }
  }
```

### 15. Trip Journal V4

```
GET {base_url}/geelyTCAccess/tcservices/vehicle/status/journalLogV4/{vin}

Headers: [Signed]

Response: 200 JSON (SPECULATIVE — extension of Tier 1 #2)
  {
    "code": 1000,
    "data": {
      "journalLogs": [
        {
          "tripId": "...",
          "startTime": "1706028240000",
          "endTime": "1706031840000",
          "distance": "25.3",
          "duration": "3600",
          "averageSpeed": "25.3",
          "energyConsumption": "4.5",
          "averageEnergyConsumption": "17.8",
          "maxSpeed": "120.0",
          "regeneratedEnergy": "1.2",
          "startAddress": "...",
          "endAddress": "..."
        }
      ],
      "totalTrips": 42
    }
  }
```

### 16. Total Distance by Label

```
GET {base_url}/geelyTCAccess/tcservices/vehicle/status/getTotalDistanceByLabel/{vin}

Headers: [Signed]

Response: 200 JSON (PARTIALLY CONFIRMED — odometer field exists in fixture)
  {
    "code": 1000,
    "data": {
      "totalDistance": "12345.6",            // km
      "label": "total",
      "updateTime": "1706028240000"
    }
  }
```

### 17. Energy Consumption Ranking

```
GET {base_url}/geelyTCAccess/tcservices/vehicle/status/ranking/aveEnergyConsumption/vehicleModel/{vin}?topn=100

Headers: [Signed]

Response: 200 JSON (SPECULATIVE)
  {
    "code": 1000,
    "data": {
      "myRanking": 42,
      "myValue": "17.8",                    // kWh/100km
      "totalParticipants": 100
    }
  }
```

### 18. Factory Plant Number

```
GET {base_url}/geelyTCAccess/tcservices/customer/vehicle/plantNo/{vin}

Headers: [Signed]

Response: 200 JSON (SPECULATIVE)
  {
    "code": 1000,
    "data": {
      "plantNo": "..."
    }
  }
```

---

## Tier 3 — Auxiliary Endpoints

### 19. FOTA Notification

```
GET {base_url}/fota/geea/assignment/notification

Headers: [Signed]

Response: 200 JSON (SPECULATIVE)
  {
    "code": 1000,
    "data": {
      "hasNotification": true,
      "notifications": [
        {
          "assignmentId": "...",
          "version": "...",
          "status": "available"
        }
      ]
    }
  }
```

---

## Endpoints NOT Implemented (Skipped)

The following endpoints from the APK analysis are intentionally skipped:

| Endpoint | Reason |
|----------|--------|
| `/geelyTCAccess/tcservices/vehicle/telematics/{vin}` | Duplicate of Tier 1 #4 |
| `/geelyTCAccess/tcservices/vehicle/status/qrvs/{vin}` | Subset of data already in vehicle status |
| `/geelyTCAccess/tcservices/vehicle/status/powerMode/{vin}` | Available from Tier 1 #1 |
| `/geelyTCAccess/tcservices/vehicle/status/historyV2/{vin}` | Superseded by journalLogV4 |
| `/remote-control/vehicle/status/location` | Already in main vehicle status response |
| `/gid/vehicle/{userId}` | User management, not vehicle data |
| `/member/user/{userId}` | User management, not vehicle data |
| `/platform/user/info/{userId}` | User management, not vehicle data |
| `/remote-control/user/authorization/selectStatus` | Auth management |
| `/remote-control/user/authorization/selectRecord` | Auth management |
| `/remote-control/user/authorization/vehicle/status/{vin}` | Auth management |
| `/profile/concurrently/switch/status` | Profile management |
| `/profile/notification` | In-app notifications, not vehicle data |
| `/security2/v2/weather/index` | Weather data — HA has dedicated weather integrations |
| `/security2/v2/weather/observe` | Weather data — HA has dedicated weather integrations |
| `/geelyTCAccess/tcservices/vehicle/status/ranking/odometer/...` | Low value |
| `/geelyTCAccess/tcservices/vehicle/status/ranking/aveFuelConsumption/...` | N/A for EVs |
| `/hf-capability-center/api/v2/ability/{vin}` | Duplicate of capability endpoint |

**Net new endpoints to implement**: 19 (Tier 1: 11, Tier 2: 5, Tier 3: 1, from existing response: 2 groups — tyre/maintenance data)

---

## Parsing Notes

1. **All numeric values are strings** — parse with `float()` / `int()` and wrap in try/except
2. **Boolean values are string "0"/"1"** or `"true"`/`"false"` — use `str(v).lower() in ("1", "true")`
3. **Timestamps are epoch milliseconds as strings** — divide by 1000 for `datetime.fromtimestamp()`
4. **Null/empty handling** — always use `data.get("field")`, never `data["field"]`
5. **kPa for tyre pressure** — spec assumed bar, but pySmartHashtag confirms kPa
