# Full Vehicle Status

Primary endpoint — returns battery, charging, doors, windows, tyres, maintenance, climate, GPS, and more.

[← Back to API Reference](../README.md) · [Common Patterns](../common-patterns.md)

---

## Request

```http
GET {base_url}/remote-control/vehicle/status/{vin}?latest={true|False}&target=basic,more&userId={userId}
```

| Parameter | Location | Required | Description |
|-----------|----------|----------|-------------|
| `vin` | Path | Yes | Vehicle VIN |
| `latest` | Query | Yes | Request freshest data (`true` EU, `False` INTL) |
| `target` | Query | Yes | Data sections to include (`basic,more`) |
| `userId` | Query | Yes | Authenticated user ID |

### Headers

Standard [signed headers](../common-patterns.md#required-headers) with `authorization` token.

> **Note:** EU uses `latest=true` (Python `True.__str__()`), INTL uses `latest=False`.

---

## Response

```json
{
  "code": 1000,
  "data": {
    "vehicleStatus": {
      "updateTime": "1706028240000",
      "additionalVehicleStatus": {
        "electricVehicleStatus": {
          "chargeLevel": "85",
          "distanceToEmptyOnBatteryOnly": "245.0",
          "chargerState": "0",
          "statusOfChargerConnection": "0"
        },
        "doorsStatus": {
          "driver": "0",
          "passenger": "0",
          "rear_left": "0",
          "rear_right": "0",
          "trunk": "0"
        },
        "windowStatus": {
          "driver": "0",
          "passenger": "0",
          "rear_left": "0",
          "rear_right": "0"
        },
        "climateStatus": {
          "climateActive": false,
          "fragActive": "0",
          "interiorTemp": "22.5",
          "exteriorTemp": "18.0"
        },
        "maintenanceStatus": {
          "odometer": "500.000",
          "daysToService": "321",
          "distanceToService": "12345",
          "brakeFluidLevelStatus": "3",
          "washerFluidLevelStatus": "1",
          "tyreStatusDriver": "241.648",
          "tyreStatusDriverRear": "240.275",
          "tyreStatusPassenger": "244.394",
          "tyreStatusPassengerRear": "237.529",
          "tyreTempDriver": "11.000",
          "tyreTempDriverRear": "10.500",
          "tyreTempPassenger": "11.200",
          "tyreTempPassengerRear": "10.800",
          "tyrePreWarningDriver": "0",
          "tyrePreWarningDriverRear": "0",
          "tyrePreWarningPassenger": "0",
          "tyrePreWarningPassengerRear": "0",
          "mainBatteryStatus": {
            "stateOfCharge": "1",
            "chargeLevel": "94.2",
            "voltage": "12.400"
          }
        },
        "runningStatus": {
          "gpsInformation": {
            "latitude": "-33.8688",
            "longitude": "151.2093",
            "altitude": "105"
          }
        },
        "basicVehicleStatus": {
          "powerMode": "0"
        }
      }
    }
  }
}
```

---

## Response Fields

### Electric Vehicle Status

| Field | Type | Unit | Description |
|-------|------|------|-------------|
| `chargeLevel` | string → int | % | Battery state of charge |
| `distanceToEmptyOnBatteryOnly` | string → float | km | Estimated range remaining |
| `chargerState` | string → enum | — | Charging state code (see mapping below) |
| `statusOfChargerConnection` | string → bool | — | `"1"` = charger connected |

### Doors Status

| Field | Type | Description |
|-------|------|-------------|
| `driver` | string → bool | `"0"` = closed, `"1"` = open |
| `passenger` | string → bool | `"0"` = closed, `"1"` = open |
| `rear_left` | string → bool | `"0"` = closed, `"1"` = open |
| `rear_right` | string → bool | `"0"` = closed, `"1"` = open |
| `trunk` | string → bool | `"0"` = closed, `"1"` = open |

### Window Status

| Field | Type | Description |
|-------|------|-------------|
| `driver` | string → bool | `"0"` = closed, `"1"` = open |
| `passenger` | string → bool | `"0"` = closed, `"1"` = open |
| `rear_left` | string → bool | `"0"` = closed, `"1"` = open |
| `rear_right` | string → bool | `"0"` = closed, `"1"` = open |

### Climate Status

| Field | Type | Unit | Description |
|-------|------|------|-------------|
| `climateActive` | bool | — | Whether HVAC is running |
| `fragActive` | string → bool | — | `"1"` = fragrance diffuser on |
| `interiorTemp` | string → float | °C | Cabin temperature |
| `exteriorTemp` | string → float | °C | Outside temperature |

### Maintenance Status

| Field | Type | Unit | Description |
|-------|------|------|-------------|
| `odometer` | string → float | km | Total distance driven |
| `daysToService` | string → int | days | Days until next service |
| `distanceToService` | string → float | km | Distance until next service |
| `brakeFluidLevelStatus` | string → bool | — | `"3"` = OK |
| `washerFluidLevelStatus` | string → int | — | Washer fluid level indicator |

### Tyre Data

| Field | Type | Unit | Description |
|-------|------|------|-------------|
| `tyreStatusDriver` | string → float | kPa | Front-left tyre pressure |
| `tyreStatusPassenger` | string → float | kPa | Front-right tyre pressure |
| `tyreStatusDriverRear` | string → float | kPa | Rear-left tyre pressure |
| `tyreStatusPassengerRear` | string → float | kPa | Rear-right tyre pressure |
| `tyreTempDriver` | string → float | °C | Front-left tyre temperature |
| `tyreTempPassenger` | string → float | °C | Front-right tyre temperature |
| `tyreTempDriverRear` | string → float | °C | Rear-left tyre temperature |
| `tyreTempPassengerRear` | string → float | °C | Rear-right tyre temperature |
| `tyrePreWarningDriver` | string → bool | — | `"1"` = pressure warning |
| `tyrePreWarningPassenger` | string → bool | — | `"1"` = pressure warning |
| `tyrePreWarningDriverRear` | string → bool | — | `"1"` = pressure warning |
| `tyrePreWarningPassengerRear` | string → bool | — | `"1"` = pressure warning |

### 12V Battery (mainBatteryStatus)

| Field | Type | Unit | Description |
|-------|------|------|-------------|
| `stateOfCharge` | string → int | — | Battery health indicator |
| `chargeLevel` | string → float | % | 12V battery charge level |
| `voltage` | string → float | V | 12V battery voltage |

### GPS (runningStatus.gpsInformation)

| Field | Type | Unit | Description |
|-------|------|------|-------------|
| `latitude` | string → float | degrees | Vehicle latitude |
| `longitude` | string → float | degrees | Vehicle longitude |
| `altitude` | string → float | m | Altitude above sea level |

### Power Mode (basicVehicleStatus)

| Field | Type | Description |
|-------|------|-------------|
| `powerMode` | string → enum | `"0"` off, `"1"` accessory, `"2"` on, `"3"` cranking |

---

## Charging State Mapping

| `chargerState` Value | ChargingState Enum |
|---------------------|-------------------|
| `0` | `not_charging` |
| `1–3` | `charge_preparation` |
| `4–6` | `ac_charging` |
| `7–9` | `dc_charging` |
| `10–14` | `charge_paused` |
| `15` | `fully_charged` |

---

## Data Model

Returns: [`VehicleStatus`](../models.md#vehiclestatus)

---

## Related Entities

| Entity | Platform | Device Class |
|--------|----------|-------------|
| `battery_level` | sensor | battery |
| `range_remaining` | sensor | distance |
| `charging_status` | sensor | enum |
| `odometer` | sensor | distance |
| `interior_temp` / `exterior_temp` | sensor | temperature |
| `tyre_pressure_*` | sensor | pressure |
| `tyre_temp_*` | sensor | temperature |
| `battery_12v_voltage` | sensor | voltage |
| `battery_12v_level` | sensor | battery |
| `days_to_service` | sensor | duration |
| `distance_to_service` | sensor | distance |
| `washer_fluid_level` | sensor | — |
| `power_mode` | sensor | enum |
| `driver_door` / `passenger_door` / etc. | binary_sensor | door |
| `driver_window` / etc. | binary_sensor | window |
| `charger_connected` | binary_sensor | plug |
| `tyre_warning_*` | binary_sensor | problem |
| `brake_fluid_ok` | binary_sensor | problem |
| `location` | device_tracker | — |

---

## Related

- [SOC / Charging Detail](soc.md) — Supplementary charging data
- [Vehicle Running State](vehicle-state.md) — Power mode, speed
- Source: [`api.py → async_get_vehicle_status()`](../../custom_components/hello_smart/api.py)
