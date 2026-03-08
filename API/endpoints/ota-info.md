# OTA Info

Current and target firmware versions for the vehicle.

[← Back to API Reference](../README.md) · [Common Patterns](../common-patterns.md)

---

## Request

```http
GET https://ota.srv.smart.com/app/info/{vin}
```

| Parameter | Location | Required | Description |
|-----------|----------|----------|-------------|
| `vin` | Path | Yes | Vehicle VIN |

### Headers

> **Different from standard endpoints.** This endpoint does NOT use HMAC signing. It uses simple token headers instead.

| Header | Value |
|--------|-------|
| `id-token` | Device ID |
| `access_token` | API access token |
| `content-type` | `application/json` |

---

## Response

> **Note:** This endpoint does **not** use the standard response envelope. It returns a flat JSON object.

```json
{
  "currentVersion": "1.2.3",
  "targetVersion": "1.3.0"
}
```

### Response Fields

| Field | Type | Description |
|-------|------|-------------|
| `currentVersion` | string | Currently installed firmware version |
| `targetVersion` | string | Available firmware version |

---

## Data Model

Returns: [`OTAInfo`](../models.md#otainfo)

| Model Field | Source |
|-------------|--------|
| `current_version` | `currentVersion` |
| `target_version` | `targetVersion` |
| `update_available` | Computed: `current_version != target_version` |

---

## Related Entities

| Entity | Platform | Device Class |
|--------|----------|-------------|
| `current_firmware_version` | sensor | — |
| `target_firmware_version` | sensor | — |
| `update_available` | binary_sensor | update |

---

## Known Issues

- Returns HTTP `403` (Forbidden) on INTL/APAC regions
- Different host (`ota.srv.smart.com`) from all other endpoints
- No HMAC signing required — uses simple token-based auth
- The `sw_version` from this endpoint is used in HA DeviceInfo

---

## Related

- [FOTA Notification](fota-notification.md) — Pending update notifications
- Source: [`api.py → async_get_ota_info()`](../../custom_components/hello_smart/api.py)
