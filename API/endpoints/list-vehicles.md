# List Vehicles

Fetch all vehicles linked to the authenticated account.

[← Back to API Reference](../README.md) · [Common Patterns](../common-patterns.md)

---

## Request

```http
GET {base_url}/device-platform/user/vehicle/secure?needSharedCar=1&userId={userId}
```

| Parameter | Location | Required | Description |
|-----------|----------|----------|-------------|
| `needSharedCar` | Query | Yes | Include shared vehicles (`1` = yes) |
| `userId` | Query | Yes | Authenticated user ID from login |

### Headers

Standard [signed headers](../common-patterns.md#required-headers) with `authorization` token.

---

## Response

```json
{
  "code": 1000,
  "data": {
    "list": [
      {
        "vin": "HESCA2C42RS234118",
        "modelName": "CM590_HC11_Performance_4WD_RHD_APAC",
        "modelYear": "2025",
        "seriesCodeVs": "HC11_IL",
        "colorName": "B07 MOYU BLACK",
        "colorCode": "026",
        "modelCode": "HC1H2D3B6213-01_IL",
        "factoryCode": "6105",
        "vehiclePhotoSmall": "",
        "vehiclePhotoBig": "",
        "plateNo": "fsp06d",
        "engineNo": "R9WK3A4AK",
        "matCode": "HC1H2D3B6213001257",
        "seriesName": "HC11",
        "vehicleType": 0,
        "fuelTankCapacity": "0",
        "ihuPlatform": "tsp",
        "tboxPlatform": "tsp",
        "defaultVehicle": true,
        "shareStatus": "N",
        "iccid": "89882390000852030884",
        "msisdn": "882399992240690",
        "temId": "V89882390000852030883088",
        "ihuId": "9997226608181950R9P00214",
        "temType": ""
      }
    ]
  }
}
```

### Response Fields

| Field | Type | Description |
|-------|------|-------------|
| `vin` | string | Vehicle Identification Number |
| `modelName` | string | Full model name (e.g., `CM590_HC11_Performance_4WD_RHD_APAC`) |
| `modelYear` | string | Model year |
| `seriesCodeVs` | string | Series code with region suffix (e.g., `HC11_IL`) |
| `colorName` | string | Paint colour name (e.g., `B07 MOYU BLACK`) |
| `colorCode` | string | Paint colour code |
| `modelCode` | string | Full model code used by VC service |
| `factoryCode` | string | Factory / production plant code |
| `vehiclePhotoSmall` | string | Small vehicle photo URL (may be empty) |
| `vehiclePhotoBig` | string | Large vehicle photo URL (may be empty) |
| `plateNo` | string | Registration plate number |
| `engineNo` | string | Motor/engine serial number |
| `matCode` | string | Material code — **encodes model and trim** (see below) |
| `seriesName` | string | Series name (e.g., `HC11`) |
| `vehicleType` | int | Vehicle type identifier |
| `fuelTankCapacity` | string | Fuel tank capacity (always `"0"` for BEV) |
| `ihuPlatform` | string | IHU (infotainment) platform type |
| `tboxPlatform` | string | T-Box (telematics) platform type |
| `defaultVehicle` | bool | Whether this is the user's primary vehicle |
| `shareStatus` | string | Share status: `"N"` = not shared, `"Y"` = shared |
| `iccid` | string | SIM ICCID |
| `msisdn` | string | SIM phone number |
| `temId` | string | Telematics unit identifier |
| `ihuId` | string | IHU hardware identifier |
| `temType` | string | Telematics type (may be empty) |

---

## Material Code (`matCode`) Decoding

The `matCode` field encodes both the **vehicle model** and **trim/edition**. This is derived from the APK sources `VehicleModel.java`, `VehicleEdition.java`, and `VehicleInfoConstants.java`.

Example: `HC1H2D3B6213001257`

### Model (positions 0–2)

| Prefix | Model | Marketing Name |
|--------|-------|----------------|
| `HX1` | Smart #1 | Compact SUV |
| `HC1` | Smart #3 | Mid-size SUV |
| `HY1` | Smart #5 | Full-size SUV |

Alternative detection via `seriesCodeVs` (strip regional suffix):

| Series Code | Model |
|-------------|-------|
| `HX11` | Smart #1 |
| `HC11` | Smart #3 |
| `HY11` | Smart #5 |

### Edition/Trim (positions 5–6)

| Code | Edition | Notes |
|------|---------|-------|
| `80` | Pure | Entry-level |
| `D1` | Pro | Mid-range |
| `GN` | Pulse | Mid-range (EU naming) |
| `D2` | Premium | Upper-range |
| `D3` | BRABUS | Performance / top-range |
| `01` | Launch Edition | Limited launch variant |

### Edition Feature Matrix

Not all editions have all hardware. The APK defines feature gates in `ClimateFragment.java` and `VehicleEdition.java`:

| Feature | Pure | Pro | Pulse | Premium | BRABUS | Launch |
|---------|------|-----|-------|---------|--------|--------|
| Driver seat heating | No | Yes | Yes | Yes | Yes | Yes |
| PM2.5 air quality sensor | No | No | Yes | Yes | Yes | Yes |
| Steering wheel heating | Market-dependent | Market-dependent | Market-dependent | Market-dependent | Market-dependent | Market-dependent |

> Steering wheel heating availability is additionally gated by market ("GD markets") per APK `hasSteeringWheelHeat()` — not purely edition-based.

The integration uses these gates to automatically exclude entities that don't apply to the vehicle's trim level.

---

## Data Model

Returns: `list[Vehicle]`

See [Vehicle model](../models.md#vehicle)

---

## Notes

- This is typically the first endpoint called after authentication
- Returns all vehicles including shared ones when `needSharedCar=1`
- The VIN from this response is used in all subsequent vehicle-specific endpoints
- The `matCode` field is essential for determining model and trim — see [Material Code Decoding](#material-code-matcode-decoding) above
- The `modelCode` field is used as a path parameter for the [Vehicle Ability](vehicle-ability.md) endpoint

---

## Related

- [Select Vehicle](select-vehicle.md) — Must be called next to set the active vehicle
- Source: [`api.py → async_get_vehicles()`](../../custom_components/hello_smart/api.py)
