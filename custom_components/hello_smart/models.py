"""Data models for the Hello Smart integration."""

from __future__ import annotations

import enum
from dataclasses import dataclass, field
from datetime import datetime


class Region(enum.StrEnum):
    """Smart API regions."""

    EU = "EU"
    INTL = "INTL"


class AuthState(enum.StrEnum):
    """Account authentication state."""

    UNAUTHENTICATED = "unauthenticated"
    AUTHENTICATED = "authenticated"
    TOKEN_EXPIRED = "token_expired"
    AUTH_FAILED = "auth_failed"


class ChargingState(enum.StrEnum):
    """Human-readable charging states mapped from API chargerState 0–15."""

    NOT_CHARGING = "not_charging"
    CHARGE_PREPARATION = "charge_preparation"
    AC_CHARGING = "ac_charging"
    DC_CHARGING = "dc_charging"
    CHARGE_PAUSED = "charge_paused"
    FULLY_CHARGED = "fully_charged"


def charging_state_from_api(value: int) -> ChargingState:
    """Map API chargerState integer (0–15) to ChargingState enum."""
    if value == 0:
        return ChargingState.NOT_CHARGING
    if 1 <= value <= 3:
        return ChargingState.CHARGE_PREPARATION
    if 4 <= value <= 6:
        return ChargingState.AC_CHARGING
    if 7 <= value <= 9:
        return ChargingState.DC_CHARGING
    if 10 <= value <= 14:
        return ChargingState.CHARGE_PAUSED
    if value == 15:
        return ChargingState.FULLY_CHARGED
    return ChargingState.NOT_CHARGING


@dataclass
class Account:
    """A user's Smart cloud account and authentication state."""

    username: str
    region: Region
    device_id: str = ""
    access_token: str = ""
    refresh_token: str = ""
    api_access_token: str = ""
    api_refresh_token: str = ""
    api_user_id: str = ""
    api_client_id: str = ""  # INTL only
    expires_at: datetime | None = None
    state: AuthState = AuthState.UNAUTHENTICATED

    @property
    def is_token_valid(self) -> bool:
        """Check if the API token is present and not expired."""
        if not self.api_access_token or self.state != AuthState.AUTHENTICATED:
            return False
        if self.expires_at is None:
            return True
        return datetime.now() < self.expires_at


@dataclass
class Vehicle:
    """A single Smart vehicle linked to an account."""

    vin: str
    model_name: str = ""
    model_year: str = ""
    series_code: str = ""
    base_url: str = ""


@dataclass
class VehicleStatus:
    """Point-in-time snapshot of a vehicle's state."""

    battery_level: int = 0
    range_remaining: float = 0.0
    charging_state: ChargingState = ChargingState.NOT_CHARGING
    charger_connected: bool = False
    charge_voltage: float | None = None
    charge_current: float | None = None
    time_to_full: int | None = None
    doors: dict[str, bool] = field(default_factory=dict)
    windows: dict[str, bool] = field(default_factory=dict)
    climate_active: bool = False
    latitude: float | None = None
    longitude: float | None = None
    last_updated: datetime | None = None


@dataclass
class OTAInfo:
    """Firmware update state for a vehicle."""

    current_version: str = ""
    target_version: str = ""

    @property
    def update_available(self) -> bool:
        """True if target version differs from current version."""
        return bool(
            self.target_version
            and self.current_version
            and self.target_version != self.current_version
        )


@dataclass
class VehicleData:
    """Combined vehicle data returned by the coordinator."""

    vehicle: Vehicle
    status: VehicleStatus = field(default_factory=VehicleStatus)
    ota: OTAInfo = field(default_factory=OTAInfo)
