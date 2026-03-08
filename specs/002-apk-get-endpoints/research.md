# Research: APK GET Endpoint Extraction & Integration

**Branch**: `002-apk-get-endpoints` | **Date**: 2026-03-08

## Sources

| Source | Confidence |
|--------|-----------|
| **pySmartHashtag** (`DasBasti/pySmartHashtag`) — Python API wrapper with test fixtures | HIGH (real API responses) |
| **SmartHashtag** (`DasBasti/SmartHashtag`) — HA integration using pySmartHashtag | HIGH (production use) |
| Local codebase (`custom_components/hello_smart/`) | HIGH (our own code) |
| APK string extraction (spec.md) | MEDIUM (paths confirmed, not schemas) |

---

## Research Topic 1: API Response Envelope

**Decision**: All Smart API endpoints share a common JSON envelope: `{"code": 1000, "data": {...}, "success": true, "message": "operation succeed"}`.

**Rationale**: Confirmed in pySmartHashtag fixtures and in our existing `_signed_request` / `_parse_vehicle_status`. `code == 1000` indicates success.

**Alternatives Considered**: None — the envelope is a platform constant.

---

## Research Topic 2: Tyre Pressure Source & Units

**Decision**: Tyre pressure data is ALREADY present in the existing `/remote-control/vehicle/status/{vin}` response under `additionalVehicleStatus.maintenanceStatus`. No separate endpoint needed. Units are **kPa** (not bar as assumed in the spec).

**Rationale**: pySmartHashtag test fixture (`vehicle_info.json`) contains:
- `tyreStatusDriver: "241.648"` (kPa, float-as-string)
- `tyreStatusDriverRear: "240.275"`
- `tyreStatusPassenger: "244.394"`
- `tyreStatusPassengerRear: "237.529"`
- `tyreTempDriver: "11.000"` (°C)
- `tyrePreWarningDriver: "0"` (boolean-as-string)

pySmartHashtag's `tires.py` parses these as kPa.

**Spec Correction**: FR-014 should read "kPa" instead of "bar". HA will handle unit conversion to user-preferred units.

**Alternatives Considered**: Using a separate tyre endpoint — rejected because the data is already in the main status response.

---

## Research Topic 3: Maintenance Data Source

**Decision**: Odometer, days-to-service, distance-to-service, brake fluid level, washer fluid level, service warning, and 12V battery status are ALSO in the existing vehicle status response under `additionalVehicleStatus.maintenanceStatus`.

**Rationale**: pySmartHashtag fixture confirms:
- `odometer: "500.000"` (km)
- `daysToService: "321"`
- `distanceToService: "12345"`
- `brakeFluidLevelStatus: "3"`
- `washerFluidLevelStatus: "1"`
- `mainBatteryStatus.stateOfCharge: "1"`, `.chargeLevel: "94.2"`, `.voltage: "12.400"`

**Implementation Note**: Extend `_parse_vehicle_status` to extract these fields from the existing response — no new API call required.

---

## Research Topic 4: Endpoint Response Schemas — Confidence Levels

### PARTIALLY CONFIRMED (have field names from reference code or fixtures)

| Endpoint | Key Fields | Source |
|----------|-----------|--------|
| `/vehicle/telematics/{vin}` | `swVersion`, `hwVersion`, `imei`, `connectivityStatus`, `powerMode`, `backupBattery` | `temStatus` block in vehicle_info.json fixture (fields null in test data) |
| `/vehicle/status/location` | `position.latitude`, `position.longitude`, `position.altitude`, `posCanBeTrusted` | `basicVehicleStatus.position` in fixture |
| `/getTotalDistanceByLabel/{vin}` | `totalDistance` (km) | `odometer` field confirmed in fixture |

### SPECULATIVE (schema inferred from APK strings + Geely platform patterns)

| Endpoint | Inferred Schema Summary |
|----------|------------------------|
| `/vehicle/status/state/{vin}` | `engineStatus`, `powerMode`, `speed`, `usageMode` (mirrors `basicVehicleStatus` fields) |
| `/vehicle/status/journalLog/{vin}` | `journalLogList` with `tripId`, `startTime`, `endTime`, `distance`, `energyConsumption` |
| `/vehicle/status/history/diagnostic/{vin}` | `diagnosticList` with DTC codes, severity, timestamps |
| `/charging/reservation/{vin}` | `reservationStatus`, `startTime`, `endTime`, `targetSoc` |
| `/schedule/{vin}` | `scheduleList` with `scheduledTime`, `temperature`, `duration` |
| `/getFridge/status/{vin}` | `fridgeStatus` ("on"/"off"), `temperature`, `mode` |
| `/getLocker/status/{vin}` | `lockerStatus`, `lockStatus` |
| `/getVtmSettingStatus` | `vtmEnabled`, `notificationEnabled`, `geofenceAlertEnabled` (no VIN in path) |
| `/vehicle/fragrance/{vin}` | `fragranceActive` (mirrors `climateStatus.fragActive`), `fragranceLevel` |
| `/locker/secret/{vin}` | `hasSecret`, `secretSet` (metadata only, not the PIN) |
| `/capability/{vin}` | `capabilities` list with `serviceId`, `enabled`, `version` |
| `/geofence/all/{vin}` | `geofences` list with `name`, `centerLatitude`, `centerLongitude`, `radius` |
| `/qrvs/{vin}` | Lightweight subset: `engineStatus`, `chargeLevel`, `doorLockStatus`, `position` |
| `/powerMode/{vin}` | `powerMode` (0=off, 1=acc, 2=on, 3=cranking) |
| `/journalLogV4/{vin}` | Extended trip with `maxSpeed`, `regeneratedEnergy`, addresses |
| `/ranking/aveEnergyConsumption/...` | `myRanking`, `myValue`, `totalParticipants` |

---

## Research Topic 5: Endpoint Deduplication Strategy

**Decision**: Where both Tier 1 (`/remote-control/...`) and Tier 2 (`/geelyTCAccess/...`) offer equivalent data, prefer the Tier 1 endpoint and only fall back to Tier 2 if Tier 1 is unavailable.

**Rationale**: Tier 1 endpoints are used by the existing integration and are confirmed working. Tier 2 (TC layer) may be a backend abstraction that wraps the same data. Calling both would double API load with no benefit.

**Deduplication Map**:
| Tier 1 | Tier 2 Equivalent | Decision |
|--------|-------------------|----------|
| `/vehicle/telematics/{vin}` | `/tcservices/vehicle/telematics/{vin}` | Use Tier 1 |
| `/vehicle/status/journalLog/{vin}` | `/tcservices/vehicle/status/journalLogV4/{vin}` | Use Tier 2 (V4 has more fields) |
| (none) | `/tcservices/vehicle/status/qrvs/{vin}` | Skip — subset of data we already get |
| (none) | `/tcservices/vehicle/status/powerMode/{vin}` | Skip — available from `/vehicle/status/state/{vin}` |
| `/vehicle/status/location` | (none) | Skip — already in main vehicle status response |

**Net Endpoints After Deduplication**: 19 new API calls (after removing 5 duplicates/subsets from the original 36).

---

## Research Topic 6: Dynamic Entity Visibility Implementation

**Decision**: Use `None` sentinel values in dataclasses. Entity platform `async_setup_entry` filters entities at registration time: if `value_fn(data)` returns `None`, the entity is not created for that vehicle. On subsequent polls, if data becomes `None`, the entity goes to `unavailable` state (standard HA coordinator behavior).

**Rationale**: This matches HA best practices. The alternative (removing entities dynamically) would require entity registry manipulation which is fragile and non-standard.

**Implementation Pattern**:
```python
# In async_setup_entry:
for vehicle_data in coordinator.data.values():
    for description in SENSOR_DESCRIPTIONS:
        if description.value_fn(vehicle_data) is not None:
            entities.append(SmartSensorEntity(coordinator, description, vehicle_data.vehicle.vin))
```

---

## Research Topic 7: Vehicle DeviceInfo Enhancement

**Decision**: Extend `DeviceInfo` with `model_id`, `hw_version`, `sw_version`, `serial_number`, and `suggested_area`. Source data from `Vehicle` dataclass (model_year, series_code, vin) and `OTAInfo` (current_version).

**Rationale**: HA device registry supports all these fields. The pySmartHashtag fixture confirms model/year data is available from the vehicle list endpoint.

**Implementation**:
```python
DeviceInfo(
    identifiers={(DOMAIN, vin)},
    manufacturer="Smart",
    model=vehicle.model_name or "Smart Vehicle",
    model_id=vehicle.series_code or None,
    name=vehicle.model_name or f"Smart {vin[-6:]}",
    hw_version=vehicle.model_year or None,
    sw_version=ota.current_version or None,
    serial_number=vin,
    suggested_area="Garage",
)
```

---

## Research Topic 8: Endpoint Rate Limiting

**Decision**: No evidence of per-endpoint rate limiting. But moving from 5-minute to 60-second polling with ~19 new endpoints means ~19× more API calls per minute. Implement sequential (not parallel) endpoint calls within a single poll cycle to avoid burst pressure.

**Rationale**: pySmartHashtag's coordinator calls endpoints sequentially. The Smart/Geely API does not document rate limits, but sequential calling is safer than parallel fan-out.

**Risk Mitigation**: If 429 errors appear at runtime, add an optional `scan_interval` config option and document minimum safe intervals. The per-endpoint try/except pattern means a 429 on one endpoint won't cascade.

---

## Research Topic 9: Fragrance System Confirmation

**Decision**: The fragrance system field `climateStatus.fragActive` is confirmed in the vehicle status fixture. The standalone `/vehicle/fragrance/{vin}` GET endpoint likely returns extended fragrance details (level, type).

**Rationale**: `fragActive: false` appears in the confirmed vehicle_info.json fixture under `climateStatus`. This confirms the hardware integration exists in the API.

---

## Research Topic 10: No-VIN Endpoints

**Decision**: Two endpoints lack `{vin}` in the path: `/getVtmSettingStatus` and `/vehicle/status/location`. These likely use the "selected vehicle" session state set by `async_select_vehicle`. Call `async_select_vehicle` before each no-VIN endpoint (we already do this in the current flow).

**Rationale**: The existing integration already calls `async_select_vehicle` before `async_get_vehicle_status`, establishing the pattern. The no-VIN endpoints likely rely on this server-side session.

---

## Summary

| Topic | Resolution |
|-------|-----------|
| Response envelope | Standard `{code, data, success, message}` |
| Tyre pressure | Already in main status response, kPa units |
| Maintenance data | Already in main status response |
| Schema confidence | 3 partially confirmed, 16 speculative |
| Deduplication | 19 net new endpoints after removing 5 duplicates |
| Entity visibility | `None` sentinel + filter at registration |
| DeviceInfo | Enhanced with model_id, hw/sw version, serial_number, suggested_area |
| Rate limiting | Sequential calls, no known limits |
| Fragrance | Confirmed via `climateStatus.fragActive` |
| No-VIN endpoints | Use selected vehicle session |
