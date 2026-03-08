# Diagnostic History

Most recent diagnostic trouble code (DTC) for the vehicle.

[← Back to API Reference](../README.md) · [Common Patterns](../common-patterns.md)

---

## Request

```http
GET {base_url}/remote-control/vehicle/status/history/diagnostic/{vin}
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
    "diagnosticList": [
      {
        "dtcCode": "P0001",
        "severity": "1",
        "timestamp": "1706028240000",
        "status": "active"
      }
    ]
  }
}
```

### Response Fields

| Field | Type | Description |
|-------|------|-------------|
| `diagnosticList` | array | List of diagnostic entries (may be empty) |

### Diagnostic Entry

| Field | Type | Description |
|-------|------|-------------|
| `dtcCode` | string | OBD-II diagnostic trouble code (e.g., `"P0001"`) |
| `severity` | string | Severity level |
| `timestamp` | string → datetime | When the diagnostic was recorded (epoch ms) |
| `status` | string | `"active"` or `"resolved"` |

---

## Data Model

Returns: [`DiagnosticEntry`](../models.md#diagnosticentry) `| None`

Only the most recent entry from `diagnosticList` is returned. Returns `None` if the list is empty.

| Model Field | Source |
|-------------|--------|
| `dtc_code` | `diagnosticList[0].dtcCode` |
| `severity` | `diagnosticList[0].severity` |
| `timestamp` | `diagnosticList[0].timestamp` parsed |
| `status` | `diagnosticList[0].status` |

---

## Related Entities

| Entity | Platform | Device Class |
|--------|----------|-------------|
| `diagnostic_status` | sensor | — |
| `diagnostic_code` | sensor | — |
| `diagnostic_active` | binary_sensor | problem |

---

## Known Issues

- Returns code `8153` ("Connection interruption") on some INTL regions
- Handled gracefully — entities show as unavailable when no data

---

## Related

- Source: [`api.py → async_get_diagnostic_history()`](../../custom_components/hello_smart/api.py)
