# Common Patterns

Shared conventions across all Smart vehicle cloud API endpoints.

[← Back to API Reference](README.md)

---

## Base URLs

| Purpose | URL | Used By |
|---------|-----|---------|
| Vehicle data (EU & INTL) | `https://api.ecloudeu.com` | All vehicle GET/POST endpoints |
| INTL session exchange | `https://apiv2.ecloudeu.com` | INTL auth step 3 only |
| INTL login | `https://sg-app-api.smart.com` | INTL auth steps 1–2 |
| INTL VC service | `https://sg-app-api.smart.com/vc` | Vehicle ability endpoint (uses Alibaba Cloud API Gateway signing) |
| INTL image CDN | `https://sg-app.smart.com` | Color-matched vehicle images |
| EU login (Gigya) | `https://auth.smart.com` | EU authentication |
| EU context | `https://awsapi.future.smart.com` | EU session exchange |
| EU VC service | `https://vehicle.vbs.srv.smart.com` | Vehicle ability endpoint (EU) |
| OTA firmware | `https://ota.srv.smart.com` | OTA endpoint only |

---

## Authentication & Signing

All vehicle data endpoints require **HMAC-SHA1 signed headers**. The integration builds these automatically via `build_signed_headers()`.

### Required Headers

| Header | Description |
|--------|-------------|
| `x-app-id` | App identifier (`SmartAPPEU` or `SMARTAPP-ISRAEL`) |
| `accept` | `application/json;responseformat=3` |
| `x-operator-code` | Region code (`SMART` or `SMART-ISRAEL`) |
| `x-device-identifier` | Random hex device ID (16 chars EU, 32 chars INTL) |
| `x-env-type` | Always `production` |
| `x-api-signature-version` | Always `1.0` |
| `x-api-signature-nonce` | Random hex (EU) or UUID (INTL) |
| `x-timestamp` | Epoch milliseconds as string |
| `x-signature` | HMAC-SHA1 signature (see below) |
| `authorization` | API access token (after auth) |
| `content-type` | `application/json; charset=utf-8` (EU) or `application/json` (INTL) |

### Signature Computation

```
payload = "{accept}\nx-api-signature-nonce:{nonce}\nx-api-signature-version:1.0\n\n{url_params}\n{body_md5}\n{timestamp}\n{method}\n{path}"

signature = base64(hmac_sha1(signing_secret, payload))
```

- **EU signing secret**: Base64-decoded `NzRlNzQ2OWFmZjUwNDJiYmJlZDdiYmIxYjM2YzE1ZTk=`
- **INTL signing secret**: `30fb4a7b7fab4e2e8b52120d0087efdd` (raw bytes)
- `body_md5`: Base64-encoded MD5 of request body, or `1B2M2Y8AsgTpgAmY7PhCfg==` for empty body
- INTL GET requests URL-encode query parameter values in the signature

### Region Differences

| Aspect | EU | INTL |
|--------|-----|------|
| App ID (vehicle API) | `SmartAPPEU` | `SMARTAPP-ISRAEL` |
| App ID (auth) | `SmartAPPEU` | `SmartAPPGlobal` |
| Operator Code | `SMART` | `SMART-ISRAEL` |
| Device ID length | 16 hex chars | 32 hex chars |
| Nonce format | Random hex | UUID v4 |
| Content-Type | `application/json; charset=utf-8` | `application/json` |
| Signing secret | Base64-encoded | Raw hex bytes |

---

### VC Signing (Alibaba Cloud API Gateway) {#vc-signing}

The [Vehicle Ability](endpoints/vehicle-ability.md) endpoint uses a completely different signing scheme: **Alibaba Cloud API Gateway HMAC-SHA256**. This is implemented in `build_vc_signed_headers()` (separate from the standard `build_signed_headers()`).

```
string_to_sign = "GET\n{Accept}\n\n{Content-Type}\n{Date}\nx-ca-key:{key}\nx-ca-nonce:{nonce}\nx-ca-signature-method:HmacSHA256\nx-ca-timestamp:{ts}\n{path}"

signature = base64(hmac_sha256(vc_app_secret, string_to_sign))
```

| Header | Description |
|--------|-------------|
| `x-ca-key` | App key from native JNI library |
| `x-ca-nonce` | UUID v4 |
| `x-ca-timestamp` | Epoch milliseconds |
| `x-ca-signature-method` | `HmacSHA256` |
| `x-ca-signature-headers` | Comma-separated sorted `x-ca-*` header names |
| `x-ca-signature` | Base64 HMAC-SHA256 signature |
| `Xs-Auth-Token` | `idToken` from INTL Gigya login |

> The signature key pair is extracted from `libnative-lib.so` in the INTL APK via JNI functions `getAppKeyReleaseFromJni` and `getAppSecretReleaseFromJni`.

---

## Response Envelope

All endpoints return a standard JSON envelope:

```json
{
  "code": 1000,
  "data": { ... },
  "success": true,
  "message": "operation succeed"
}
```

The integration checks `code == 1000` for success and extracts the `data` field.

---

## Error Codes

### API-Level Codes

| Code | Meaning | Integration Handling |
|------|---------|---------------------|
| `1000` | Success | Parse `data` field |
| `1400` | Missing required parameter | Logged at debug, endpoint skipped |
| `1402` | Token expired | Triggers re-authentication |
| `1405` | Resource not found | Logged at debug, endpoint skipped |
| `1445` | Signature verification failed | Logged at debug, endpoint skipped |
| `8006` | Vehicle not linked | Raises `VehicleNotLinkedError` |
| `8153` | Connection interruption / service error | Logged at debug, endpoint skipped |

### HTTP-Level Errors

| Status | Meaning | Integration Handling |
|--------|---------|---------------------|
| `401` | Unauthorized | Triggers re-authentication |
| `403` | Forbidden | Endpoint skipped (e.g., OTA by region) |
| `429` | Rate limited | `RateLimitedError` with `Retry-After` |

### Exception Hierarchy

```
SmartAPIError (base)
├── TokenExpiredError      # code 1402 or HTTP 401
├── VehicleNotLinkedError  # code 8006
└── RateLimitedError       # HTTP 429
```

---

## Data Types

All API responses encode values as **strings**, even numeric and boolean fields:

| Type | API Format | Example | Parse Method |
|------|-----------|---------|-------------|
| Integer | String | `"241"` | `int(value)` |
| Float | String | `"241.648"` | `float(value)` |
| Boolean | String `"0"`/`"1"` or `"true"`/`"false"` | `"1"` | `str(v) == "1"` |
| Timestamp | Epoch milliseconds as string | `"1706028240000"` | `datetime.fromtimestamp(int(v) / 1000)` |
| Enum | String | `"engine_off"` | Direct string match |

The integration uses safe parsing helpers (`_safe_float`, `_safe_int`, `_safe_bool`) that return `None` on unparseable values rather than raising exceptions.

---

## URL Validation

All outbound requests are validated against a URL allowlist:

```
api.ecloudeu.com
apiv2.ecloudeu.com
sg-app-api.smart.com
auth.smart.com
awsapi.future.smart.com
ota.srv.smart.com
```

Only HTTPS requests are permitted. Requests to unlisted hosts are rejected with `SmartAPIError`.

---

## Vehicle Commands (PUT)

Vehicle control commands are sent via PUT to the telematics endpoint:

```http
PUT {base_url}/remote-control/vehicle/telematics/{vin}
```

Headers: Standard [signed headers](#required-headers) with `authorization` token. The request body must be serialised with **no spaces** (`json.dumps(payload, separators=(",",":"))`).

### Command Payload Envelope

```json
{
  "creator": "tc",
  "command": "start",
  "serviceId": "RDL_2",
  "timestamp": "1706028240000",
  "operationScheduling": {
    "duration": 6,
    "interval": 0,
    "occurs": 1,
    "recurrentOperation": false
  },
  "serviceParameters": [
    {"key": "param.name", "value": "param_value"}
  ]
}
```

| Field | Type | Description |
|-------|------|-------------|
| `creator` | string | Always `"tc"` |
| `command` | string | `"start"` or `"stop"` |
| `serviceId` | string | Service identifier (see table below) |
| `timestamp` | string | Epoch milliseconds |
| `operationScheduling.duration` | int | Command duration in minutes |
| `operationScheduling.interval` | int | Always `0` |
| `operationScheduling.occurs` | int | Always `1` |
| `operationScheduling.recurrentOperation` | bool/int | `false` (or `0` for charging) |
| `serviceParameters` | array | Key/value pairs specific to each service |

> **Charging exception**: The `rcs` service uses `"timeStamp"` (camelCase) and `"recurrentOperation": 0` (integer) instead of the standard `"timestamp"` and `false`.

### Service IDs & Parameters

#### Door Lock / Unlock

| Service ID | Command | Parameters | Description |
|------------|---------|------------|-------------|
| `RDL_2` | `start` | *(none)* | Lock all doors |
| `RDU_2` | `start` | *(none)* | Unlock all doors |

#### Climate Control

| Service ID | Command | Parameters | Description |
|------------|---------|------------|-------------|
| `RCE_2` | `start` | `rce.conditioner=1`, `rce.temp={temp}` | Start HVAC at target temperature |
| `RCE_2` | `stop` | `rce.conditioner=1` | Stop HVAC |

- Temperature is in °C as a string (e.g., `"22"`)
- Default duration is 30 minutes

#### Seat Heating

| Service ID | Command | Parameters | Description |
|------------|---------|------------|-------------|
| `RSH` | `start` | `rsh.seat={seat}`, `rsh.level={level}` | Set seat heating level |

**Seat keys**: `front-left`, `front-right`, `steering_wheel`

**Level values**: `0` (off), `1` (low), `2` (medium), `3` (high)

#### Seat Ventilation

| Service ID | Command | Parameters | Description |
|------------|---------|------------|-------------|
| `RSV` | `start` | `rsv.seat={seat}`, `rsv.level={level}` | Set seat ventilation level |

**Seat keys**: `front-left`

**Level values**: `0` (off), `1` (low), `2` (medium), `3` (high)

#### Horn & Lights (Find My Car)

| Service ID | Command | Parameters | Description |
|------------|---------|------------|-------------|
| `RHL` | `start` | `rhl.horn=1` | Sound horn |
| `RHL` | `start` | `rhl.flash=1` | Flash lights |
| `RHL` | `start` | `rhl.horn=1`, `rhl.flash=1` | Find my car (horn + flash) |

#### Windows

| Service ID | Command | Parameters | Description |
|------------|---------|------------|-------------|
| `RWS_2` | `start` | `rws.close=1` | Close all windows |

#### Charging

| Service ID | Command | Parameters | Description |
|------------|---------|------------|-------------|
| `rcs` | `start` | `operation=1`, `rcs.restart=1` | Start charging |
| `rcs` | `start` | `operation=0`, `rcs.terminate=1` | Stop charging |

> Note: Charging uses `command: "start"` for **both** start and stop — the `operation` parameter controls the action.

#### Mini-Fridge

| Service ID | Command | Parameters | Description |
|------------|---------|------------|-------------|
| `UFR` | `start` | `ufr.status=1` | Turn on fridge |
| `UFR` | `stop` | `ufr.status=0` | Turn off fridge |

#### Fragrance Diffuser

| Service ID | Command | Parameters | Description |
|------------|---------|------------|-------------|
| `RFD_2` | `start` | `rfd.status=1` | Turn on fragrance |
| `RFD_2` | `stop` | `rfd.status=0` | Turn off fragrance |

#### Vehicle Tracking (VTM)

| Service ID | Command | Parameters | Description |
|------------|---------|------------|-------------|
| `VTM` | `start` | `vtm.enabled=1` | Enable vehicle tracking |
| `VTM` | `stop` | `vtm.enabled=0` | Disable vehicle tracking |

#### Locker

| Service ID | Command | Parameters | Description |
|------------|---------|------------|-------------|
| `RPC` | `start` | `rpc.lock=1` | Lock storage locker |
| `RPC` | `start` | `rpc.unlock=1` | Unlock storage locker |

### Command Response

```json
{
  "code": 1000,
  "data": { ... },
  "success": true,
  "message": "operation succeed"
}
```

The integration checks top-level `success` first, then falls back to `data.success`.

### Command Flow

1. **Select vehicle** — `POST /device-platform/user/session/update` with the target VIN
2. **Send command** — `PUT /remote-control/vehicle/telematics/{vin}` with the payload
3. **Cooldown** — 5-second per-VIN cooldown between commands
4. **Delayed refresh** — 8-second delay before polling for updated state

### Charging Reservation (PUT)

```http
PUT {base_url}/remote-control/charging/reservation/{vin}
```

Updates the scheduled charging configuration. Body is the updated reservation object — see [Charging Reservation](endpoints/charging-reservation.md).

### Climate Schedule (PUT)

```http
PUT {base_url}/remote-control/schedule/{vin}
```

Updates the climate pre-conditioning schedule. Body is the updated schedule object — see [Climate Schedule](endpoints/climate-schedule.md).
