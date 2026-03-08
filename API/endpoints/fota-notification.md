# FOTA Notification

Firmware-Over-The-Air update notification status.

[← Back to API Reference](../README.md) · [Common Patterns](../common-patterns.md)

---

## Request

```http
GET {base_url}/fota/geea/assignment/notification
```

> **Note:** No `{vin}` in the path — uses the [selected vehicle session](select-vehicle.md).

### Headers

Standard [signed headers](../common-patterns.md#required-headers) with `authorization` token.

---

## Response

```json
{
  "code": 1000,
  "data": {
    "notifications": [
      {
        "assignmentId": "abc123",
        "version": "2.0.1",
        "status": "available"
      }
    ]
  }
}
```

### Response Fields

| Field | Type | Description |
|-------|------|-------------|
| `notifications` | array | List of pending FOTA update notifications |

### Notification Entry

| Field | Type | Description |
|-------|------|-------------|
| `assignmentId` | string | Update assignment identifier |
| `version` | string | Firmware version available |
| `status` | string | Notification status |

---

## Data Model

Returns: [`FOTANotification`](../models.md#fotanotification)

| Model Field | Source |
|-------------|--------|
| `has_notification` | `len(notifications) > 0` |
| `pending_count` | `len(notifications)` |

---

## Related Entities

| Entity | Platform | Device Class |
|--------|----------|-------------|
| `fota_available` | binary_sensor | update |
| `fota_pending_count` | sensor | — |

---

## Related

- [OTA Info](ota-info.md) — Current and target firmware versions
- [Select Vehicle](select-vehicle.md) — Must be called first (no VIN in path)
- Source: [`api.py → async_get_fota_notification()`](../../custom_components/hello_smart/api.py)
