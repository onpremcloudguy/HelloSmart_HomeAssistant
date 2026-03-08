# Feature Specification: APK GET Endpoint Extraction & Integration

**Feature Branch**: `002-apk-get-endpoints`  
**Created**: 2026-03-08  
**Status**: Draft  
**Input**: User description: "Reverse-engineer all GET API endpoints from both APK files (hello_smart_europe.apk and hello_smart_intl.xapk) and extend the Hello Smart HA integration to consume them. Silent per-region failure, dynamic entity visibility, 60-second auto-refresh, and proper vehicle device identity."

## APK Analysis Summary

Both APK files (EU `.apk` and INTL `.xapk`) share the same underlying codebase. String extraction from the compiled DEX files reveals an identical set of API path patterns. The following GET endpoints were discovered that are **not yet implemented** in the current integration:

### Tier 1 — Vehicle Data Endpoints (via `{base_url}` — HMAC signed)

| # | Path | Purpose |
|---|------|---------|
| 1 | `/remote-control/vehicle/status/location` | Standalone vehicle GPS location |
| 2 | `/remote-control/vehicle/status/state/{vin}` | Condensed vehicle running state |
| 3 | `/remote-control/vehicle/status/journalLog/{vin}` | Trip journal / drive log |
| 4 | `/remote-control/vehicle/status/history/diagnostic/{vin}` | Diagnostic trouble history |
| 5 | `/remote-control/vehicle/telematics/{vin}` | Telematics / connectivity status |
| 6 | `/remote-control/charging/reservation/{vin}` | Charging schedule / reservation |
| 7 | `/remote-control/schedule/{vin}` | Climate pre-conditioning schedule |
| 8 | `/remote-control/getFridge/status/{vin}` | Mini-fridge status (Smart #1) |
| 9 | `/remote-control/getLocker/status/{vin}` | Frunk / storage locker status |
| 10 | `/remote-control/getVtmSettingStatus` | Vehicle theft monitoring settings |
| 11 | `/remote-control/vehicle/fragrance/{vin}` | Cabin fragrance system status |
| 12 | `/remote-control/locker/secret/{vin}` | Locker PIN/secret status |

### Tier 2 — Telematics Cloud Endpoints (via `{base_url}` — HMAC signed)

| # | Path | Purpose |
|---|------|---------|
| 13 | `/geelyTCAccess/tcservices/capability/{vin}` | Vehicle feature capabilities |
| 14 | `/geelyTCAccess/tcservices/vehicle/geofence/all/{vin}` | All configured geofences |
| 15 | `/geelyTCAccess/tcservices/vehicle/status/qrvs/{vin}` | Quick Remote Vehicle Status |
| 16 | `/geelyTCAccess/tcservices/vehicle/status/historyV2/{vin}` | Status history V2 |
| 17 | `/geelyTCAccess/tcservices/vehicle/status/powerMode/{vin}` | Power mode (on/off/accessory) |
| 18 | `/geelyTCAccess/tcservices/vehicle/status/journalLogV4/{vin}` | Trip journal V4 (extended) |
| 19 | `/geelyTCAccess/tcservices/vehicle/telematics/{vin}` | TC telematics status |
| 20 | `/geelyTCAccess/tcservices/customer/vehicle/plantNo/{vin}` | Factory plant number |
| 21 | `/geelyTCAccess/tcservices/vehicle/status/getTotalDistanceByLabel/{vin}` | Total distance / odometer |
| 22 | `/geelyTCAccess/tcservices/vehicle/status/ranking/odometer/vehicleModel/{vin}?topn=100` | Odometer ranking among model |
| 23 | `/geelyTCAccess/tcservices/vehicle/status/ranking/aveFuelConsumption/vehicleModel/{vin}?topn=100` | Fuel consumption ranking |
| 24 | `/geelyTCAccess/tcservices/vehicle/status/ranking/aveEnergyConsumption/vehicleModel/{vin}?topn=100` | Energy consumption ranking |
| 25 | `/hf-capability-center/api/v2/ability/{vin}` | Vehicle ability matrix |

### Tier 3 — Auxiliary / User Endpoints (via `{base_url}` — HMAC signed)

| # | Path | Purpose |
|---|------|---------|
| 26 | `/gid/vehicle/{userId}` | GID-linked vehicle info |
| 27 | `/member/user/{userId}` | Account member info |
| 28 | `/platform/user/info/{userId}` | Platform user profile |
| 29 | `/remote-control/user/authorization/selectStatus` | Authorization grant status |
| 30 | `/remote-control/user/authorization/selectRecord` | Authorization audit records |
| 31 | `/remote-control/user/authorization/vehicle/status/{vin}` | Per-vehicle auth status |
| 32 | `/profile/concurrently/switch/status` | Profile switching status |
| 33 | `/profile/notification` | User notifications |
| 34 | `/fota/geea/assignment/notification` | Firmware update notifications |

### Tier 4 — Weather (via `{base_url}` — HMAC signed)

| # | Path | Purpose |
|---|------|---------|
| 35 | `/security2/v2/weather/index` | Weather index at vehicle location |
| 36 | `/security2/v2/weather/observe` | Current weather observation |

## User Scenarios & Testing *(mandatory)*

### User Story 1 — Extended Vehicle Status with Tyre Pressure, Diagnostics, and Running State (Priority: P1)

A Smart vehicle owner who has already set up the Hello Smart integration sees additional entities appear on their vehicle's device card: tyre pressure per wheel, diagnostic status, vehicle running/power state, and telematics connectivity. These data points come from the newly integrated GET endpoints (`/vehicle/status/state/{vin}`, `/vehicle/telematics/{vin}`, `/vehicle/status/history/diagnostic/{vin}`, and tyre data from the existing vehicle status response's `tyreStatus` fields). The owner can create automations based on low tyre pressure warnings or diagnostic alerts.

**Why this priority**: Core vehicle health data is the highest-value addition. Tyre pressure, diagnostics, and running state are the most universally available and useful data points across all Smart vehicle models and regions.

**Independent Test**: After integration reload, verify that new sensor entities (e.g., tyre pressure FL/FR/RL/RR, vehicle power mode, telematics connection status) appear under the vehicle device card with valid numeric/state values.

**Acceptance Scenarios**:

1. **Given** a configured Hello Smart integration with one vehicle, **When** the coordinator polls and the API returns tyre pressure data, **Then** four tyre pressure sensor entities (front-left, front-right, rear-left, rear-right) appear under the vehicle device with values in bar/PSI.
2. **Given** a configured Hello Smart integration, **When** the API returns vehicle state data, **Then** a "Power Mode" sensor shows the current state (off, accessory, on, cranking).
3. **Given** a configured Hello Smart integration, **When** the API returns telematics status, **Then** a "Telematics Connected" binary sensor reflects the vehicle's connectivity state.
4. **Given** a configured Hello Smart integration, **When** the diagnostic endpoint returns data, **Then** a "Last Diagnostic" sensor shows the most recent diagnostic result or timestamp.
5. **Given** a vehicle whose API does not return tyre data (e.g., field is null), **When** the coordinator polls, **Then** the tyre pressure entities are not registered at all — no "unavailable" or "unknown" state is shown.

---

### User Story 2 — Charging Schedule and Climate Pre-conditioning Visibility (Priority: P2)

A Smart vehicle owner can see their configured charging schedule and climate pre-conditioning schedule as sensor entities. They can view whether a charging reservation is active, the scheduled start/end times, and whether climate pre-conditioning is programmed. This helps them verify their car is set up correctly for overnight charging without opening the mobile app.

**Why this priority**: Charging schedule visibility is a high-demand feature for EV owners who use time-of-use electricity pricing. Climate scheduling is a close companion.

**Independent Test**: Configure a charging schedule in the Hello Smart mobile app, then verify the HA entities reflect the scheduled times and active/inactive state.

**Acceptance Scenarios**:

1. **Given** a vehicle with a charging reservation configured, **When** the coordinator polls `/remote-control/charging/reservation/{vin}`, **Then** entities appear showing reservation status (active/inactive), scheduled start time, and scheduled end time.
2. **Given** a vehicle with a climate schedule configured, **When** the coordinator polls `/remote-control/schedule/{vin}`, **Then** entities appear showing the climate schedule status and scheduled activation time.
3. **Given** a vehicle with no charging reservation set, **When** the endpoint returns empty/null data, **Then** no charging schedule entities are created.

---

### User Story 3 — Trip Journal and Distance Tracking (Priority: P3)

A Smart vehicle owner can see trip history data: the most recent trip's distance, duration, energy consumption, start/end address summaries, and total odometer reading. This data comes from the trip journal endpoints and the total-distance endpoint.

**Why this priority**: Trip tracking provides historical context and long-term vehicle usage insights. The odometer reading is especially valuable for maintenance planning.

**Independent Test**: After driving the vehicle, verify that the "Last Trip Distance" sensor updates with a valid km value and "Odometer" reflects the total distance.

**Acceptance Scenarios**:

1. **Given** a vehicle with trip journal data, **When** the coordinator polls the journal log endpoint, **Then** sensors for last trip distance, last trip duration, and last trip energy consumption appear with valid values.
2. **Given** a vehicle with total distance data, **When** the coordinator polls `/geelyTCAccess/tcservices/vehicle/status/getTotalDistanceByLabel/{vin}`, **Then** an "Odometer" sensor shows the total distance in km.
3. **Given** a vehicle where the trip journal endpoint returns no data (unsupported region), **When** the coordinator polls, **Then** no trip-related entities are created and no error is logged above debug level.

---

### User Story 4 — Vehicle Feature Accessories: Fridge, Fragrance, and Locker (Priority: P4)

A Smart vehicle owner with optional accessories (mini-fridge in Smart #1, cabin fragrance system, front trunk locker) sees status entities for each accessory that their vehicle supports. Vehicles without these features simply don't show the corresponding entities.

**Why this priority**: Accessory status is niche but demonstrates the dynamic entity visibility system. Only shown if the vehicle actually has the hardware.

**Independent Test**: For a Smart #1 with the mini-fridge option, verify a "Fridge" binary sensor appears showing on/off. For a vehicle without a fridge, verify no fridge entity exists.

**Acceptance Scenarios**:

1. **Given** a vehicle with a mini-fridge, **When** the coordinator polls `/remote-control/getFridge/status/{vin}`, **Then** a "Mini Fridge" binary sensor shows on/off state.
2. **Given** a vehicle with the fragrance system, **When** the coordinator polls `/remote-control/vehicle/fragrance/{vin}`, **Then** a "Fragrance" sensor shows the current fragrance level or mode.
3. **Given** a vehicle without a mini-fridge, **When** the fridge endpoint returns an error or null data, **Then** no fridge entity is created and no error is raised.

---

### User Story 5 — Vehicle Theft Monitoring and Geofence Status (Priority: P5)

A Smart vehicle owner can see whether vehicle theft monitoring (VTM) is enabled and view their configured geofences. This provides peace-of-mind visibility directly in HA without needing to open the Smart app.

**Why this priority**: Security monitoring is important but less frequently consulted than core vehicle state.

**Independent Test**: Enable VTM in the Smart app, then verify a "Theft Monitoring" binary sensor appears as "on" in HA.

**Acceptance Scenarios**:

1. **Given** a vehicle with VTM enabled, **When** the coordinator polls `/remote-control/getVtmSettingStatus`, **Then** a "Vehicle Theft Monitoring" binary sensor shows on.
2. **Given** a vehicle with geofences configured, **When** the coordinator polls `/geelyTCAccess/tcservices/vehicle/geofence/all/{vin}`, **Then** a "Geofence Count" sensor shows the number of active geofences.
3. **Given** a vehicle where VTM is not supported (endpoint returns error), **When** the coordinator polls, **Then** no VTM entity is created.

---

### User Story 6 — 60-Second Auto-Refresh (Priority: P6)

All entities (existing and new) update every 60 seconds by default instead of the previous 5-minute interval. The owner sees near-real-time vehicle state on their HA dashboard.

**Why this priority**: Faster refresh makes the integration feel responsive and enables time-sensitive automations (e.g., "notify me when my car finishes charging").

**Independent Test**: After setup, observe entity `last_updated` timestamps and verify they advance every ~60 seconds.

**Acceptance Scenarios**:

1. **Given** a freshly installed integration with default settings, **When** checking the coordinator's update interval, **Then** it is 60 seconds.
2. **Given** a user who changes the scan interval in options to 120 seconds, **When** the coordinator runs, **Then** the polling interval is 120 seconds.
3. **Given** existing users who upgrade, **When** they have not explicitly configured a scan interval, **Then** the new default of 60 seconds takes effect.

---

### User Story 7 — Proper Vehicle Device Identity (Priority: P7)

Each vehicle's device card in HA shows rich device information: manufacturer "Smart", model name from the API, model year as hardware version, current firmware as software version, the VIN as serial number, and a suggested area of "Garage". All entities are displayed as sub-entities of the car (e.g., "Smart #1 Battery Level") rather than standalone entities.

**Why this priority**: Device identity is cosmetic but significantly improves the user experience by making the device card look professional and organized.

**Independent Test**: After setup, navigate to the vehicle's device page in HA and verify the device info panel shows manufacturer, model, HW version, SW version, and serial number. Verify all entities are listed under this device.

**Acceptance Scenarios**:

1. **Given** a configured vehicle, **When** viewing its device card in HA, **Then** the card shows manufacturer="Smart", model from API, model_id=series code, hw_version=model year, sw_version=current firmware, serial_number=VIN.
2. **Given** a configured vehicle, **When** viewing its device card, **Then** all sensor, binary sensor, and device tracker entities are grouped under this device.
3. **Given** a configured vehicle, **When** viewing entity names, **Then** they appear as "{Car Name} Battery Level", "{Car Name} Driver Door", etc.
4. **Given** a vehicle where OTA firmware data is not available, **When** viewing the device card, **Then** sw_version is omitted (not shown as "unknown").

---

### Edge Cases

- What happens when a GET endpoint returns HTTP 403 (e.g., endpoint not enabled for the user's plan/region)? → The coordinator logs a debug message and skips that data source; no entity is created for that data point.
- What happens when the API returns valid JSON but with all-null fields? → No entity is created for null fields; entities only appear when data has a valid, non-null value.
- What happens when an endpoint exists in the EU APK but the INTL API returns 404? → The coordinator silently skips; INTL users simply don't see those entities.
- What happens when a previously available endpoint starts returning errors? → Existing entities remain with their last known value until the next successful poll, following HA's standard coordinator behavior. No error cascades to other entities.
- What happens when the vehicle has tyre data for only 2 of 4 wheels? → Only the wheels with valid data get entities; the others are not created.
- What happens when the user has multiple vehicles and one vehicle's API calls all fail? → That vehicle's entities are unavailable, but other vehicles continue to update normally.

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: System MUST extract and consume all new GET endpoints discovered in both APK files (`hello_smart_europe.apk` and `hello_smart_intl.xapk`) that return vehicle or user data.
- **FR-002**: System MUST NOT implement any POST, PUT, or DELETE endpoints — only GET (read-only) endpoints.
- **FR-003**: System MUST handle per-endpoint failure silently — if any single GET endpoint returns an error (HTTP 4xx/5xx, unexpected response, timeout, or API error code), the integration MUST log a debug-level message and continue fetching all other endpoints for that vehicle. No single endpoint failure may cascade to other endpoints or mark the entire vehicle unavailable.
- **FR-004**: System MUST only create HA entities for data points that returned valid, non-null data from the API. If an endpoint or field returns no data (None, empty, error, or not available for the user's region), the corresponding entity MUST NOT be registered in HA. EU users and INTL users may see different sets of entities.
- **FR-005**: System MUST set the default polling interval to 60 seconds (`DEFAULT_SCAN_INTERVAL = 60`). The minimum allowed interval MUST remain at 60 seconds.
- **FR-006**: System MUST register each vehicle in the HA device registry with: `manufacturer`="Smart", `model`=API model name, `model_id`=series code, `hw_version`=model year, `sw_version`=current firmware (updated each poll), `serial_number`=VIN, `suggested_area`="Garage".
- **FR-007**: All entities MUST set `_attr_has_entity_name = True` and use `translation_key` for display names, so they render as sub-entities of the vehicle device (e.g., "{Car Name} Tyre Pressure FL").
- **FR-008**: All new API calls MUST validate URLs against the existing `URL_ALLOWLIST` and enforce HTTPS. Any new API hosts MUST be added to the allowlist.
- **FR-009**: All new API calls requiring authentication MUST use the existing HMAC-SHA1 signed request mechanism (`_signed_request`) with region-aware headers.
- **FR-010**: System MUST handle region differences (EU vs INTL) in endpoint parameters using conditional logic, following the existing pattern (e.g., `latest=true` for EU, `latest=False` for INTL).
- **FR-011**: Any new fields containing sensitive data (tokens, user IDs, PINs, secrets) MUST be added to `SENSITIVE_FIELDS` in `const.py` for log/diagnostics redaction.
- **FR-012**: New data model dataclasses MUST follow the existing pattern in `models.py` (frozen dataclasses with default values).
- **FR-013**: New sensor entities MUST use `SmartSensorEntityDescription` with `value_fn`, and new binary sensor entities MUST use `SmartBinarySensorEntityDescription` with `is_on_fn`, matching the existing patterns.
- **FR-014**: System MUST expose tyre pressure data as four independent sensor entities (front-left, front-right, rear-left, rear-right) with appropriate unit of measurement (bar or PSI).
- **FR-015**: System MUST expose the vehicle's total distance / odometer reading as a sensor entity with `device_class=DISTANCE`.
- **FR-016**: System MUST expose charging schedule/reservation status and scheduled times as sensor entities when available.
- **FR-017**: System MUST expose climate pre-conditioning schedule status when available.
- **FR-018**: System MUST expose vehicle power mode (off, accessory, on, cranking) as a sensor entity when available.
- **FR-019**: System MUST expose accessory statuses (mini-fridge, fragrance, locker) as entities only when the vehicle supports the accessory and the endpoint returns valid data.
- **FR-020**: System MUST expose vehicle theft monitoring (VTM) status as a binary sensor when the endpoint returns valid data.
- **FR-021**: System MUST expose geofence count as a sensor when the vehicle has geofences configured.
- **FR-022**: System MUST expose telematics connection status as a binary sensor when available.
- **FR-023**: System MUST expose trip journal data (last trip distance, duration, energy consumption) as sensors when the endpoint returns valid data.
- **FR-024**: System MUST document all new endpoints in the API contract specification including URL template, query parameters, headers, and response schema.
- **FR-025**: System MUST update `strings.json` with translation keys for all new entity names.

### Key Entities

- **TyrePressure**: Per-wheel tyre pressure readings (FL, FR, RL, RR) with pressure values and warning flags. Related to VehicleStatus.
- **VehicleState**: Condensed running state including power mode (off/accessory/on/cranking), ignition status. One per vehicle.
- **TripJournal**: Most recent trip data — distance, duration, energy consumption, start/end timestamps. One per vehicle.
- **ChargingReservation**: Charging schedule — active/inactive flag, scheduled start time, scheduled end time. One per vehicle.
- **ClimateSchedule**: Climate pre-conditioning schedule — enabled flag, scheduled activation time. One per vehicle.
- **TelematicsStatus**: Connectivity state of the vehicle's telematics unit. One per vehicle.
- **DiagnosticHistory**: Most recent diagnostic result or alert. One per vehicle.
- **FridgeStatus**: Mini-fridge on/off state (Smart #1 specific). One per vehicle if equipped.
- **FragranceStatus**: Cabin fragrance mode and level. One per vehicle if equipped.
- **LockerStatus**: Front trunk / locker open/closed state. One per vehicle if equipped.
- **VtmStatus**: Vehicle theft monitoring enabled/disabled. One per vehicle.
- **GeofenceInfo**: Number of configured geofences. One per vehicle.
- **Odometer**: Total distance driven. One per vehicle.
- **VehicleCapability**: Feature capability flags indicating which accessories/features the vehicle supports. Used internally to determine which entities to create.

### Assumptions

- Both APK files (EU and INTL) share the same underlying API path structure since they use the same Geely/ecarx backend. Region differences are in authentication, parameter values, and which endpoints are actually enabled server-side — not in path structure.
- The `geelyTCAccess/tcservices/*` endpoints use the same base URL (`api.ecloudeu.com`) and the same HMAC signing scheme as the existing `remote-control/*` endpoints.
- Tyre pressure values from the API are in bar. The integration will expose them in bar with HA handling unit conversion.
- Trip journal data represents the most recent completed trip, not a full trip history.
- The "ranking" endpoints (odometer ranking, energy consumption ranking) are informational and low-priority; they will be implemented but hidden behind the dynamic entity visibility — if the API returns no ranking data, no ranking entities appear.
- Endpoints that require specific hardware (fridge, fragrance, locker) will commonly return errors on vehicles without those features, and those errors will be silently absorbed.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: All GET endpoints discovered in both APK files are consumed by the integration, with each endpoint's data exposed as one or more HA entities when data is available.
- **SC-002**: EU users and INTL users see only the entities that their region's API supports — no "unavailable" or "unknown" entities for unsupported data points.
- **SC-003**: Failure of any single endpoint does not affect any other endpoint or entity. A vehicle with 3 out of 12 endpoints failing still shows 9 sets of valid entities.
- **SC-004**: All entities auto-refresh every 60 seconds by default.
- **SC-005**: Each vehicle's device card in HA displays complete device metadata: manufacturer, model, model year, firmware version, VIN, and suggested area.
- **SC-006**: All entities appear as sub-entities of the vehicle device card (e.g., "{Car Name} Tyre Pressure FL"), not as standalone entities.
- **SC-007**: The integration adds zero additional Python package dependencies — all new code uses `aiohttp` and Python stdlib only.
- **SC-008**: All new sensitive fields are redacted in diagnostics downloads and debug logs.
