# Research: API Command Controls

**Feature**: 003-api-command-controls  
**Date**: 2025-07-24  
**Sources**: Hello Smart INTL APK (DEX string extraction), pySmartHashtag library (DasBasti/pySmartHashtag), existing codebase

---

## R-001: Command API Transport Pattern

**Question**: What HTTP method and endpoint are used for sending vehicle commands?

**Decision**: All vehicle commands use **PUT** to `/remote-control/vehicle/telematics/{vin}`

**Rationale**: Both the pySmartHashtag library (`control/climate.py`, `control/charging.py`) and the APK reverse engineering confirm that all remote control commands are sent as PUT requests to the telematics endpoint. The endpoint path is already imported via `API_TELEMATICS_URL` in pySmartHashtag's `const.py`. The existing `hello_smart` integration already has this URL in its `api.py` for GET requests.

**Alternatives considered**:
- Individual POST endpoints per command: Not found in APK or pySmartHashtag. The API uses a single endpoint with `serviceId` multiplexing.
- PATCH for partial updates: Not used for commands. Only the shared PUT telematics endpoint is used.

**Evidence**:
- pySmartHashtag `control/climate.py` line 117: `client.put(API_BASE_URL + API_TELEMATICS_URL + self.vin, ...)`
- pySmartHashtag `control/charging.py` line 97: `client.put(self.account.vehicles[self.vin].base_url + API_TELEMATICS_URL + self.vin, ...)`
- pySmartHashtag test mock `common.py` line 78: `self.put(base_url + "/remote-control/vehicle/telematics/TestVIN0000000001")`

---

## R-002: Command Payload Structure

**Question**: What is the JSON payload structure for vehicle commands?

**Decision**: All commands share a standard payload envelope:

```json
{
  "creator": "tc",
  "command": "start" | "stop",
  "serviceId": "<SERVICE_ID>",
  "timestamp": "<epoch_milliseconds>",
  "operationScheduling": {
    "duration": <int>,
    "interval": 0,
    "occurs": 1,
    "recurrentOperation": false
  },
  "serviceParameters": [
    {"key": "<param_key>", "value": "<param_value>"},
    ...
  ]
}
```

**Rationale**: Two independent implementations confirm this structure:
1. pySmartHashtag `ClimateControll.BASE_PAYLOAD_TEMPLATE` uses `creator`, `operationScheduling`, `serviceId` fields.
2. pySmartHashtag `ChargingControl.BASE_PAYLOAD_TEMPLATE` uses the same envelope structure.
3. APK strings show `ServiceParameter` class with `key`/`value` fields, `OperationScheduling` class, and `RemoteControlRequest` with `ServiceId`.

**Key observations**:
- `creator` is always `"tc"` (telematics controller)
- `command` is `"start"` or `"stop"` for most services
- For charging, `command` is always `"start"` — the actual start/stop is controlled via `serviceParameters`
- `timestamp` uses `utils.create_correct_timestamp()` which returns epoch milliseconds as a string
- The payload is JSON-serialized with spaces stripped: `json.dumps(payload).replace(" ", "")`
- HMAC signature is computed over the stripped JSON body

**Alternatives considered**: None — both sources agree on this structure.

---

## R-003: Service ID Mapping

**Question**: What are all the available service IDs and what commands do they control?

**Decision**: The following service IDs were extracted from the APK and cross-referenced with pySmartHashtag:

### Confirmed (implemented in pySmartHashtag)

| Service ID | Command | Description |
|-----------|---------|-------------|
| `RCE_2` | Climate | Remote Climate/Environment control — AC, heating, ventilation |
| `rcs` | Charging | Remote Charging Start/Stop |

### Discovered in APK (not yet in pySmartHashtag)

| Service ID | Likely Command | Inferred From |
|-----------|---------------|---------------|
| `RDL` / `RDL_2` | Door Lock | "Remote Door Lock" naming, `iovLock` APK method |
| `RDU` / `RDU_2` | Door Unlock | "Remote Door Unlock" naming, `iovUnlock` APK method |
| `RHL` | Horn & Light | "Remote Horn & Light", `iovHorn` + `iovFlash` APK methods, `lambda$horn$7` and `lambda$flash$6` in `GSVControlsActivity` |
| `RTL` | Trunk Lock | "Remote Trunk Lock" naming |
| `RTU` | Trunk Unlock | "Remote Trunk Unlock" naming, `showTrunkLockOpenedDialog` in APK |
| `RWS` / `RWS_2` | Window Set | "Remote Window Set" naming |
| `RWR` | Window Raise | "Remote Window Raise" (close) |
| `RSH` | Seat Heat | "Remote Seat Heat", `iovSeatHeat` APK method, `getSeatHeatServiceID` |
| `RPC` | Pre-Conditioning | "Remote Pre-Conditioning" |
| `RCC` / `RCC_2` | Climate Control | "Remote Climate Control" (may be legacy, superseded by RCE_2) |
| `UFR` | Fridge | "Update Fridge", `ColdWarmBoxRequest` APK class |
| `RFD_2` | Find Device | "Remote Find Device" |
| `RDO_2` | Door Open | "Remote Door Open" (possibly trunk-specific) |
| `RDC_2` | Door Close | "Remote Door Close" |
| `RES` | Engine Start | "Remote Engine Start", `remote-control-engine-start` APK string |
| `RQT_2` | Unknown | Possibly "Remote Query Telematics" |
| `RSM` | Unknown | Possibly "Remote Set Mode" |
| `RSV` | Unknown | Possibly "Remote Set Ventilation" |
| `RTB` | Unknown | Possibly "Remote Trunk Button" |
| `RPP` | Unknown | Possibly "Remote Parking Pilot" |
| `RMM` | Unknown | Unknown |
| `REC` | Unknown | Unknown |

### Non-vehicle Service IDs (skipped)

| Service ID | Purpose |
|-----------|---------|
| `AVP` | Autonomous Valet Parking (infrastructure) |
| `PARK` | Parking services |
| `DCL` | Door Central Lock (BLE only) |
| `DIA` | Diagnostics |
| `JOU` | Journey log |
| `MRS` | Unknown infrastructure service |
| `PAC` | Pre-Air Conditioning (possibly legacy) |
| `ZAB/ZAD/ZAE/ZAG/ZAH/ZAN` | ZEEKR/Geely brand specific |

**Rationale**: The `_2` suffix variants appear to be newer API versions. pySmartHashtag uses `RCE_2` (not `RCE`), suggesting the `_2` variants should be preferred when available. For this feature, we'll use the `_2` variants where they exist: `RDL_2`, `RDU_2`, `RWS_2`.

**Alternatives considered**: Using `_2` vs non-`_2` variants. Decision: prefer `_2` following pySmartHashtag's pattern, but fall back to non-`_2` if the API rejects the request or if testing reveals the `_2` variant is unsupported for certain models.

---

## R-004: Climate Command Payload Details

**Question**: What are the specific `serviceParameters` for climate pre-conditioning?

**Decision**: Climate uses `serviceId: "RCE_2"` with the following parameters:

```json
{
  "serviceId": "RCE_2",
  "command": "start" | "stop",
  "serviceParameters": [
    {"key": "rce.conditioner", "value": "1"},
    {"key": "rce.temp", "value": "22.0"},
    {"key": "rce.heat", "value": "front-left"},
    {"key": "rce.level", "value": "3"}
  ],
  "operationScheduling": {
    "duration": 180,
    "interval": 0,
    "occurs": 1,
    "recurrentOperation": false
  }
}
```

**Key details**:
- `rce.conditioner`: `"1"` to enable AC
- `rce.temp`: Temperature as string float (e.g., `"22.0"`), range 16.0–30.0
- `rce.heat` + `rce.level`: Optional seat heating pairs. Locations: `"front-left"`, `"front-right"`, `"steering_wheel"`. Levels: `0`–`3` (0 = off)
- `duration`: 180 minutes for climate (3-hour max)
- For "stop" command, `serviceParameters` can be minimal (just the conditioner key)

**Rationale**: Directly from pySmartHashtag `control/climate.py` `_get_payload()` and `_add_rce_heating_service()` methods. Validated by test suite (`test_actions.py`).

---

## R-005: Charging Command Payload Details

**Question**: What are the specific `serviceParameters` for charging start/stop?

**Decision**: Charging uses `serviceId: "rcs"` (lowercase) with:

```json
{
  "serviceId": "rcs",
  "command": "start",
  "serviceParameters": [
    {"key": "operation", "value": "1"},
    {"key": "rcs.restart", "value": "1"}
  ],
  "operationScheduling": {
    "scheduledTime": null,
    "interval": 0,
    "occurs": 1,
    "recurrentOperation": 0,
    "duration": 6
  }
}
```

**Key details**:
- `command` is always `"start"` (even for stop) — the actual operation is controlled by `serviceParameters`
- Start: `{"key": "operation", "value": "1"}` + `{"key": "rcs.restart", "value": "1"}`
- Stop: `{"key": "operation", "value": "0"}` + `{"key": "rcs.terminate", "value": "1"}`
- Timestamp field is `"timeStamp"` (camelCase with capital S), unlike climate which uses `"timestamp"`
- `duration`: 6 (minutes? units unclear but matches pySmartHashtag)
- `scheduledTime`: `null` for immediate action

**Rationale**: Directly from pySmartHashtag `control/charging.py` `_get_payload()`. Note the `serviceId` is lowercase `"rcs"` unlike climate's uppercase `"RCE_2"`.

---

## R-006: Command Response Structure

**Question**: What does the API return after a command is sent?

**Decision**: Commands return a JSON response with `{"success": true/false}`.

**Rationale**: From pySmartHashtag:
- `control/climate.py`: `api_result = vehicles_response.json()` → `return api_result["success"]`
- `control/charging.py`: `api_result = response.json()` → `return api_result["success"]`

This differs from GET endpoints which return `{"code": 1000, "data": {...}}`. The command response is simpler.

**Note**: The existing `hello_smart` api.py `_signed_request` processes GET responses by checking `code == 1000`. For PUT commands, the response processing will need to check the `success` boolean instead, OR the response may wrap the `success` inside the standard `{"code": 1000, "data": {"success": true}}` envelope. This needs validation during implementation.

---

## R-007: Inferred Door Lock/Unlock Payload

**Question**: What payload is needed for door lock/unlock?

**Decision**: Based on the established command pattern and APK analysis, door lock/unlock likely uses:

```json
{
  "serviceId": "RDL_2",
  "command": "start",
  "serviceParameters": [
    {"key": "operation", "value": "1"}
  ]
}
```

For unlock: `serviceId: "RDU_2"` with the same parameters. Alternatively, a single service ID with different `serviceParameters` to indicate lock vs unlock.

**Rationale**: The APK shows separate service IDs for lock (`RDL`, `RDL_2`) and unlock (`RDU`, `RDU_2`), with `iovLock` and `iovUnlock` as separate methods. This suggests separate service IDs per direction (not a single ID with a parameter switch).

**Confidence**: Medium — the exact payload structure is inferred. Must be verified during implementation testing. The pattern is consistent with how charging uses the same endpoint/method but different `serviceId` values.

---

## R-008: Inferred Horn & Flash Payload

**Question**: What payload is needed for horn, flash lights, and find-my-car?

**Decision**: Based on APK analysis:

- Horn: `serviceId: "RHL"` with `command: "start"`, `serviceParameters: [{"key": "rhl.horn", "value": "1"}]`
- Flash: `serviceId: "RHL"` with `command: "start"`, `serviceParameters: [{"key": "rhl.flash", "value": "1"}]`
- Find My Car (both): `serviceId: "RHL"` with `command: "start"`, `serviceParameters: [{"key": "rhl.horn", "value": "1"}, {"key": "rhl.flash", "value": "1"}]`

**Rationale**: The APK shows a single `RHL` (Remote Horn & Light) service ID, with `lambda$horn$7` and `lambda$flash$6` in `GSVControlsActivity` suggesting they are options within the same service. The key naming convention follows `rce.*` (climate), `rcs.*` (charging) → `rhl.*` (horn/light).

**Confidence**: Medium — key names are inferred from naming patterns. Must be verified during implementation.

---

## R-009: Inferred Window Close Payload

**Question**: What payload is needed for closing windows?

**Decision**: Likely uses `serviceId: "RWS_2"` (Remote Window Set) or `"RWR"` (Remote Window Raise):

```json
{
  "serviceId": "RWS_2",
  "command": "start",
  "serviceParameters": [
    {"key": "rws.window", "value": "close"}
  ]
}
```

**Rationale**: APK shows both `RWS`/`RWS_2` and `RWR` service IDs. `RWR` (Window Raise = close) is likely the close-only command, while `RWS` (Window Set) may allow specifying a position.

**Confidence**: Low — no pySmartHashtag reference implementation for window commands. Must be verified.

---

## R-010: Inferred Fridge/Fragrance/VTM Payloads

**Question**: What payloads are needed for accessory controls?

**Decision**:

### Fridge (ColdWarmBox)
- Uses `serviceId: "UFR"` (Update Fridge)
- APK shows `ColdWarmBoxRequest` class name and `iovColdWarmBox` methods
- Likely: `serviceParameters: [{"key": "ufr.status", "value": "1"}]` for on, `"0"` for off

### Fragrance
- APK shows `iovFragranceQuery` for reading status, `FragranceChannel` response class
- Command likely uses the same telematics PUT with a fragrance-specific serviceId
- APK shows `/remote-control/vehicle/fragrance/{vin}` endpoint — may use separate PUT to this URL instead of telematics

### VTM
- APK shows `iovVTMSettingQuery` and `setVtmTSActive` methods
- GET via `/remote-control/getVtmSettingStatus`
- Command likely uses telematics PUT with a VTM serviceId, or a separate PUT to the VTM endpoint

**Confidence**: Low for all three — no pySmartHashtag implementation, payloads are speculative. These are P5/P7 priority and can be investigated iteratively.

---

## R-011: Schedule Command Endpoints

**Question**: How are charging and climate schedules managed?

**Decision**: Schedules use a separate endpoint: `PUT /remote-control/schedule/{vin}`

**Evidence**:
- APK string: `/remote-control/schedule/{vin}`
- Existing `hello_smart` integration already has `async_get_climate_schedule()` doing GET to this endpoint
- APK shows `OperationScheduling` class with `scheduledTime`, `duration`, `interval`, `occurs`, `recurrentOperation` fields
- Charging reservations use `PUT /remote-control/charging/reservation/{vin}`

**Rationale**: Schedule updates use their own dedicated endpoints rather than the telematics command endpoint. This makes sense as schedules are persistent configuration changes, not immediate vehicle commands.

**Confidence**: Medium — endpoint paths are confirmed, but exact PUT request body schemas need verification.

---

## R-012: HMAC Signing for PUT Requests

**Question**: Does the existing HMAC signing work for PUT requests?

**Decision**: Yes — the existing `_signed_request` infrastructure supports PUT.

**Evidence**:
- The existing `api.py` `_signed_request` method accepts `method` parameter and supports POST already
- pySmartHashtag's `generate_default_header` accepts `method="PUT"` explicitly
- The HMAC signature includes the method, URL, and body — all properly handled for PUT/POST
- The existing `auth.py` `build_signed_headers` generates headers that work with any HTTP method

**Required change**: The existing `_signed_request` in `api.py` currently supports GET and POST. It needs to be extended to also handle PUT. This is a trivial change — pass `method="PUT"` to the session request.

---

## R-013: Error Handling for Commands

**Question**: What error codes are relevant for commands?

**Decision**: Commands use the same error infrastructure as GET endpoints, plus command-specific errors.

**Known error codes from existing integration**:
- `1000`: Success
- `1402`: Token expired → trigger re-auth
- `8006`: Vehicle not linked

**Additional from APK**:
- `iovLock error`, `iovLock fail`, `iovUnlock error`: Commands can fail with descriptive error messages
- `handleIovLockTimeout`, `handleIovUnlockTimeout`: Commands have timeout handling
- `seatHeat fail`, `seatHeat onError`: Climate commands have error callbacks
- The APK has `GSVControlResponse` and `GSVControlState.ServiceState` for tracking command state

**Decision**: Wrap all command calls in the same try/except pattern used for GET endpoints. Surface command failures via HA's `HomeAssistantError` exception so the UI shows a notification.

---

## R-014: Optimistic Updates and Delayed Refresh

**Question**: How should the UI reflect command state changes?

**Decision**: Use HA's built-in optimistic update pattern:
1. Send command via PUT
2. If successful, immediately update the coordinator's cached `VehicleData` to reflect expected state
3. Call `async_write_ha_state()` on the entity to push the UI update
4. Schedule a delayed `coordinator.async_request_refresh()` after 5–10 seconds to confirm actual state

**Rationale**: The vehicle takes several seconds to execute commands. Without optimistic updates, the user would see no feedback until the next poll cycle (60 seconds). The delayed refresh reconciles the optimistic state with reality.

**Pattern reference**: This is standard HA practice used by integrations like `hue`, `zwave`, and `tesla_custom`.

---

## R-015: Rate Limiting Between Commands

**Question**: How to prevent command flooding?

**Decision**: Enforce a per-vehicle cooldown of 5 seconds between commands.

**Implementation**: Track last command timestamp per VIN in the coordinator. Before sending any command, check if the cooldown period has elapsed. If not, raise a `HomeAssistantError` with a user-friendly message.

**Rationale**: The APK shows timeout handling for lock/unlock (suggesting the API expects sequential commands), and rapid-fire commands could overwhelm both the API and the vehicle's telematics unit. pySmartHashtag's 3-retry loop also suggests commands should not be overlapped.

---

## R-016: Vehicle Session Selection Before Commands

**Question**: Must `async_select_vehicle()` be called before commands?

**Decision**: Yes — `async_select_vehicle(vin)` must be called before any command.

**Evidence**: pySmartHashtag calls `await self.account.select_active_vehicle(self.vin)` before every command in both `control/climate.py` and `control/charging.py`.

**Implementation**: The existing `coordinator.py` already calls `async_select_vehicle()` before GET requests during each poll cycle. For commands, the command method should call `async_select_vehicle()` immediately before the PUT request.

---

## R-017: Base URL Selection (V1 vs V2 API)

**Question**: Which base URL to use for commands?

**Decision**: Use the same base URL as the vehicle's GET endpoints.

**Evidence**: pySmartHashtag's `ChargingControl._set_charging()` uses `self.account.vehicles[self.vin].base_url` which is dynamically set based on vehicle series:
- `HX` (Smart #1): `API_BASE_URL` (`https://api.ecloudeu.com`)
- `HC` (Smart #3): `API_BASE_URL` (`https://api.ecloudeu.com`)
- `HY` (Smart #5): `API_BASE_URL_V2` (`https://apiv2.ecloudeu.com`)

The existing `hello_smart` integration uses `API_BASE_URL` for all vehicles. If Smart #5 support is needed, the base URL selection logic should be added.

**For now**: Use `API_BASE_URL` (v1) as the existing integration already does. Smart #5 support can be added later.
