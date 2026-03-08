# Capabilities

Feature flags indicating which services are enabled for the vehicle.

[← Back to API Reference](../README.md) · [Common Patterns](../common-patterns.md)

---

## Request

```http
GET {base_url}/geelyTCAccess/tcservices/capability/{vin}
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
    "capabilities": [
      {
        "serviceId": "RCE_2",
        "enabled": true,
        "version": "1.0"
      },
      {
        "serviceId": "FOTA",
        "enabled": true,
        "version": "2.0"
      }
    ]
  }
}
```

### Response Fields

| Field | Type | Description |
|-------|------|-------------|
| `capabilities` | array | List of capability entries |

### Capability Entry

| Field | Type | Description |
|-------|------|-------------|
| `serviceId` | string | Service identifier (e.g., `"RCE_2"`, `"FOTA"`) |
| `enabled` | bool | Whether the service is active |
| `version` | string | Service API version |

---

## Data Model

Returns: [`VehicleCapabilities`](../models.md#vehiclecapabilities)

| Model Field | Source |
|-------------|--------|
| `service_ids` | List of `serviceId` values where `enabled == true` |

---

## Related Entities

| Entity | Platform | Device Class |
|--------|----------|-------------|
| `capability_count` | sensor | — |

---

## Notes

- The capability list can be used to determine which other endpoints are available for the vehicle
- The integration currently only exposes the count, not individual capabilities

---

## Related

- Source: [`api.py → async_get_capabilities()`](../../custom_components/hello_smart/api.py)
