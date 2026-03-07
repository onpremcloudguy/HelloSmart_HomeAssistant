"""Constants for the Hello Smart integration."""

from __future__ import annotations

import base64

DOMAIN = "hello_smart"

# --- Default configuration ---
DEFAULT_SCAN_INTERVAL = 300  # seconds (5 minutes)
MIN_SCAN_INTERVAL = 60  # seconds

# --- API Base URLs ---
EU_API_BASE_URL = "https://api.ecloudeu.com"
INTL_API_BASE_URL = "https://apiv2.ecloudeu.com"
# INTL uses EU_API_BASE_URL for vehicle data. INTL_API_BASE_URL only for session exchange.
INTL_AUTH_BASE_URL = "https://sg-app-api.smart.com"
EU_AUTH_BASE_URL = "https://auth.smart.com"
EU_CONTEXT_URL = "https://awsapi.future.smart.com"
OTA_BASE_URL = "https://ota.srv.smart.com"

# --- URL Allowlist (FR-015) ---
URL_ALLOWLIST: frozenset[str] = frozenset(
    {
        "api.ecloudeu.com",
        "apiv2.ecloudeu.com",
        "sg-app-api.smart.com",
        "auth.smart.com",
        "awsapi.future.smart.com",
        "ota.srv.smart.com",
    }
)

# --- App identifiers ---
EU_APP_ID = "SmartAPPEU"
INTL_APP_ID = "SmartAPPGlobal"
INTL_VEHICLE_APP_ID = "SMARTAPP-ISRAEL"

EU_OPERATOR_CODE = "SMART"
INTL_OPERATOR_CODE = "SMART-ISRAEL"

# --- Auth keys ---
GIGYA_API_KEY = (
    "3_L94eyQ-wvJhWm7Afp1oBhfTGXZArUfSHHW9p9Pncg513hZELXsxCfMWHrF8f5P5a"
)
INTL_X_CA_KEY = "204587190"

# --- HMAC signing secrets (public app identifiers, not user secrets) ---
EU_SIGNING_SECRET: bytes = base64.b64decode(
    "NzRlNzQ2OWFmZjUwNDJiYmJlZDdiYmIxYjM2YzE1ZTk="
)
INTL_SIGNING_SECRET: bytes = b"30fb4a7b7fab4e2e8b52120d0087efdd"

# --- Identity types ---
EU_IDENTITY_TYPE = "smart"
INTL_IDENTITY_TYPE = "smart-israel"

# --- Device ID lengths ---
EU_DEVICE_ID_LENGTH = 16
INTL_DEVICE_ID_LENGTH = 32

# --- Accept header used in signing ---
ACCEPT_HEADER = "application/json;responseformat=3"

# --- Empty body MD5 (pre-computed) ---
EMPTY_BODY_MD5 = "1B2M2Y8AsgTpgAmY7PhCfg=="

# --- Sensitive fields for log/diagnostics redaction (FR-014, FR-022) ---
SENSITIVE_FIELDS: tuple[str, ...] = (
    "access_token",
    "accessToken",
    "refresh_token",
    "refreshToken",
    "api_access_token",
    "api_refresh_token",
    "password",
    "userId",
    "api_user_id",
    "vin",
    "loginID",
    "login_token",
    "idToken",
    "authCode",
    "api_client_id",
    "clientId",
)

# --- API URL paths ---
API_SESSION_PATH = "/auth/account/session/secure"
API_CARS_PATH = "/device-platform/user/vehicle/secure"
API_SELECT_CAR_PATH = "/device-platform/user/session/update"

# --- API response codes ---
API_CODE_SUCCESS = 1000
API_CODE_TOKEN_EXPIRED = 1402
API_CODE_VEHICLE_NOT_LINKED = 8006
