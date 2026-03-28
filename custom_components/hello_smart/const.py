"""Constants for the Hello Smart integration."""

from __future__ import annotations

import base64

DOMAIN = "hello_smart"

# --- Default configuration ---
DEFAULT_SCAN_INTERVAL = 60  # seconds
MIN_SCAN_INTERVAL = 60  # seconds

# --- API Base URLs ---
EU_API_BASE_URL = "https://api.ecloudeu.com"
INTL_API_BASE_URL = "https://apiv2.ecloudeu.com"
# INTL uses EU_API_BASE_URL for vehicle data. INTL_API_BASE_URL only for session exchange.
INTL_AUTH_BASE_URL = "https://sg-app-api.smart.com"
EU_AUTH_BASE_URL = "https://auth.smart.com"
EU_CONTEXT_URL = "https://awsapi.future.smart.com"
OTA_BASE_URL = "https://ota.srv.smart.com"

# --- Vehicle Services (VC) Base URLs (for ability/image endpoints) ---
VC_INTL_BASE_URL = "https://sg-app-api.smart.com/vc"
VC_EU_BASE_URL = "https://vehicle.vbs.srv.smart.com"

# --- URL Allowlist (FR-015) ---
URL_ALLOWLIST: frozenset[str] = frozenset(
    {
        "api.ecloudeu.com",
        "apiv2.ecloudeu.com",
        "sg-app-api.smart.com",
        "sg-app.smart.com",
        "auth.smart.com",
        "awsapi.future.smart.com",
        "ota.srv.smart.com",
        "vehicle.vbs.srv.smart.com",
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
INTL_VC_APP_SECRET = "vxnzkHbpQrkKKQKmFBZlOnL780rjXLFT"

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
    "imei",
    "locker_secret",
    "secretSet",
    "plate_no",
    "engine_no",
    "iccid",
    "msisdn",
    "ihu_id",
    "tem_id",
)

# --- Command service IDs ---
SERVICE_ID_DOOR_LOCK = "RDL_2"
SERVICE_ID_DOOR_UNLOCK = "RDU_2"
SERVICE_ID_CLIMATE = "RCE_2"
SERVICE_ID_CHARGING = "rcs"
SERVICE_ID_HORN_LIGHT = "RHL"
SERVICE_ID_WINDOW_SET = "RWS_2"
SERVICE_ID_FRIDGE = "UFR"
SERVICE_ID_SEAT_HEAT = "RSH"
SERVICE_ID_SEAT_VENT = "RSV"

# --- Command settings ---
COMMAND_COOLDOWN_SECONDS = 5

# --- Capability function IDs (from APK FunctionId.java) ---
FUNCTION_ID_REMOTE_LOCK = "remote_control_lock"
FUNCTION_ID_REMOTE_UNLOCK = "remote_control_unlock"
FUNCTION_ID_CLIMATE = "remote_air_condition_switch"
FUNCTION_ID_WINDOW_CLOSE = "remote_window_close"
FUNCTION_ID_WINDOW_OPEN = "remote_window_open"
FUNCTION_ID_TRUNK_OPEN = "remote_trunk_open"
FUNCTION_ID_HONK_FLASH = "honk_flash"
FUNCTION_ID_SEAT_HEAT = "remote_seat_preheat_switch"
FUNCTION_ID_SEAT_VENT = "seat_ventilation_status"
FUNCTION_ID_FRAGRANCE = "remote_control_fragrance"
FUNCTION_ID_CHARGING = "charging_status"
FUNCTION_ID_DOOR_STATUS = "door_lock_switch_status"
FUNCTION_ID_TRUNK_STATUS = "trunk_status"
FUNCTION_ID_WINDOW_STATUS = "windows_rolling_status"
FUNCTION_ID_SKYLIGHT_STATUS = "skylight_rolling_status"
FUNCTION_ID_TYRE_PRESSURE = "tyre_pressure"
FUNCTION_ID_VEHICLE_POSITION = "vehicle_position"
FUNCTION_ID_TOTAL_MILEAGE = "total_mileage"
FUNCTION_ID_HOOD_STATUS = "engine_compartment_cover_status"
FUNCTION_ID_CHARGE_PORT_STATUS = "recharge_lid_status"
FUNCTION_ID_CURTAIN_STATUS = "curtain_status"
FUNCTION_ID_DOORS_STATUS = "vehiecle_doors_status"
FUNCTION_ID_CLIMATE_STATUS = "climate_status"
FUNCTION_ID_CHARGING_RESERVATION = "remote_appointment_charging"

# --- API URL paths ---
API_SESSION_PATH = "/auth/account/session/secure"
API_CARS_PATH = "/device-platform/user/vehicle/secure"
API_SELECT_CAR_PATH = "/device-platform/user/session/update"
API_TELEMATICS_COMMAND_PATH = "/remote-control/vehicle/telematics"
API_CHARGING_RESERVATION_PATH = "/remote-control/charging/reservation"
API_CLIMATE_SCHEDULE_PATH = "/remote-control/schedule"
API_VC_ABILITY_PATH = "/vehicle/v1/ability"

# --- API response codes ---
API_CODE_SUCCESS = 1000
API_CODE_TOKEN_EXPIRED = 1402
API_CODE_VEHICLE_NOT_LINKED = 8006
