# Feature Specification: API Command Controls

**Feature Branch**: `003-api-command-controls`  
**Created**: 2026-03-08  
**Status**: Draft  
**Input**: User description: "Implement all POST/PUT/PATCH command endpoints from the Smart vehicle cloud API as interactive Home Assistant controls for the existing Hello Smart custom integration."

## User Scenarios & Testing *(mandatory)*

### User Story 1 — Door Lock and Unlock Control (Priority: P1)

A Smart vehicle owner opens their Home Assistant dashboard and sees a lock entity for their vehicle's doors. They tap "Unlock" to remotely unlock the vehicle before walking to the car, or tap "Lock" from inside the house to secure the vehicle they forgot to lock. The lock entity reflects the current lock state and updates within seconds after a command is sent.

**Why this priority**: Vehicle security is the most universally desired remote command. Every Smart vehicle supports door locking, making this the broadest-reach, highest-value command to implement first. It also establishes the foundational command infrastructure (POST request pattern, optimistic updates, delayed refresh) that all other commands will reuse.

**Independent Test**: From the HA UI, tap "Unlock" on the vehicle lock entity. Verify the entity optimistically switches to "unlocked" immediately, then confirm the vehicle's doors actually unlock within 15 seconds. Repeat with "Lock" and verify the reverse.

**Acceptance Scenarios**:

1. **Given** a configured Hello Smart integration with a vehicle whose doors are locked, **When** the user triggers "Unlock" on the door lock entity, **Then** the entity optimistically updates to "unlocked" and the vehicle's doors unlock within 15 seconds.
2. **Given** a configured vehicle whose doors are unlocked, **When** the user triggers "Lock" on the door lock entity, **Then** the entity optimistically updates to "locked" and the vehicle's doors lock within 15 seconds.
3. **Given** a command is sent but the vehicle is offline or unreachable, **When** the API returns an error, **Then** the optimistic state is reverted and the user sees a notification that the command failed.
4. **Given** a vehicle that supports the lock command, **When** the integration loads, **Then** a lock entity appears under the vehicle device. Vehicles that do not support remote lock (per capabilities) do not show a lock entity.

---

### User Story 2 — Climate Pre-Conditioning Start and Stop (Priority: P2)

A Smart vehicle owner wants to warm up or cool down their car before getting in. They use a climate control entity in HA to start climate pre-conditioning with a target temperature. They can also stop it remotely. The entity shows whether climate is currently active and the set temperature.

**Why this priority**: Climate pre-conditioning is the second-most requested remote command for EV owners. It provides immediate tangible comfort value and is a common automation trigger (e.g., "pre-condition my car at 7:00 AM on weekdays").

**Independent Test**: Set the climate entity to 22°C and turn it on. Verify the vehicle starts pre-conditioning within 15 seconds. Turn it off and verify the vehicle stops.

**Acceptance Scenarios**:

1. **Given** a configured vehicle with climate off, **When** the user sets a target temperature and turns on the climate entity, **Then** the entity shows "heating" or "cooling" mode and the vehicle begins pre-conditioning.
2. **Given** a vehicle with climate running, **When** the user turns off the climate entity, **Then** the entity shows "off" and the vehicle stops pre-conditioning.
3. **Given** a vehicle where climate is not supported or the endpoint returns an error, **When** the integration loads, **Then** no climate entity is created.
4. **Given** a user sets a temperature outside the vehicle's supported range, **When** the command is sent, **Then** the temperature is clamped to the valid range (assumed 16–30°C).

---

### User Story 3 — Charging Start, Stop, and Target SOC (Priority: P3)

A Smart vehicle owner plugged in at home wants to start or stop charging remotely and adjust their target state-of-charge (SOC) percentage. They use a switch entity to start/stop charging and a number slider to set the target SOC between 50% and 100%.

**Why this priority**: Charging control is essential for EV owners managing time-of-use electricity pricing or wanting to limit SOC for battery longevity. It pairs naturally with the existing charging status sensors.

**Independent Test**: With the vehicle plugged in, toggle the charging switch to "on" and verify charging begins. Adjust the target SOC slider to 80% and verify the vehicle's target updates accordingly.

**Acceptance Scenarios**:

1. **Given** a vehicle with a charger connected and not charging, **When** the user turns on the charging switch, **Then** the vehicle begins charging and the switch shows "on".
2. **Given** a vehicle that is actively charging, **When** the user turns off the charging switch, **Then** charging stops and the switch shows "off".
3. **Given** no charger is connected, **When** the user attempts to start charging, **Then** the command fails gracefully and the user is notified that no charger is connected.
4. **Given** a vehicle with a target SOC of 100%, **When** the user moves the SOC slider to 80%, **Then** the vehicle's target SOC updates to 80%.

---

### User Story 4 — Horn, Flash Lights, and Find My Car (Priority: P4)

A Smart vehicle owner in a parking lot can't find their car. They press the "Find My Car" button in HA to trigger a horn honk and light flash simultaneously. They can also press individual "Horn" or "Flash Lights" buttons independently.

**Why this priority**: Alert commands are simple, universally supported, and immediately verifiable. They are momentary actions with no state to track, making them low-risk to implement.

**Independent Test**: Press the "Horn" button in HA and verify the vehicle honks once within 15 seconds. Press "Flash Lights" and verify lights flash. Press "Find My Car" and verify both occur.

**Acceptance Scenarios**:

1. **Given** a configured vehicle, **When** the user presses the "Horn" button entity, **Then** the vehicle honks its horn once.
2. **Given** a configured vehicle, **When** the user presses the "Flash Lights" button entity, **Then** the vehicle flashes its lights.
3. **Given** a configured vehicle, **When** the user presses the "Find My Car" button entity, **Then** the vehicle honks and flashes simultaneously.
4. **Given** the vehicle is offline, **When** a button is pressed, **Then** the user is notified that the command could not be delivered.

---

### User Story 5 — Accessory Controls: Fridge, Fragrance, and Locker (Priority: P5)

A Smart #1 owner with optional accessories (mini-fridge, fragrance diffuser, front trunk locker) can toggle each accessory on/off or lock/unlock via HA switch and lock entities. Vehicles without a particular accessory do not show the corresponding entity.

**Why this priority**: Accessory commands are niche (not all vehicles have them), but they complete the feature parity with the mobile app for well-equipped vehicles. They reuse the same command infrastructure built in P1.

**Independent Test**: For a vehicle with a mini-fridge, toggle the fridge switch to "on" and verify the fridge activates. For a vehicle without a fridge, verify no fridge switch entity exists.

**Acceptance Scenarios**:

1. **Given** a vehicle with a mini-fridge that is off, **When** the user turns on the fridge switch, **Then** the fridge activates and the switch reflects "on".
2. **Given** a vehicle with a fragrance diffuser that is off, **When** the user turns on the fragrance switch, **Then** the diffuser activates.
3. **Given** a vehicle with a front trunk locker that is locked, **When** the user triggers "Unlock" on the locker lock entity, **Then** the locker unlocks.
4. **Given** a vehicle without a mini-fridge, **When** the integration loads, **Then** no fridge switch entity is created.
5. **Given** a vehicle without a front trunk locker, **When** the integration loads, **Then** no locker lock entity is created.

---

### User Story 6 — Window Close Command (Priority: P6)

A Smart vehicle owner realizes they left a window open after parking. They press a "Close Windows" button in HA to remotely close all windows. For safety, only a close command is available — no remote window open.

**Why this priority**: Window control is a safety-focused convenience feature. It is intentionally limited to close-only to prevent misuse. Lower priority because it is less frequently needed than lock or climate.

**Independent Test**: With a window open, press the "Close Windows" button and verify all windows close within 30 seconds.

**Acceptance Scenarios**:

1. **Given** a vehicle with one or more windows open, **When** the user presses the "Close Windows" button, **Then** all windows close.
2. **Given** all windows are already closed, **When** the user presses the button, **Then** the command succeeds without error (idempotent).
3. **Given** the integration loads, **Then** no "Open Windows" command or entity is ever exposed (close-only for safety).

---

### User Story 7 — Vehicle Theft Monitoring Toggle (Priority: P7)

A Smart vehicle owner can enable or disable Vehicle Theft Monitoring (VTM) via a switch entity in HA. This mirrors the toggle in the mobile app and controls whether the vehicle sends alerts for unauthorized movement or geofence violations.

**Why this priority**: VTM is a security setting that most users configure once and leave. Lower priority than active commands but still valuable for automation scenarios (e.g., auto-enable VTM when leaving home).

**Independent Test**: Toggle the VTM switch to "on" and verify the VTM GET endpoint reflects the change on the next poll.

**Acceptance Scenarios**:

1. **Given** a vehicle with VTM disabled, **When** the user turns on the VTM switch, **Then** VTM is enabled and the switch reflects "on".
2. **Given** a vehicle with VTM enabled, **When** the user turns off the VTM switch, **Then** VTM is disabled.
3. **Given** VTM is not supported by the vehicle, **When** the integration loads, **Then** no VTM switch entity is created.

---

### User Story 8 — Charging and Climate Schedule Configuration (Priority: P8)

A Smart vehicle owner can set their charging schedule start/end times and climate pre-conditioning schedule time directly from HA using time-picker entities. They can also toggle the climate schedule on/off with a switch. This eliminates the need to open the mobile app for schedule management.

**Why this priority**: Schedule management is useful but lower urgency — most users set schedules once. It rounds out the full command parity with the mobile app.

**Independent Test**: Set the charging start time to 22:00 via the time entity and verify the charging reservation reflects the new time on the next poll.

**Acceptance Scenarios**:

1. **Given** a vehicle with a charging reservation, **When** the user sets the start time to 22:00 and end time to 06:00, **Then** the charging schedule updates to reflect those times.
2. **Given** a vehicle with a climate schedule, **When** the user sets the schedule time to 07:30, **Then** the climate schedule updates.
3. **Given** a vehicle with a climate schedule disabled, **When** the user toggles the climate schedule switch to "on", **Then** the climate schedule is enabled.
4. **Given** a vehicle without charging schedule support, **When** the integration loads, **Then** no schedule time entities are created.

---

### Edge Cases

- What happens when a command is sent while the vehicle is driving? — The API is expected to reject the command; the integration surfaces the error to the user without crashing.
- What happens when two commands are sent in rapid succession? — The second command queues behind the first; no race condition in optimistic state updates. A minimum 5-second interval between commands to the same vehicle is enforced.
- What happens when the API acknowledges a command (code 1000) but the vehicle never acts? — The delayed refresh (5–10 seconds post-command) will show the unchanged state, effectively reverting the optimistic update.
- What happens when a shared-vehicle user without command permissions sends a command? — The API returns an authorization error; the integration surfaces a clear "permission denied" message.
- What happens when the integration is reloaded while a delayed refresh is pending? — The pending refresh is cancelled cleanly; state is re-fetched from the API on the next poll.
- What happens when a command endpoint doesn't exist for the user's region? — Same silent-failure pattern as GET endpoints: log at debug level and hide the corresponding entity.

## Assumptions

- Command endpoints use the same HMAC-SHA1 signed request pattern as GET endpoints, with the same base URL (`https://api.ecloudeu.com`) and standard response envelope (`{"code": 1000, "data": {...}}`).
- Command endpoints are identical between EU and INTL regions (same paths, same request bodies) — only the signing secrets and app identifiers differ, which is already handled by the existing `_signed_request` infrastructure.
- The exact API paths, HTTP methods, and request body schemas for command endpoints will be confirmed via APK reverse engineering and cross-referencing with the pySmartHashtag open-source library during the planning/research phase. The paths listed in this spec are educated guesses based on GET endpoint naming conventions.
- Climate temperature range is 16–30°C based on standard automotive HVAC ranges. The exact range will be confirmed from the APK or API responses.
- Target SOC range is 50–100% based on common EV charging practices. The exact minimum will be confirmed.
- The `async_select_vehicle()` call is required before sending commands to ensure the correct vehicle session is active. This is already implemented for GET endpoints.
- Horn and flash commands are momentary — the API fires once and does not provide a duration or repeat parameter.

## Requirements *(mandatory)*

### Functional Requirements

#### Command Infrastructure

- **FR-001**: System MUST reverse-engineer all POST, PUT, and PATCH command endpoints from the Smart mobile APKs (EU and INTL) and cross-reference with the pySmartHashtag open-source library to confirm paths, methods, and request body schemas.
- **FR-002**: System MUST send all commands using the existing `_signed_request` infrastructure with HMAC-SHA1 signed headers, validating URLs against the existing allowlist.
- **FR-003**: System MUST call `async_select_vehicle()` before sending any command that requires an active vehicle session.
- **FR-004**: System MUST optimistically update the coordinator's cached data immediately after a successful command (API response code 1000) so the UI reflects the expected new state without waiting for a poll.
- **FR-005**: System MUST trigger a coordinator data refresh 5–10 seconds after a successful command to confirm the vehicle acted on the command and reconcile optimistic state with actual state.
- **FR-006**: System MUST enforce a minimum 5-second interval between consecutive commands to the same vehicle to prevent API rate limiting and command collisions.
- **FR-007**: System MUST revert optimistic state updates when a command fails (non-1000 response code, network error, or timeout).

#### Vehicle Security Commands

- **FR-010**: System MUST provide a lock entity for vehicle door lock/unlock, supporting both the lock and unlock actions.
- **FR-011**: System MUST expose the door lock entity only for vehicles that support remote lock/unlock per their capabilities.

#### Climate Commands

- **FR-020**: System MUST provide a climate entity that allows starting and stopping climate pre-conditioning.
- **FR-021**: System MUST allow setting a target temperature for climate pre-conditioning within the vehicle's supported range.
- **FR-022**: System MUST clamp temperature values to the valid range rather than rejecting out-of-range requests.

#### Charging Commands

- **FR-030**: System MUST provide a switch entity for starting and stopping vehicle charging.
- **FR-031**: System MUST provide a number entity (slider) for setting the target SOC percentage.
- **FR-032**: Target SOC MUST be constrained to the valid range supported by the vehicle (assumed 50–100% until confirmed).

#### Alert Commands

- **FR-040**: System MUST provide button entities for horn honk, flash lights, and find-my-car (combined horn + flash).
- **FR-041**: Alert commands MUST be momentary — each button press triggers a single activation with no repeat or loop capability.

#### Accessory Commands

- **FR-050**: System MUST provide a switch entity for toggling the mini-fridge on/off (vehicles with fridge only).
- **FR-051**: System MUST provide a switch entity for toggling the fragrance diffuser on/off (vehicles with fragrance only).
- **FR-052**: System MUST provide a lock entity for the front trunk locker lock/unlock (vehicles with locker only).

#### Window Command

- **FR-060**: System MUST provide a button entity for closing all windows.
- **FR-061**: System MUST NOT provide any command to remotely open windows (close-only for safety).

#### VTM Command

- **FR-070**: System MUST provide a switch entity for enabling/disabling Vehicle Theft Monitoring.

#### Schedule Commands

- **FR-080**: System MUST provide time-picker entities for setting charging schedule start and end times.
- **FR-081**: System MUST provide a time-picker entity for setting the climate schedule activation time.
- **FR-082**: System MUST provide a switch entity for enabling/disabling the climate schedule.

#### Dynamic Visibility

- **FR-090**: Command entities MUST only appear for vehicles that support the corresponding feature, determined by the capabilities endpoint data, API endpoint availability, or feature-specific GET endpoint responses.
- **FR-091**: If a command endpoint returns an error indicating the feature is unavailable (HTTP 403, API codes 1405 or 8153), the corresponding command entity MUST NOT be created, consistent with the existing GET endpoint behavior.

#### Safety

- **FR-100**: The door unlock action MUST require explicit user intent — the standard lock platform interaction model satisfies this requirement.
- **FR-101**: No remote window-open command MUST ever be exposed.
- **FR-102**: All command API URLs MUST be validated against the existing URL allowlist before sending.

### Key Entities

- **Door Lock**: Represents the vehicle's central locking system. States: locked/unlocked. Actions: lock, unlock.
- **Climate Control**: Represents the vehicle's HVAC pre-conditioning system. States: off/heating/cooling. Attributes: target temperature. Actions: turn on (with temperature), turn off, set temperature.
- **Charging Switch**: Represents the vehicle's charging state as a controllable toggle. States: on (charging)/off (not charging). Actions: turn on (start charging), turn off (stop charging).
- **Target SOC**: Represents the desired charge level as a numeric value. Range: 50–100%. Actions: set value.
- **Horn Button**: Momentary action to honk the vehicle's horn. No state.
- **Flash Lights Button**: Momentary action to flash the vehicle's lights. No state.
- **Find My Car Button**: Momentary action to trigger horn + lights simultaneously. No state.
- **Close Windows Button**: Momentary action to close all vehicle windows. No state.
- **Fridge Switch**: Represents the mini-fridge on/off state. Actions: turn on, turn off.
- **Fragrance Switch**: Represents the fragrance diffuser on/off state. Actions: turn on, turn off.
- **Locker Lock**: Represents the front trunk locker lock state. States: locked/unlocked. Actions: lock, unlock.
- **VTM Switch**: Represents Vehicle Theft Monitoring enabled/disabled. Actions: turn on, turn off.
- **Charging Schedule Start Time**: Time-picker for the charging reservation start time (HH:MM format).
- **Charging Schedule End Time**: Time-picker for the charging reservation end time (HH:MM format).
- **Climate Schedule Time**: Time-picker for the climate pre-conditioning activation time (HH:MM format).
- **Climate Schedule Switch**: Toggle for enabling/disabling the climate pre-conditioning schedule.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: Users can lock or unlock their vehicle from the HA dashboard within 15 seconds of pressing the control.
- **SC-002**: Users can start or stop climate pre-conditioning and see the state reflected in HA within 15 seconds.
- **SC-003**: Users can start or stop charging and adjust target SOC, with the change confirmed on the next coordinator refresh.
- **SC-004**: Horn, flash, and find-my-car button presses result in audible/visible vehicle feedback within 15 seconds.
- **SC-005**: Accessory controls (fridge, fragrance, locker) change state within 15 seconds for vehicles that have them, and are invisible for vehicles that do not.
- **SC-006**: All command entities are dynamically visible — vehicles without a given feature show zero command entities for that feature.
- **SC-007**: Failed commands (vehicle offline, API error, permission denied) surface a clear error notification to the user; no silent failures for user-initiated actions.
- **SC-008**: 95% of command round-trips (send command → confirmed state change) complete within 30 seconds under normal network conditions.
- **SC-009**: The integration continues to poll and display read-only sensor data even if all command endpoints are unavailable, with no regression to existing functionality.
