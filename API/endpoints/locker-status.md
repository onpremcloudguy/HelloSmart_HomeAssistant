# Locker Status

Front trunk / storage locker open and lock state.

[← Back to API Reference](../README.md) · [Common Patterns](../common-patterns.md)

---

## Request

```http
GET {base_url}/remote-control/getLocker/status/{vin}
```

| Parameter | Location | Required | Description |
|-----------|----------|----------|-------------|
| `vin` | Path | Yes | Vehicle VIN |

### Headers

Standard [signed headers](../common-patterns.md#required-headers) with `authorization` token.

---

## Response

```json
{
  "code": 1000,
  "data": {
    "lockerStatus": "closed",
    "lockStatus": "locked"
  }
}
```

### Response Fields

| Field | Type | Description |
|-------|------|-------------|
| `lockerStatus` | string → bool | `"open"` = locker is open, `"closed"` = locker is closed |
| `lockStatus` | string → bool | `"locked"` = locker is locked, `"unlocked"` = locker is unlocked |

---

## Data Model

Returns: [`LockerStatus`](../models.md#lockerstatus)

| Model Field | Source |
|-------------|--------|
| `open` | `lockerStatus == "open"` |
| `locked` | `lockStatus == "locked"` |

---

## Related Entities

| Entity | Platform | Device Class | Notes |
|--------|----------|-------------|-------|
| `locker_open` | binary_sensor | opening | `True` when open |
| `locker_locked` | binary_sensor | lock | Inverted — `True` (on) when **unlocked** |

---

## Known Issues

- Returns code `1405` ("not found resource") on vehicles without locker option
- Handled gracefully — entities are hidden when data is unavailable

---

## Related

- [Locker Secret](locker-secret.md) — Whether a PIN is configured
- Source: [`api.py → async_get_locker_status()`](../../custom_components/hello_smart/api.py)
