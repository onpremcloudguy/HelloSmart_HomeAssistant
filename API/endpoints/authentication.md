# Authentication

Authentication flows for EU and INTL regions.

[← Back to API Reference](../README.md) · [Common Patterns](../common-patterns.md)

---

## EU Login (Gigya)

Multi-step OAuth flow via Gigya identity provider.

### Flow Overview

```
┌─────────────┐     ┌──────────────────┐     ┌───────────────────────┐     ┌────────────────────┐
│  Step 1      │     │  Step 2           │     │  Step 3                │     │  Step 4             │
│  Login       │ ──► │  Get JWT          │ ──► │  Exchange Token        │ ──► │  Session Exchange   │
│  auth.smart  │     │  auth.smart       │     │  awsapi.future.smart   │     │  api.ecloudeu       │
└─────────────┘     └──────────────────┘     └───────────────────────┘     └────────────────────┘
```

### Step 1 — Gigya Login

```http
POST https://auth.smart.com/accounts.login
Content-Type: application/x-www-form-urlencoded
```

**Request (form-encoded):**

| Parameter | Value |
|-----------|-------|
| `loginID` | User email |
| `password` | User password |
| `apiKey` | Gigya API key |
| `targetEnv` | `jssdk` |
| `include` | `profile,data,emails` |
| `includeUserInfo` | `true` |

**Response:**
```json
{
  "UID": "abc123...",
  "UIDSignature": "...",
  "signatureTimestamp": "1706028240"
}
```

### Step 2 — Get JWT

```http
POST https://auth.smart.com/accounts.getJWT
Content-Type: application/x-www-form-urlencoded
```

**Request (form-encoded):**

| Parameter | Value |
|-----------|-------|
| `UID` | From step 1 |
| `UIDSignature` | From step 1 |
| `signatureTimestamp` | From step 1 |
| `apiKey` | Gigya API key |

**Response:**
```json
{
  "id_token": "eyJ..."
}
```

### Step 3 — Token Exchange

```http
POST https://awsapi.future.smart.com/.../oauth/token
Content-Type: application/json
```

**Request:**
```json
{
  "grant_type": "authorization_code",
  "code": "{id_token from step 2}"
}
```

**Response:**
```json
{
  "access_token": "...",
  "refresh_token": "..."
}
```

### Step 4 — Session Exchange

```http
POST https://api.ecloudeu.com/auth/account/session/secure?identity_type=smart
Content-Type: application/json
```

**Request:**
```json
{
  "accessToken": "{access_token from step 3}"
}
```

**Response:**
```json
{
  "code": 1000,
  "data": {
    "accessToken": "api_access_token_here",
    "refreshToken": "api_refresh_token_here",
    "userId": "12345"
  }
}
```

**Result:** `api_access_token`, `api_refresh_token`, and `userId` are stored in the `Account` model for all subsequent requests.

---

## INTL Login (3-Step)

Simplified direct login flow for international regions (Israel, APAC, etc.).

### Flow Overview

```
┌─────────────────────┐     ┌─────────────────────┐     ┌─────────────────────┐
│  Step 1              │     │  Step 2              │     │  Step 3              │
│  Login               │ ──► │  Authorize           │ ──► │  Session Exchange    │
│  sg-app-api.smart    │     │  sg-app-api.smart    │     │  apiv2.ecloudeu      │
└─────────────────────┘     └─────────────────────┘     └─────────────────────┘
```

### Step 1 — Login

```http
POST https://sg-app-api.smart.com/iam/service/api/v1/login
Content-Type: application/json
X-Ca-Key: 204587190
X-App-Id: SmartAPPGlobal
```

**Request:**
```json
{
  "email": "user@example.com",
  "password": "password123"
}
```

**Response:**
```json
{
  "code": 200,
  "data": {
    "userId": "12345",
    "loginToken": "token_here",
    "clientId": "client_id_here"
  }
}
```

### Step 2 — Authorize

```http
POST https://sg-app-api.smart.com/iam/service/api/v1/oauth/authorize
Content-Type: application/json
X-Ca-Key: 204587190
X-App-Id: SmartAPPGlobal
```

**Request:**
```json
{
  "loginToken": "{loginToken from step 1}",
  "clientId": "{clientId from step 1}"
}
```

**Response:**
```json
{
  "code": 200,
  "data": {
    "authCode": "auth_code_here"
  }
}
```

### Step 3 — Session Exchange

```http
POST https://apiv2.ecloudeu.com/auth/account/session/secure?identity_type=smart-israel
Content-Type: application/json
x-app-id: SMARTAPP-ISRAEL
x-operator-code: SMART-ISRAEL
x-signature: {hmac_signature}
```

> **Note:** This request uses signed headers (see [Common Patterns](../common-patterns.md#authentication--signing)) but does **not** include an `authorization` header (no token yet).

**Request:**
```json
{
  "authCode": "{authCode from step 2}",
  "userId": "{userId from step 1}",
  "deviceId": "{device_id}"
}
```

**Response:**
```json
{
  "code": 1000,
  "data": {
    "accessToken": "api_access_token_here",
    "refreshToken": "api_refresh_token_here",
    "userId": "12345"
  }
}
```

**Result:** `api_access_token`, `api_refresh_token`, and `userId` are stored in the `Account` model.

---

## Related

- [Common Patterns — Signing](../common-patterns.md#authentication--signing)
- Source: [`auth.py`](../../custom_components/hello_smart/auth.py)
