# Feature Specification: Hello-Smart Foundation

**Feature Branch**: `001-hello-smart-foundation`  
**Created**: 2026-03-07  
**Status**: Draft  
**Input**: User description: "Hello-Smart: A Home Assistant custom integration for Smart brand vehicles with EU and INTL auth support, vehicle status monitoring, charging state, and OTA update information."

## User Scenarios & Testing *(mandatory)*

### User Story 1 — INTL Region Setup and Vehicle Discovery (Priority: P1)

A Smart vehicle owner in an international market (Australia, Singapore, Israel, etc.) adds the "Hello Smart" integration and selects "INTL" as their region. The integration authenticates using the INTL login flow and discovers their vehicles. Within seconds the user sees battery level, charging status, and estimated range on their dashboard.

**Why this priority**: INTL uses a simpler 3-step authentication flow, making it the fastest path to a working MVP. Without successful authentication and vehicle discovery, no other functionality is possible.

**Independent Test**: Can be fully tested by configuring a real or mocked INTL Smart account and verifying that vehicles appear as devices with at least one sensor entity showing battery level.

**Acceptance Scenarios**:

1. **Given** a user with a valid INTL Smart account and at least one vehicle, **When** they complete the config flow with correct credentials and INTL region selected, **Then** each vehicle appears as a device in HA with its VIN as an identifier, and sensor entities for battery level, range, and charging status are created.
2. **Given** a user enters incorrect credentials, **When** they submit the config flow, **Then** the flow shows an authentication error and does not create a config entry.
3. **Given** an INTL account with multiple vehicles, **When** setup completes, **Then** each vehicle is registered as a separate device with its own entities.

---

### User Story 2 — EU Region Setup and Vehicle Discovery (Priority: P2)

A Smart vehicle owner in Europe opens Home Assistant, navigates to Integrations, and adds "Hello Smart." They are prompted for their Smart account email, password, and region (EU). The integration authenticates against the Smart EU cloud service using the multi-step Gigya-based login flow, discovers all vehicles linked to the account, and registers each vehicle as a device in Home Assistant. The resulting entities and experience are identical to the INTL flow.

**Why this priority**: Expands coverage to the European market. Depends on the same vehicle-discovery and entity-creation infrastructure built for P1, but uses a different (more complex) authentication path.

**Independent Test**: Can be fully tested by configuring a real or mocked EU Smart account and verifying vehicle devices and entities appear identically to the INTL path.

**Acceptance Scenarios**:

1. **Given** a user with a valid EU Smart account and at least one vehicle, **When** they complete the config flow with correct credentials and EU region, **Then** each vehicle appears as a device with the same entity types as the INTL path.
2. **Given** invalid EU credentials, **When** they submit the config flow, **Then** an authentication error is shown.
3. **Given** a user's EU account has no vehicles linked, **When** they complete the config flow, **Then** the config entry is created but no device or entity is registered, and a warning is logged.

---

### User Story 3 — Periodic Vehicle Status Updates (Priority: P3)

After initial setup, the integration automatically polls the Smart cloud API at a configurable interval (default: 5 minutes) to refresh vehicle data. The user sees updated battery percentage, charging state, door/window status, climate status, and estimated range on their HA dashboard without any manual action.

**Why this priority**: Continuous monitoring is the core ongoing value of the integration. It depends on successful auth and vehicle discovery from P1/P2.

**Independent Test**: Can be tested by verifying that entity values change over time when the vehicle's status changes (e.g., plugging in the charger causes the charging binary sensor to turn on within one polling interval).

**Acceptance Scenarios**:

1. **Given** a configured Hello Smart integration with one or more vehicles, **When** one polling interval elapses, **Then** all vehicle sensor and binary sensor entities are updated with the latest data from the Smart API.
2. **Given** the Smart API returns an authentication error during a poll, **When** the coordinator detects the error, **Then** it re-authenticates automatically and retries the data fetch without user intervention.
3. **Given** the Smart API is unreachable, **When** a poll fails, **Then** the coordinator marks entities as unavailable and retries at the next interval.

---

### User Story 4 — Vehicle Location Tracking (Priority: P4)

The integration provides a device tracker entity for each vehicle, reporting latitude, longitude, and an optional address. The user can see their vehicle's last-known location on the HA map.

**Why this priority**: Location tracking is a high-value feature but builds on top of the polling infrastructure from P3.

**Independent Test**: Can be tested by verifying the device_tracker entity has valid GPS coordinates that update when the vehicle moves.

**Acceptance Scenarios**:

1. **Given** a configured vehicle with location data available from the API, **When** a poll completes, **Then** a device_tracker entity reports the vehicle's latitude and longitude.
2. **Given** the API returns no location data for a vehicle, **When** a poll completes, **Then** the device_tracker entity is marked as unavailable rather than reporting stale or zero coordinates.

---

### User Story 5 — OTA Update Information (Priority: P5)

The integration exposes the current firmware version and target firmware version for each vehicle as sensor entities. The user can see whether an over-the-air update is available.

**Why this priority**: Informational and lower urgency than core vehicle status. Requires a separate API endpoint but uses the same polling infrastructure.

**Independent Test**: Can be tested by verifying sensors display current and target firmware versions, and that an update-available binary sensor reflects when the two versions differ.

**Acceptance Scenarios**:

1. **Given** a vehicle with OTA data from the API, **When** a poll completes, **Then** sensors for current firmware version and target firmware version are populated.
2. **Given** target version differs from current version, **When** a poll completes, **Then** an "update available" binary sensor reports true.
3. **Given** target version equals current version, **When** a poll completes, **Then** the "update available" binary sensor reports false.

---

### User Story 6 — Diagnostics Dump (Priority: P6)

A user experiencing issues can download a diagnostics dump from the integration's page in HA. The dump contains account metadata, vehicle data, and coordinator state with all sensitive fields (tokens, passwords, user IDs, VINs) redacted.

**Why this priority**: Essential for debugging but does not block normal operation.

**Independent Test**: Can be tested by triggering a diagnostics download and verifying the output contains vehicle data with sensitive fields replaced by redaction markers.

**Acceptance Scenarios**:

1. **Given** a configured Hello Smart integration, **When** the user downloads diagnostics, **Then** the output contains vehicle data and coordinator state.
2. **Given** the diagnostics output, **When** inspecting all fields, **Then** no tokens, passwords, or user IDs appear in plain text.

---

### Edge Cases

- What happens when the Smart API rate-limits requests? The integration must respect rate limits (HTTP 429), wait the indicated period, and retry without crashing the coordinator.
- What happens when a user changes their Smart password after initial setup? The next poll fails authentication; the integration must raise a re-authentication flow in HA so the user can update credentials without removing and re-adding the integration.
- What happens when a vehicle is added to or removed from the Smart account after initial setup? On the next full poll, newly discovered vehicles should be registered as new devices; vehicles no longer in the API response should have their entities marked as unavailable.
- What happens during HA restart? The integration must re-authenticate and resume polling automatically without user intervention.
- What happens if the user configures the same Smart account twice? The config flow must detect a duplicate account (by username + region) and reject the second setup attempt.

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: System MUST provide a config flow that collects username, password, and region (EU or INTL) from the user.
- **FR-002**: System MUST authenticate against the Smart EU API using the multi-step Gigya-based login flow (username/password → login_token → access_token → API session token).
- **FR-003**: System MUST authenticate against the Smart INTL API using the three-step flow (username/password login → OAuth authCode exchange → vehicle API session).
- **FR-004**: System MUST select the correct authentication flow and API endpoints automatically based on the user's region selection.
- **FR-005**: System MUST retrieve the list of vehicles associated with the authenticated account and register each vehicle as a device using the VIN as an identifier.
- **FR-006**: System MUST create sensor entities for each vehicle: battery level (%), estimated range, and charging status.
- **FR-007**: System MUST create binary sensor entities for each vehicle: door open/closed, window open/closed, and charging cable connected.
- **FR-008**: System MUST create a device tracker entity for each vehicle with GPS latitude and longitude.
- **FR-009**: System MUST create sensor entities for OTA information: current firmware version and target firmware version.
- **FR-010**: System MUST create a binary sensor entity indicating whether a firmware update is available (target version differs from current version).
- **FR-011**: System MUST poll the Smart API at a configurable interval (default 5 minutes) to refresh all vehicle data.
- **FR-012**: System MUST store access and refresh tokens in memory and automatically re-authenticate when tokens expire (on HTTP 401 or API error code 1402).
- **FR-013**: System MUST never hardcode credentials, tokens, or API keys; all secrets must be stored in the config entry.
- **FR-014**: System MUST redact all sensitive data (tokens, passwords, user IDs) from log output.
- **FR-015**: System MUST constrain all outbound API URLs to known Smart API base URLs; no user-controlled URL construction is permitted.
- **FR-016**: System MUST enforce HTTPS with certificate validation for all API communication.
- **FR-017**: System MUST generate region-appropriate signed request headers (EU: HMAC-based signing; INTL: X-Ca-Key gateway headers with x-api-signature-version signing).
- **FR-018**: System MUST support multiple vehicles per account, each as a separate HA device with independent entities.
- **FR-019**: System MUST raise a re-authentication flow when stored credentials become invalid (e.g., password change) rather than silently failing.
- **FR-020**: System MUST detect duplicate account configurations (same username + region) and reject them during setup.
- **FR-021**: System MUST mark entities as unavailable when the API is unreachable and resume updating them when connectivity is restored.
- **FR-022**: System MUST provide a diagnostics dump with all sensitive fields redacted.
- **FR-023**: System MUST handle API rate limiting (HTTP 429) by waiting the indicated retry period before retrying.

### Key Entities

- **Account**: Represents a user's Smart account. Key attributes: username, region (EU/INTL), authentication state (tokens, expiry).
- **Vehicle**: Represents a single Smart vehicle linked to an account. Key attributes: VIN, model name, model year, associated account.
- **Vehicle Status**: Point-in-time snapshot of a vehicle's state. Key attributes: battery level, estimated range, charging state, door status (per-door), window status (per-window), climate state, GPS coordinates.
- **OTA Info**: Firmware update state for a vehicle. Key attributes: current firmware version, target firmware version, update availability.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: Users can complete integration setup (config flow through first entity appearance) in under 2 minutes for both EU and INTL regions.
- **SC-002**: All vehicle sensor and binary sensor entities update within one polling interval (default 5 minutes) of a vehicle state change.
- **SC-003**: The integration recovers from an expired-token scenario automatically without user intervention in 100% of cases.
- **SC-004**: After an API outage, entities return to available state within one polling interval of connectivity being restored.
- **SC-005**: Diagnostics dumps contain zero instances of plain-text tokens, passwords, or user IDs.
- **SC-006**: The integration supports accounts with up to 10 vehicles without degraded performance or entity creation failures.
- **SC-007**: 90% of users successfully complete first-time setup on their first attempt without encountering unrecoverable errors.

## Assumptions

- The Smart cloud API (ecloudeu.com, sg-app-api.smart.com) endpoints and authentication flows remain stable and match the behavior observed in the Hello Smart mobile app as of early 2026.
- EU and INTL are the only two region variants; if additional regions are introduced, a constitution amendment and spec update will be needed.
- The default polling interval of 5 minutes is an acceptable balance between data freshness and API rate limits. Users can adjust this via the options flow.
- Vehicle location data may not be available in all markets or for all vehicle models; the integration handles missing location gracefully.
- The Smart API uses JSON responses for all data endpoints.
- API keys/app identifiers used by the Hello Smart mobile app (e.g., the Gigya API key for EU, the X-Ca-Key for INTL) are public application identifiers, not user secrets, and can be stored as constants.
