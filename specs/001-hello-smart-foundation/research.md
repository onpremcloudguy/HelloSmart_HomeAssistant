# Research: Hello-Smart Foundation

**Branch**: `001-hello-smart-foundation` | **Date**: 2026-03-07

## R1: Smart API EU Authentication Flow

**Decision**: Implement the multi-step Gigya-based login flow matching the Hello Smart mobile app behavior.

**Rationale**: The EU flow is the only documented authentication path for European Smart accounts. It uses Gigya (SAP Customer Identity) as the identity provider with a context-based OIDC authorization. This is the primary market for Smart #1 vehicles.

**Flow (4 steps)**:

1. **GET context** → `https://awsapi.future.smart.com/login-app/api/v1/authorize?uiLocales=de-DE` — returns a redirect with a `context` parameter.
2. **POST login** → `https://auth.smart.com/accounts.login` — sends `loginID`, `password`, Gigya `APIKey` (`3_L94eyQ-wvJhWm7Afp1oBhfTGXZArUfSHHW9p9Pncg513hZELXsxCfMWHrF8f5P5a`), returns `login_token` + `expires_in`.
3. **GET authorize** → `https://auth.smart.com/oidc/op/v1.0/{API_KEY}/authorize/continue?context={context}&login_token={login_token}` — redirects with `access_token` and `refresh_token` in URL fragment.
4. **POST session** → `https://api.ecloudeu.com/auth/account/session/secure?identity_type=smart` — exchanges `accessToken` for `api_access_token`, `api_refresh_token`, `api_user_id`.

**Alternatives considered**:
- HA's built-in `config_entry_oauth2_flow`: Not applicable because Smart's Gigya flow is not a standard OAuth2 redirect flow with PKCE. It's a server-to-server credential exchange that mimics the mobile app.

## R2: Smart API INTL Authentication Flow

**Decision**: Implement the three-step INTL login flow for international markets (Australia, Singapore, Israel, etc.).

**Rationale**: International markets use `sg-app-api.smart.com` with a simpler flow that doesn't require request signatures for authentication endpoints, only for the final session exchange.

**Flow (3 steps)**:

1. **POST login** → `https://sg-app-api.smart.com/iam/service/api/v1/login` — sends `email` + `password` with `X-Ca-Key: 204587190` headers. Returns `accessToken`, `idToken`, `refreshToken`, `userId`.
2. **GET authorize** → `https://sg-app-api.smart.com/iam/service/api/v1/oauth20/authorize?accessToken={accessToken}` — uses `Xs-Auth-Token: {idToken}` header. Returns `authCode`.
3. **POST session** → `https://apiv2.ecloudeu.com/auth/account/session/secure?identity_type=smart-israel` — exchanges `authCode` for vehicle API tokens (`accessToken`, `refreshToken`, `userId`, `clientId`).

**Alternatives considered**:
- Unified single flow for both regions: Not possible; the endpoints, signing secrets, and app identifiers are fundamentally different between EU and INTL.

## R3: HMAC-SHA1 Request Signing

**Decision**: Implement region-aware HMAC-SHA1 signing for vehicle API requests.

**Rationale**: All vehicle data API calls require a signed `x-signature` header. Both EU and INTL use the same algorithm structure but different secrets.

**Algorithm**:
```
payload = "{content_type}\nx-api-signature-nonce:{nonce}\nx-api-signature-version:1.0\n\n{url_params}\n{body_md5}\n{timestamp}\n{method}\n{url_path}"
signature = base64(HMAC-SHA1(secret, payload.encode()))
```

Where:
- `content_type` = `application/json;responseformat=3`
- `body_md5` = `base64(MD5(body))` or `1B2M2Y8AsgTpgAmY7PhCfg==` (empty body)
- `url_path` = API path without base URL (e.g., `/remote-control/vehicle/status/{vin}`)

**Secrets**:
- EU: `base64_decode("NzRlNzQ2OWFmZjUwNDJiYmJlZDdiYmIxYjM2YzE1ZTk=")`
- INTL: `b"30fb4a7b7fab4e2e8b52120d0087efdd"` (raw ASCII)

**Alternatives considered**:
- Skipping signing: Not possible; the API rejects unsigned requests.
- Using a third-party signing library: Unnecessary — `hmac` and `hashlib` are Python stdlib.

## R4: Token Lifecycle & Re-authentication

**Decision**: Perform full re-login on token expiry rather than attempting token refresh.

**Rationale**: The pySmartHashtag reference library stores refresh tokens but never uses them — both EU and INTL paths perform full re-login when tokens expire. The refresh token flow is undocumented and may not be reliable. Full re-login is simpler and proven reliable.

**Token expiry detection**:
- HTTP 401 response
- API response `code: 1402` (SmartTokenRefreshNecessary)
- `expires_at` timestamp exceeded (checked proactively before requests)

**HA integration pattern**:
- On token expiry during `DataUpdateCoordinator._async_update_data()`, catch the auth error, re-login, and retry.
- On persistent auth failure (invalid credentials), raise `ConfigEntryAuthFailed` to trigger HA's re-auth flow.

**Alternatives considered**:
- Implementing refresh token flow: Rejected due to undocumented behavior and unreliable results in the reference library.

## R5: aiohttp Migration from httpx

**Decision**: Rewrite all HTTP calls using `aiohttp.ClientSession` via `async_get_clientsession(hass)` instead of the reference library's `httpx`.

**Rationale**: Constitution Principle I (HA Compatibility) mandates using HA's bundled HTTP client. The reference library uses `httpx.AsyncClient` extensively, including an `httpx.Auth` subclass for automatic token injection. This must be replaced with manual header management on `aiohttp` requests.

**Key differences**:
- No `httpx.Auth` equivalent in aiohttp — must manually attach `Authorization: Bearer {token}` headers.
- No built-in redirect-following with header extraction — must handle 302 responses manually in the EU auth flow.
- SSL context: Use HA's session (already configured with proper SSL/TLS) instead of creating custom SSL contexts with `certifi`.

**Alternatives considered**:
- Adding `httpx` as a dependency: Rejected by Constitution Principle I (no dependencies outside HA runtime).

## R6: Vehicle Data Endpoints

**Decision**: Use the documented ecloudeu.com REST endpoints for vehicle data, SOC, and OTA information.

**Endpoints**:

| Purpose | Method | URL | Key Params |
|---------|--------|-----|------------|
| Vehicle list | GET | `{base}/device-platform/user/vehicle/secure` | `needSharedCar=1`, `userId={id}` |
| Vehicle status | GET | `{base}/remote-control/vehicle/status/{vin}` | `latest={bool}`, `target=basic,more`, `userId={id}` |
| SOC / Charging | GET | `{base}/remote-control/vehicle/status/soc/{vin}` | `setting=charging` |
| OTA info | GET | `https://ota.srv.smart.com/app/info/{vin}` | (different host, simpler headers) |
| Select vehicle | POST | `{base}/device-platform/user/session/update` | (body: `vehicleIdentity.vin`) |

**Note**: Vehicle selection (POST session/update) must be called before fetching status for each vehicle when iterating multiple vehicles.

**Status response fields mapped to HA entities**:
- `electricVehicleStatus.chargeLevel` → battery level sensor (%)
- `electricVehicleStatus.distanceToEmptyOnBatteryOnly` → range sensor (km)
- `electricVehicleStatus.chargerState` → charging status sensor (enum 0-15)
- `electricVehicleStatus.statusOfChargerConnection` → charging connected binary sensor
- `doorsStatus.*` → door binary sensors (per-door)
- `windowStatus.*` → window binary sensors (per-window)
- `climateStatus.*` → climate sensors
- GPS coordinates from vehicle status → device_tracker

## R7: HA Integration Patterns

**Decision**: Follow standard HA custom integration patterns using `DataUpdateCoordinator`, config flow, and entity platforms.

**Key patterns**:
- `config_flow.py`: Two-step flow — (1) credentials + region, (2) validate by attempting login. Options flow for scan interval.
- `coordinator.py`: Subclass `DataUpdateCoordinator[dict[str, VehicleData]]`. The `_async_update_data` method authenticates (if needed), iterates vehicles, fetches status for each, and returns a dict keyed by VIN.
- Entity platforms (`sensor.py`, `binary_sensor.py`, `device_tracker.py`): Each defines entity descriptions and creates entities per vehicle from coordinator data.
- Device registry: Each vehicle registered with VIN as identifier, manufacturer "Smart", model from API data.
- Diagnostics: `async_get_config_entry_diagnostics()` returns coordinator data with `async_redact_data()` applied.

**Alternatives considered**:
- Separate coordinators per vehicle: Rejected as unnecessary complexity. A single coordinator iterating vehicles is simpler and avoids multiple concurrent auth sessions.
- Push-based updates (webhooks): Out of scope per spec. The Smart API doesn't offer webhooks for consumer integrations.
