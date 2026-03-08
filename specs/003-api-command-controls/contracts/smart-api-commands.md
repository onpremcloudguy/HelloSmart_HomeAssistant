# Smart API Command Contracts

**Feature**: 003-api-command-controls  
**Date**: 2025-07-24  
**Source**: pySmartHashtag library, APK reverse engineering

---

## C-001: Vehicle Command (Telematics PUT)

All vehicle commands are sent via a single multiplexed endpoint.

### Endpoint

```
PUT /remote-control/vehicle/telematics/{vin}
```

### Headers

Standard HMAC-SHA1 signed headers (same as GET endpoints):

```
x-app-id: SmartAPPEU (EU) | SmartAPPGlobal (INTL)
x-api-signature-version: 1.0
x-api-signature-nonce: <random_hex>
x-api-signature: <hmac_sha1_signature>
x-timestamp: <epoch_ms>
Content-Type: application/json
Authorization: Bearer <api_access_token>
```

The HMAC signature includes: nonce, empty params, timestamp, method (`PUT`), URL path, JSON body.

### Request Body

```json
{
  "creator": "tc",
  "command": "<start|stop>",
  "serviceId": "<SERVICE_ID>",
  "timestamp": "<epoch_milliseconds_string>",
  "operationScheduling": {
    "duration": <int>,
    "interval": 0,
    "occurs": 1,
    "recurrentOperation": false
  },
  "serviceParameters": [
    {"key": "<param_key>", "value": "<param_value>"}
  ]
}
```

**Important**: The JSON body MUST be serialized with no spaces: `json.dumps(payload).replace(" ", "")`

### Response

```json
{
  "success": true
}
```

Or on failure:

```json
{
  "success": false,
  "message": "<error description>"
}
```

**Note**: The response may be wrapped in the standard `{"code": 1000, "data": {"success": true}}` envelope. Verify during implementation.

### Error Codes

| Code | Meaning | Action |
|------|---------|--------|
| HTTP 200 + `success: true` | Command accepted | Optimistic update + delayed refresh |
| HTTP 200 + `success: false` | Command rejected | Revert optimistic state, notify user |
| HTTP 401 | Auth expired | Trigger token refresh, retry |
| HTTP 403 | Permission denied | Notify user, do not retry |
| HTTP 429 | Rate limited | Wait and retry after backoff |
| HTTP 5xx | Server error | Notify user, do not retry |

---

## C-002: Door Lock Command

### Lock

```json
{
  "creator": "tc",
  "command": "start",
  "serviceId": "RDL_2",
  "timestamp": "1721827200000",
  "operationScheduling": {
    "duration": 6,
    "interval": 0,
    "occurs": 1,
    "recurrentOperation": false
  },
  "serviceParameters": []
}
```

### Unlock

```json
{
  "creator": "tc",
  "command": "start",
  "serviceId": "RDU_2",
  "timestamp": "1721827200000",
  "operationScheduling": {
    "duration": 6,
    "interval": 0,
    "occurs": 1,
    "recurrentOperation": false
  },
  "serviceParameters": []
}
```

**Confidence**: Medium — service IDs confirmed from APK, payload structure inferred from pattern. Empty `serviceParameters` is an assumption.

---

## C-003: Climate Pre-Conditioning Command

### Start Climate (22°C)

```json
{
  "creator": "tc",
  "command": "start",
  "serviceId": "RCE_2",
  "timestamp": "1721827200000",
  "operationScheduling": {
    "duration": 180,
    "interval": 0,
    "occurs": 1,
    "recurrentOperation": false
  },
  "serviceParameters": [
    {"key": "rce.conditioner", "value": "1"},
    {"key": "rce.temp", "value": "22.0"}
  ]
}
```

### Start Climate with Seat Heating

```json
{
  "serviceParameters": [
    {"key": "rce.conditioner", "value": "1"},
    {"key": "rce.temp", "value": "22.0"},
    {"key": "rce.heat", "value": "front-left"},
    {"key": "rce.level", "value": "3"},
    {"key": "rce.heat", "value": "front-right"},
    {"key": "rce.level", "value": "2"}
  ]
}
```

### Stop Climate

```json
{
  "creator": "tc",
  "command": "stop",
  "serviceId": "RCE_2",
  "timestamp": "1721827200000",
  "operationScheduling": {
    "duration": 180,
    "interval": 0,
    "occurs": 1,
    "recurrentOperation": false
  },
  "serviceParameters": [
    {"key": "rce.conditioner", "value": "1"}
  ]
}
```

**Constraints**:
- Temperature range: 16.0–30.0°C (float, one decimal)
- Seat heat levels: 0–3 (0 = off)
- Seat heat locations: `"front-left"`, `"front-right"`, `"steering_wheel"`
- Duration: 180 minutes (max pre-conditioning time)

**Confidence**: High — confirmed by pySmartHashtag implementation and test suite.

---

## C-004: Charging Start/Stop Command

### Start Charging

```json
{
  "creator": "tc",
  "command": "start",
  "serviceId": "rcs",
  "timeStamp": "1721827200000",
  "operationScheduling": {
    "scheduledTime": null,
    "interval": 0,
    "occurs": 1,
    "recurrentOperation": 0,
    "duration": 6
  },
  "serviceParameters": [
    {"key": "operation", "value": "1"},
    {"key": "rcs.restart", "value": "1"}
  ]
}
```

### Stop Charging

```json
{
  "creator": "tc",
  "command": "start",
  "serviceId": "rcs",
  "timeStamp": "1721827200000",
  "operationScheduling": {
    "scheduledTime": null,
    "interval": 0,
    "occurs": 1,
    "recurrentOperation": 0,
    "duration": 6
  },
  "serviceParameters": [
    {"key": "operation", "value": "0"},
    {"key": "rcs.terminate", "value": "1"}
  ]
}
```

**Important differences from climate**:
- `serviceId` is lowercase `"rcs"` (not uppercase)
- `command` is always `"start"` even for stop — the `serviceParameters` control the action
- Timestamp field is `"timeStamp"` (camelCase S) not `"timestamp"`
- `operationScheduling.recurrentOperation` is `0` (int) not `false` (bool)
- `operationScheduling.scheduledTime` is present and set to `null`

**Confidence**: High — confirmed by pySmartHashtag implementation and test suite.

---

## C-005: Horn & Light Commands

### Horn Only

```json
{
  "creator": "tc",
  "command": "start",
  "serviceId": "RHL",
  "timestamp": "1721827200000",
  "operationScheduling": {
    "duration": 6,
    "interval": 0,
    "occurs": 1,
    "recurrentOperation": false
  },
  "serviceParameters": [
    {"key": "rhl.horn", "value": "1"}
  ]
}
```

### Flash Lights Only

```json
{
  "serviceParameters": [
    {"key": "rhl.flash", "value": "1"}
  ]
}
```

### Find My Car (Horn + Flash)

```json
{
  "serviceParameters": [
    {"key": "rhl.horn", "value": "1"},
    {"key": "rhl.flash", "value": "1"}
  ]
}
```

**Confidence**: Medium — service ID confirmed from APK, parameter key names are inferred from the `rce.*`/`rcs.*` naming convention.

---

## C-006: Window Close Command

```json
{
  "creator": "tc",
  "command": "start",
  "serviceId": "RWS_2",
  "timestamp": "1721827200000",
  "operationScheduling": {
    "duration": 6,
    "interval": 0,
    "occurs": 1,
    "recurrentOperation": false
  },
  "serviceParameters": [
    {"key": "rws.close", "value": "1"}
  ]
}
```

**Confidence**: Low — service ID from APK, payload structure speculative. Alternative service ID `RWR` (Remote Window Raise) may be the correct one.

---

## C-007: Fridge Toggle Command

```json
{
  "creator": "tc",
  "command": "start",
  "serviceId": "UFR",
  "timestamp": "1721827200000",
  "operationScheduling": {
    "duration": 6,
    "interval": 0,
    "occurs": 1,
    "recurrentOperation": false
  },
  "serviceParameters": [
    {"key": "ufr.status", "value": "1"}
  ]
}
```

For off: `"value": "0"`

**Confidence**: Low — service ID from APK, exact parameter format speculative. The APK shows `ColdWarmBoxRequest` as a separate request class which might use different parameter conventions.

---

## C-008: Charging Schedule Update

### Endpoint

```
PUT /remote-control/charging/reservation/{vin}
```

### Request Body (inferred)

```json
{
  "startTime": "22:00",
  "endTime": "06:00",
  "targetSoc": 80,
  "active": true
}
```

**Confidence**: Low — endpoint path confirmed from APK, body format is speculative based on the corresponding GET response structure from the existing `ChargingReservation` model.

---

## C-009: Climate Schedule Update

### Endpoint

```
PUT /remote-control/schedule/{vin}
```

### Request Body (inferred)

```json
{
  "enabled": true,
  "scheduledTime": "07:30",
  "temperature": 22.0,
  "duration": 30
}
```

**Confidence**: Low — endpoint path confirmed from APK, body format speculative.

---

## Authentication Pre-requisite

Before any command in C-001 through C-009, the caller MUST:

1. Ensure a valid `api_access_token` (refresh if expired)
2. Call `POST /device-platform/user/session/update` with `{"vin": "<vin>", "sessionToken": "<token>", "language": ""}` to select the active vehicle session
3. Then send the command

This matches the existing flow in the `hello_smart` integration's `async_select_vehicle()` method.
