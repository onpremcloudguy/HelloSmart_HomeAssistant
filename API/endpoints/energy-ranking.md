# Energy Ranking

Energy consumption ranking among vehicles of the same model.

[← Back to API Reference](../README.md) · [Common Patterns](../common-patterns.md)

---

## Request

```http
GET {base_url}/geelyTCAccess/tcservices/vehicle/status/ranking/aveEnergyConsumption/vehicleModel/{vin}?topn=100&latitude={lat}&longitude={lng}
```

| Parameter | Location | Required | Description |
|-----------|----------|----------|-------------|
| `vin` | Path | Yes | Vehicle VIN |
| `topn` | Query | Yes | Number of top rankings to include (default: `100`) |
| `latitude` | Query | Yes | Vehicle latitude (defaults to `0.0`) |
| `longitude` | Query | Yes | Vehicle longitude (defaults to `0.0`) |

### Headers

Standard [signed headers](../common-patterns.md#required-headers) with `authorization` token.

---

## Response

```json
{
  "code": 1000,
  "data": {
    "myRanking": 42,
    "myValue": "17.8",
    "totalParticipants": 100
  }
}
```

### Response Fields

| Field | Type | Unit | Description |
|-------|------|------|-------------|
| `myRanking` | int | — | Your position in the ranking |
| `myValue` | string → float | kWh/100km | Your average energy consumption |
| `totalParticipants` | int | — | Total vehicles in the ranking pool |

---

## Data Model

Returns: [`EnergyRanking`](../models.md#energyranking)

| Model Field | Source |
|-------------|--------|
| `my_ranking` | `myRanking` |
| `my_value` | `float(myValue)` |
| `total_participants` | `totalParticipants` |

---

## Related Entities

| Entity | Platform | Device Class |
|--------|----------|-------------|
| `energy_ranking` | sensor | — |

---

## Known Issues

- Returns code `1445` ("signature verification failed") on some INTL regions — likely due to query parameter encoding differences in the signature generation
- Returns code `1400` ("missing required parameter") if `latitude`/`longitude` are omitted
- The integration defaults `lat`/`lng` to `0.0` which may cause issues on some server-side validation

---

## Related

- [Trip Journal](trip-journal.md) — Per-trip energy consumption
- Source: [`api.py → async_get_energy_ranking()`](../../custom_components/hello_smart/api.py)
