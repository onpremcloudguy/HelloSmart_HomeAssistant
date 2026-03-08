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
| EU login (Gigya) | `https://auth.smart.com` | EU authentication |
| EU context | `https://awsapi.future.smart.com` | EU session exchange |
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
