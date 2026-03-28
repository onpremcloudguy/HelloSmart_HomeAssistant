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
          "exteriorTemp": "18.0",
          "winPosDriver": "0",
          "winPosPassenger": "0",
          "winPosDriverRear": "0",
          "winPosPassengerRear": "0",
          "sunroofPos": "101",
          "sunroofOpenStatus": "0",
          "curtainPos": "101",
          "curtainOpenStatus": "0",
          "sunCurtainRearPos": "101",
          "sunCurtainRearOpenStatus": "0",
          "drvHeatSts": "0",
          "passHeatingSts": "0",
          "rlHeatingSts": "0",
          "rrHeatingSts": "0",
          "drvVentSts": "0",
          "passVentSts": "0",
          "rlVentSts": "0",
          "rrVentSts": "0",
          "steerWhlHeatingSts": "0",
          "preClimateActive": false,
          "defrost": false,
          "airBlowerActive": false
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

### Climate Detailed (also in climateStatus)

| Field | Type | Unit | Description |
|-------|------|------|-------------|
| `winPosDriver` | string → int | % | Driver window position (0 = closed, 100 = fully open) |
| `winPosPassenger` | string → int | % | Passenger window position |
| `winPosDriverRear` | string → int | % | Rear-left window position |
| `winPosPassengerRear` | string → int | % | Rear-right window position |
| `sunroofPos` | string → int | % | Sunroof position (**`101` = not equipped**) |
| `sunroofOpenStatus` | string → bool | — | `"1"` = sunroof open |
| `curtainPos` | string → int | % | Sun curtain position (**`101` = not equipped**) |
| `curtainOpenStatus` | string → bool | — | `"1"` = curtain open |
| `sunCurtainRearPos` | string → int | % | Rear sun curtain position (**`101` = not equipped**) |
| `sunCurtainRearOpenStatus` | string → bool | — | `"1"` = rear curtain open |
| `drvHeatSts` | string → int | level | Driver seat heating (0=off, 1=low, 2=medium, 3=high) |
| `passHeatingSts` | string → int | level | Passenger seat heating |
| `rlHeatingSts` | string → int | level | Rear-left seat heating |
| `rrHeatingSts` | string → int | level | Rear-right seat heating |
| `drvVentSts` | string → int | level | Driver seat ventilation (0=off, 1=low, 2=medium, 3=high) |
| `passVentSts` | string → int | level | Passenger seat ventilation |
| `rlVentSts` | string → int | level | Rear-left seat ventilation |
| `rrVentSts` | string → int | level | Rear-right seat ventilation |
| `steerWhlHeatingSts` | string → int | level | Steering wheel heating |
| `preClimateActive` | bool | — | Pre-conditioning active |
| `defrost` | bool | — | Defrost active |
| `airBlowerActive` | bool | — | Air blower active |

### Sentinel Value: `101` (Not Equipped)

Position fields (`sunroofPos`, `curtainPos`, `sunCurtainRearPos`, and window position fields) use **`101`** as a sentinel value meaning **"hardware not equipped"** on this vehicle.

When a position field equals `101`:
- The position is normalised to `None` (unavailable)
- The corresponding open/closed boolean (e.g., `sunroofOpenStatus`) is also set to `None`
- The integration will **not create entities** for that hardware at all

This applies to vehicles without sunroofs, sun curtains, or (less commonly) powered rear windows. The sentinel is consistent across all Smart models (#1, #3, #5) and all trim levels.

Example — a Smart #3 BRABUS **without** a sunroof:
```json
{
  "sunroofPos": "101",
  "sunroofOpenStatus": "0",
  "curtainPos": "101",
  "curtainOpenStatus": "0",
  "sunCurtainRearPos": "101",
  "sunCurtainRearOpenStatus": "0"
}
```

> **Integration behaviour**: On first data fetch, entities with `equipped_fn` callbacks check whether the underlying field is `None`. If it is, the entity is never registered. Any previously-registered stale entities are cleaned up from the entity registry.

### Maintenance Status

| Field | Type | Unit | Description |
|-------|------|------|-------------|
| `odometer` | string → float | km | Total distance driven |
| `daysToService` | string → int | days | Days until next service |
| `distanceToService` | string → float | km | Distance until next service |
| `brakeFluidLevelStatus` | string → bool | — | Fluid status: `0`=normal, `1`=low, `2`=too low, `3`=high (OK), `7`=unknown |
| `washerFluidLevelStatus` | string → bool | — | Fluid status: `0`=normal, `1`=low, `2`=too low, `3`=high (OK), `7`=unknown |

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
| `2` | `ac_charging` |
| `15` | `dc_charging` |
| `24` | `super_charging` |
| `25` | `plugged_not_charging` |
| `28` | `boost_charging` |
| `30` | `wireless_charging` |

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
| `power_mode` | sensor | enum |
| `window_position_*` | sensor | — |
| `sunroof_position` | sensor | — |
| `curtain_position` | sensor | — |
| `sun_curtain_rear_position` | sensor | — |
| `driver_seat_heating` / `passenger_seat_heating` | sensor | — |
| `rear_left_seat_heating` / `rear_right_seat_heating` | sensor | — |
| `driver_seat_ventilation` / `passenger_seat_ventilation` | sensor | — |
| `steering_wheel_heating` | sensor | — |
| `driver_door` / `passenger_door` / etc. | binary_sensor | door |
| `driver_window` / etc. | binary_sensor | window |
| `sunroof_open` | binary_sensor | opening |
| `curtain_open` / `sun_curtain_rear_open` | binary_sensor | opening |
| `charger_connected` | binary_sensor | plug |
| `tyre_warning_*` | binary_sensor | problem |
| `brake_fluid_ok` | binary_sensor | problem |
| `washer_fluid_low` | binary_sensor | problem |
| `location` | device_tracker | — |

---

## Related

- [SOC / Charging Detail](soc.md) — Supplementary charging data
- [Vehicle Running State](vehicle-state.md) — Power mode, speed
- Source: [`api.py → async_get_vehicle_status()`](../../custom_components/hello_smart/api.py)
