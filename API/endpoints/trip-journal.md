# Trip Journal V4

Extended trip data with energy consumption metrics for the most recent trip.

[← Back to API Reference](../README.md) · [Common Patterns](../common-patterns.md)

---

## Request

```http
GET {base_url}/geelyTCAccess/tcservices/vehicle/status/journalLogV4/{vin}
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
    "journalLogs": [
      {
        "tripId": "12345",
        "startTime": "1706028240000",
        "endTime": "1706031840000",
        "distance": "25.3",
        "duration": "3600",
        "averageSpeed": "25.3",
        "energyConsumption": "4.5",
        "averageEnergyConsumption": "17.8",
        "maxSpeed": "120.0",
        "regeneratedEnergy": "1.2",
        "startAddress": "123 Start St",
        "endAddress": "456 End Ave"
      }
    ],
    "totalTrips": 42
  }
}
```

### Response Fields

| Field | Type | Unit | Description |
|-------|------|------|-------------|
| `journalLogs` | array | — | List of trip entries (most recent first) |
| `totalTrips` | int | — | Total number of recorded trips |

### Trip Entry Fields

| Field | Type | Unit | Description |
|-------|------|------|-------------|
| `tripId` | string | — | Unique trip identifier |
| `startTime` | string → datetime | — | Trip start timestamp (epoch ms) |
| `endTime` | string → datetime | — | Trip end timestamp (epoch ms) |
| `distance` | string → float | km | Trip distance |
| `duration` | string → int | seconds | Trip duration |
| `averageSpeed` | string → float | km/h | Average speed |
| `maxSpeed` | string → float | km/h | Maximum speed reached |
| `energyConsumption` | string → float | kWh | Total energy consumed |
| `averageEnergyConsumption` | string → float | kWh/100km | Average consumption rate |
| `regeneratedEnergy` | string → float | kWh | Energy recovered via regenerative braking |
| `startAddress` | string | — | Trip origin address |
| `endAddress` | string | — | Trip destination address |

---

## Data Model

Returns: [`TripJournal`](../models.md#tripjournal) `| None`

Only the **most recent** trip from `journalLogs` is returned. Returns `None` if the list is empty.

| Model Field | Source |
|-------------|--------|
| `trip_id` | `journalLogs[0].tripId` |
| `distance` | `float(journalLogs[0].distance)` |
| `duration` | `int(journalLogs[0].duration)` |
| `energy_consumption` | `float(journalLogs[0].energyConsumption)` |
| `avg_energy_consumption` | `float(journalLogs[0].averageEnergyConsumption)` |
| `avg_speed` | `float(journalLogs[0].averageSpeed)` |
| `max_speed` | `float(journalLogs[0].maxSpeed)` |
| `start_time` | `journalLogs[0].startTime` parsed |
| `end_time` | `journalLogs[0].endTime` parsed |

---

## Related Entities

| Entity | Platform | Device Class | Unit |
|--------|----------|-------------|------|
| `last_trip_distance` | sensor | distance | km |
| `last_trip_duration` | sensor | duration | s |
| `last_trip_energy` | sensor | energy | kWh |
| `last_trip_avg_consumption` | sensor | — | kWh/100km |
| `last_trip_avg_speed` | sensor | speed | km/h |
| `last_trip_max_speed` | sensor | speed | km/h |

---

## Known Issues

- Returns code `8153` ("Connection interruption") on some INTL regions
- `startAddress` and `endAddress` are not currently exposed as entities

---

## Related

- [Total Distance](total-distance.md) — Cumulative odometer
- [Energy Ranking](energy-ranking.md) — Consumption ranking
- Source: [`api.py → async_get_trip_journal()`](../../custom_components/hello_smart/api.py)
