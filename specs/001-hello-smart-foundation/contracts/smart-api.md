# Smart Vehicle API Contract

**Branch**: `001-hello-smart-foundation` | **Date**: 2026-03-07

This document specifies the external Smart cloud API endpoints that the Hello Smart integration consumes. These are **third-party contracts** — the integration must conform to them.

---

## Authentication Endpoints

### EU: Get Authorization Context

```
GET https://awsapi.future.smart.com/login-app/api/v1/authorize?uiLocales=de-DE

Request Headers:
  x-app-id: SmartAPPEU
  x-requested-with: com.smart.hellosmart
  accept: text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8

Response: 302 Redirect
  Location: https://app.id.smart.com/login?context={context_token}
```

### EU: Gigya Login

```
POST https://auth.smart.com/accounts.login

Content-Type: application/x-www-form-urlencoded

Body:
  loginID={email}
  &password={password}
  &sessionExpiration=2592000
  &targetEnv=jssdk
  &include=profile%2Cdata%2Cemails%2Csubscriptions%2Cpreferences%2C
  &includeUserInfo=True
  &loginMode=standard
  &lang=de
  &APIKey=3_L94eyQ-wvJhWm7Afp1oBhfTGXZArUfSHHW9p9Pncg513hZELXsxCfMWHrF8f5P5a
  &source=showScreenSet
  &sdk=js_latest
  &sdkBuild=15482
  &format=json

Response: 200 JSON
  {
    "sessionInfo": {
      "login_token": "{login_token}",
      "expires_in": 3600
    }
  }

Error Response: 200 JSON (Gigya returns 200 even on failure)
  {
    "errorCode": 403042,
    "errorMessage": "Invalid LoginID"
  }
```

### EU: Authorization Continue

```
GET https://auth.smart.com/oidc/op/v1.0/{API_KEY}/authorize/continue
  ?context={context}
  &login_token={login_token}

Request Headers:
  cookie: {gigya_cookies}

Response: 302 Redirect
  Location: ...#access_token={access_token}&refresh_token={refresh_token}
```

### EU: Session Exchange

```
POST https://api.ecloudeu.com/auth/account/session/secure?identity_type=smart

Content-Type: application/json
Body: {"accessToken":"{access_token}"}

Headers: [Signed — see Signing section]

Response: 200 JSON
  {
    "code": 1000,
    "data": {
      "accessToken": "{api_access_token}",
      "refreshToken": "{api_refresh_token}",
      "userId": "{user_id}"
    }
  }
```

---

### INTL: Login

```
POST https://sg-app-api.smart.com/iam/service/api/v1/login

Content-Type: application/json
Body: {"email": "{email}", "password": "{password}"}

Headers:
  X-Ca-Key: 204587190
  X-Ca-Nonce: {uuid}
  X-Ca-Timestamp: {millis}
  X-App-Id: SmartAPPGlobal
  User-Agent: ALIYUN-ANDROID-DEMO

Response: 200 JSON
  {
    "code": "200",
    "result": {
      "accessToken": "{intl_access_token}",
      "refreshToken": "{intl_refresh_token}",
      "idToken": "{intl_id_token}",
      "userId": "{user_id}",
      "expiresIn": 86400
    }
  }
```

### INTL: OAuth Authorize

```
GET https://sg-app-api.smart.com/iam/service/api/v1/oauth20/authorize
  ?accessToken={intl_access_token}

Headers:
  X-Ca-Key: 204587190
  X-Ca-Nonce: {uuid}
  X-Ca-Timestamp: {millis}
  X-App-Id: SmartAPPGlobal
  Xs-Auth-Token: {intl_id_token}

Response: 200 JSON
  {
    "code": "200",
    "result": "{auth_code}"
  }
```

### INTL: Session Exchange

```
POST https://apiv2.ecloudeu.com/auth/account/session/secure?identity_type=smart-israel

Content-Type: application/json
Body: {"authCode":"{auth_code}"}

Headers: [Signed — see Signing section, INTL variant]

Response: 200 JSON
  {
    "code": 1000,
    "data": {
      "accessToken": "{api_access_token}",
      "refreshToken": "{api_refresh_token}",
      "userId": "{user_id}",
      "clientId": "{client_id}"
    }
  }
```

---

## Vehicle Data Endpoints

### Vehicle List

```
GET {base_url}/device-platform/user/vehicle/secure
  ?needSharedCar=1
  &userId={user_id}

Headers: [Signed]

Response: 200 JSON
  {
    "code": 1000,
    "data": {
      "list": [
        {
          "vin": "WME...",
          "seriesCodeVs": "HC1H2D3B6213-01_DE",
          "modelName": "Smart #1",
          ...
        }
      ]
    }
  }
```

### Vehicle Status

```
GET {base_url}/remote-control/vehicle/status/{vin}
  ?latest={true|false}
  &target=basic,more
  &userId={user_id}

Headers: [Signed]
Note: EU uses latest=True; INTL uses latest=False

Response: 200 JSON
  {
    "code": 1000,
    "data": {
      "vehicleStatus": {
        "updateTime": "{epoch_millis}",
        "additionalVehicleStatus": {
          "electricVehicleStatus": {
            "distanceToEmptyOnBatteryOnly": "{range_km}",
            "chargeLevel": "{soc_percent}",
            "statusOfChargerConnection": "{0|1}",
            "chargerState": "{0-15}"
          },
          "doorsStatus": { ... },
          "climateStatus": { ... },
          "windowStatus": { ... },
          "runningStatus": { ... },
          "lightStatus": { ... }
        }
      }
    }
  }
```

### SOC / Charging Detail

```
GET {base_url}/remote-control/vehicle/status/soc/{vin}
  ?setting=charging

Headers: [Signed]

Response: 200 JSON
  {
    "code": 1000,
    "data": {
      "chargeUAct": "{voltage}",
      "chargeIAct": "{current}",
      "chargeLevel": "{soc_percent}",
      "chargerState": "{0-15}",
      "timeToFullyCharged": "{minutes}"
    }
  }
```

### OTA Info

```
GET https://ota.srv.smart.com/app/info/{vin}

Headers:
  id-token: {device_id}
  access_token: {access_token}
  content-type: application/json

Response: 200 JSON
  {
    "targetVersion": "{version}",
    "currentVersion": "{version}"
  }
```

### Select Active Vehicle

```
POST {base_url}/device-platform/user/session/update

Content-Type: application/json
Body: {"vehicleIdentity": {"vin": "{vin}"}}

Headers: [Signed]

Response: 200 JSON (empty body on success)
```

---

## Request Signing

### Signature Header Format

All vehicle API calls require these headers in addition to standard HTTP headers:

```
x-app-id: {app_id}           # EU: "SmartAPPEU", INTL: "SMARTAPP-ISRAEL"
x-operator-code: {code}      # EU: "SMART", INTL: "SMART-ISRAEL"
x-device-identifier: {id}    # Random hex (EU: 16 chars, INTL: 32 chars)
x-api-signature-version: 1.0
x-api-signature-nonce: {nonce}  # Random hex
x-timestamp: {millis}
x-signature: {signature}
authorization: Bearer {api_access_token}
accept: application/json;responseformat=3
content-type: application/json; charset=utf-8
```

### Signature Computation

```
payload = "{accept}\nx-api-signature-nonce:{nonce}\nx-api-signature-version:1.0\n\n{params}\n{body_md5}\n{timestamp}\n{method}\n{path}"

signature = base64(HMAC-SHA1(secret, payload.encode("utf-8")))
```

Where:
- `{accept}` = `application/json;responseformat=3`
- `{params}` = URL query parameters as `key1=value1&key2=value2`
- `{body_md5}` = `base64(MD5(body))` or `1B2M2Y8AsgTpgAmY7PhCfg==` for empty body
- `{path}` = API path without base URL (e.g., `/remote-control/vehicle/status/{vin}`)

### Signing Secrets

- EU: `base64_decode("NzRlNzQ2OWFmZjUwNDJiYmJlZDdiYmIxYjM2YzE1ZTk=")`
- INTL: `b"30fb4a7b7fab4e2e8b52120d0087efdd"` (raw ASCII bytes)

---

## Error Responses

| HTTP Status | API Code | Meaning | Action |
|-------------|----------|---------|--------|
| 200 | 1000 | Success | Process data |
| 200 | 1402 | Token expired | Re-authenticate and retry |
| 200 | 8006 | Vehicle not linked | Mark vehicle unavailable |
| 401 | — | Unauthorized | Re-authenticate and retry |
| 429 | — | Rate limited | Wait `Retry-After` seconds and retry |
| 5xx | — | Server error | Mark entities unavailable, retry next interval |
