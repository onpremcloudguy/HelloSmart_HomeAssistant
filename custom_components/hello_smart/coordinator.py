"""DataUpdateCoordinator for the Hello Smart integration."""

from __future__ import annotations

import logging
from datetime import timedelta
from typing import Any

from homeassistant.config_entries import ConfigEntry
from homeassistant.const import CONF_EMAIL, CONF_PASSWORD, CONF_REGION
from homeassistant.core import HomeAssistant
from homeassistant.exceptions import ConfigEntryAuthFailed
from homeassistant.helpers.aiohttp_client import async_get_clientsession
from homeassistant.helpers.device_registry import DeviceInfo
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed

from .api import SmartAPI, SmartAPIError, TokenExpiredError
from .auth import AuthenticationError, async_login_eu, async_login_intl
from .const import DEFAULT_SCAN_INTERVAL, DOMAIN
from .models import Account, AuthState, OTAInfo, Region, VehicleData

_LOGGER = logging.getLogger(__name__)

CONF_SCAN_INTERVAL = "scan_interval"


class SmartDataCoordinator(DataUpdateCoordinator[dict[str, VehicleData]]):
    """Coordinator that polls Smart API for vehicle data."""

    def __init__(
        self,
        hass: HomeAssistant,
        entry: ConfigEntry,
    ) -> None:
        """Initialize the coordinator."""
        scan_interval = entry.options.get(CONF_SCAN_INTERVAL, DEFAULT_SCAN_INTERVAL)

        super().__init__(
            hass,
            _LOGGER,
            name=DOMAIN,
            update_interval=timedelta(seconds=scan_interval),
        )

        self.entry = entry
        self._session = async_get_clientsession(hass)
        self._api = SmartAPI(self._session)
        self._account: Account | None = None
        self._device_infos: dict[str, DeviceInfo] = {}

    @property
    def account(self) -> Account | None:
        """Return the current account."""
        return self._account

    def get_device_info(self, vin: str) -> DeviceInfo | None:
        """Return DeviceInfo for a specific vehicle."""
        return self._device_infos.get(vin)

    async def _async_authenticate(self) -> Account:
        """Authenticate or re-authenticate against the Smart API."""
        email = self.entry.data[CONF_EMAIL]
        password = self.entry.data[CONF_PASSWORD]
        region = Region(self.entry.data[CONF_REGION])

        try:
            if region == Region.INTL:
                account = await async_login_intl(self._session, email, password)
            else:
                account = await async_login_eu(self._session, email, password)
        except AuthenticationError as err:
            raise ConfigEntryAuthFailed(
                f"Authentication failed: {err}"
            ) from err

        # Preserve device_id from stored config if available
        stored_device_id = self.entry.data.get("device_id")
        if stored_device_id:
            account.device_id = stored_device_id

        self._account = account
        return account

    async def _async_update_data(self) -> dict[str, VehicleData]:
        """Fetch vehicle data from the Smart API."""
        # Authenticate if needed
        if self._account is None or not self._account.is_token_valid:
            try:
                await self._async_authenticate()
            except ConfigEntryAuthFailed:
                raise
            except Exception as err:
                raise UpdateFailed(f"Authentication failed: {err}") from err

        account = self._account
        assert account is not None

        try:
            return await self._async_fetch_all_vehicles(account)
        except TokenExpiredError:
            _LOGGER.debug("Token expired, re-authenticating")
            account.state = AuthState.TOKEN_EXPIRED
            try:
                await self._async_authenticate()
            except ConfigEntryAuthFailed:
                raise
            except Exception as err:
                raise UpdateFailed(f"Re-authentication failed: {err}") from err

            account = self._account
            assert account is not None
            return await self._async_fetch_all_vehicles(account)
        except SmartAPIError as err:
            raise UpdateFailed(f"API error: {err}") from err

    async def _async_fetch_all_vehicles(
        self, account: Account
    ) -> dict[str, VehicleData]:
        """Fetch status for all vehicles on the account."""
        vehicles = await self._api.async_get_vehicles(account)

        result: dict[str, VehicleData] = {}

        for vehicle in vehicles:
            vin = vehicle.vin
            if not vin:
                continue

            # Register device in HA
            self._device_infos[vin] = DeviceInfo(
                identifiers={(DOMAIN, vin)},
                manufacturer="Smart",
                model=vehicle.model_name or "Smart Vehicle",
                name=vehicle.model_name or f"Smart {vin[-6:]}",
            )

            try:
                await self._api.async_select_vehicle(account, vin)
                status = await self._api.async_get_vehicle_status(account, vin)

                # Fetch SOC / charging detail
                try:
                    soc_data = await self._api.async_get_soc(account, vin)
                    if soc_data:
                        if soc_data.get("chargeUAct"):
                            status.charge_voltage = float(soc_data["chargeUAct"])
                        if soc_data.get("chargeIAct"):
                            status.charge_current = float(soc_data["chargeIAct"])
                        if soc_data.get("timeToFullyCharged"):
                            status.time_to_full = int(soc_data["timeToFullyCharged"])
                except SmartAPIError:
                    _LOGGER.debug("SOC detail unavailable for %s", vin[:6] + "...")

                # Fetch OTA info
                ota = None
                try:
                    ota = await self._api.async_get_ota_info(account, vin)
                except SmartAPIError:
                    _LOGGER.debug("OTA info unavailable for %s", vin[:6] + "...")

            except SmartAPIError as err:
                _LOGGER.warning(
                    "Failed to fetch status for vehicle %s: %s",
                    vin[:6] + "...",
                    err,
                )
                result[vin] = VehicleData(vehicle=vehicle)
                continue

            result[vin] = VehicleData(
                vehicle=vehicle, status=status, ota=ota or OTAInfo()
            )

        _LOGGER.debug("Updated data for %d vehicle(s)", len(result))
        return result
