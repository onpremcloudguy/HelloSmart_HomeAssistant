# Locker Secret

Whether a locker PIN has been configured. Does **not** expose the actual PIN value.

[← Back to API Reference](../README.md) · [Common Patterns](../common-patterns.md)

---

## Request

```http
GET {base_url}/remote-control/locker/secret/{vin}
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
    "hasSecret": true,
    "secretSet": true
  }
}
```

### Response Fields

| Field | Type | Description |
|-------|------|-------------|
| `hasSecret` | bool | Whether the locker secret feature is available |
| `secretSet` | bool | Whether a PIN has been configured |

---

## Data Model

Returns: [`LockerSecret`](../models.md#lockersecret)

| Model Field | Source |
|-------------|--------|
| `has_secret` | `hasSecret` |
| `secret_set` | `secretSet` |

---

## Related Entities

| Entity | Platform | Device Class |
|--------|----------|-------------|
| `locker_secret_set` | binary_sensor | — |

---

## Related

- [Locker Status](locker-status.md) — Open/locked state
- Source: [`api.py → async_get_locker_secret()`](../../custom_components/hello_smart/api.py)
