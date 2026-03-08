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

from .api import SmartAPI, TokenExpiredError
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
        except Exception as err:
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
                model_id=vehicle.series_code or None,
                hw_version=vehicle.model_year or None,
                serial_number=vin,
                suggested_area="Garage",
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
                except Exception:
                    _LOGGER.debug("SOC detail unavailable for %s", vin[:6] + "...", exc_info=True)

                # Fetch OTA info
                ota = None
                try:
                    ota = await self._api.async_get_ota_info(account, vin)
                except Exception:
                    _LOGGER.debug("OTA info unavailable for %s", vin[:6] + "...", exc_info=True)

                # Fetch vehicle running state
                running_state = None
                try:
                    running_state = await self._api.async_get_vehicle_state(account, vin)
                except Exception:
                    _LOGGER.debug("Vehicle state unavailable for %s", vin[:6] + "...", exc_info=True)

                # Fetch telematics
                telematics = None
                try:
                    telematics = await self._api.async_get_telematics(account, vin)
                except Exception:
                    _LOGGER.debug("Telematics unavailable for %s", vin[:6] + "...", exc_info=True)

                # Fetch diagnostic history
                diagnostic = None
                try:
                    diagnostic = await self._api.async_get_diagnostic_history(account, vin)
                except Exception:
                    _LOGGER.debug("Diagnostics unavailable for %s", vin[:6] + "...", exc_info=True)

                # Fetch charging reservation
                charging_reservation = None
                try:
                    charging_reservation = await self._api.async_get_charging_reservation(account, vin)
                except Exception:
                    _LOGGER.debug("Charging reservation unavailable for %s", vin[:6] + "...", exc_info=True)

                # Fetch climate schedule
                climate_schedule = None
                try:
                    climate_schedule = await self._api.async_get_climate_schedule(account, vin)
                except Exception:
                    _LOGGER.debug("Climate schedule unavailable for %s", vin[:6] + "...", exc_info=True)

                # Fetch fridge status
                fridge = None
                try:
                    fridge = await self._api.async_get_fridge_status(account, vin)
                except Exception:
                    _LOGGER.debug("Fridge status unavailable for %s", vin[:6] + "...", exc_info=True)

                # Fetch locker status
                locker = None
                try:
                    locker = await self._api.async_get_locker_status(account, vin)
                except Exception:
                    _LOGGER.debug("Locker status unavailable for %s", vin[:6] + "...", exc_info=True)

                # Fetch VTM settings (no VIN param — uses session)
                vtm = None
                try:
                    vtm = await self._api.async_get_vtm_settings(account)
                except Exception:
                    _LOGGER.debug("VTM settings unavailable for %s", vin[:6] + "...", exc_info=True)

                # Fetch fragrance details
                fragrance = None
                try:
                    fragrance = await self._api.async_get_fragrance(account, vin)
                except Exception:
                    _LOGGER.debug("Fragrance unavailable for %s", vin[:6] + "...", exc_info=True)

                # Fetch trip journal
                last_trip = None
                try:
                    last_trip = await self._api.async_get_trip_journal(account, vin)
                except Exception:
                    _LOGGER.debug("Trip journal unavailable for %s", vin[:6] + "...", exc_info=True)

                # Fetch total distance
                total_distance = None
                try:
                    total_distance = await self._api.async_get_total_distance(account, vin)
                except Exception:
                    _LOGGER.debug("Total distance unavailable for %s", vin[:6] + "...", exc_info=True)

                # Fetch geofences
                geofence = None
                try:
                    geofence = await self._api.async_get_geofences(account, vin)
                except Exception:
                    _LOGGER.debug("Geofences unavailable for %s", vin[:6] + "...", exc_info=True)

                # Fetch capabilities
                capabilities = None
                try:
                    capabilities = await self._api.async_get_capabilities(account, vin)
                except Exception:
                    _LOGGER.debug("Capabilities unavailable for %s", vin[:6] + "...", exc_info=True)

                # Fetch energy ranking
                energy_ranking = None
                try:
                    energy_ranking = await self._api.async_get_energy_ranking(account, vin)
                except Exception:
                    _LOGGER.debug("Energy ranking unavailable for %s", vin[:6] + "...", exc_info=True)

                # Fetch locker secret status
                locker_secret = None
                try:
                    locker_secret = await self._api.async_get_locker_secret(account, vin)
                except Exception:
                    _LOGGER.debug("Locker secret unavailable for %s", vin[:6] + "...", exc_info=True)

                # Fetch FOTA notification
                fota_notification = None
                try:
                    fota_notification = await self._api.async_get_fota_notification(account)
                except Exception:
                    _LOGGER.debug("FOTA notification unavailable for %s", vin[:6] + "...", exc_info=True)

                # Fetch plant number for DeviceInfo
                plant_no = None
                try:
                    plant_no = await self._api.async_get_plant_no(account, vin)
                except Exception:
                    _LOGGER.debug("Plant number unavailable for %s", vin[:6] + "...", exc_info=True)

            except Exception as err:
                _LOGGER.warning(
                    "Failed to fetch status for vehicle %s: %s",
                    vin[:6] + "...",
                    err,
                )
                result[vin] = VehicleData(vehicle=vehicle)
                continue

            # Update DeviceInfo with sw_version from OTA and configuration_url
            if ota and ota.current_version:
                self._device_infos[vin] = DeviceInfo(
                    identifiers={(DOMAIN, vin)},
                    manufacturer="Smart",
                    model=vehicle.model_name or "Smart Vehicle",
                    name=vehicle.model_name or f"Smart {vin[-6:]}",
                    model_id=vehicle.series_code or None,
                    hw_version=vehicle.model_year or None,
                    sw_version=ota.current_version,
                    serial_number=vin,
                    suggested_area="Garage",
                )

            result[vin] = VehicleData(
                vehicle=vehicle,
                status=status,
                ota=ota or OTAInfo(),
                running_state=running_state,
                telematics=telematics,
                diagnostic=diagnostic,
                charging_reservation=charging_reservation,
                climate_schedule=climate_schedule,
                fridge=fridge,
                locker=locker,
                vtm=vtm,
                fragrance=fragrance,
                last_trip=last_trip,
                total_distance=total_distance,
                geofence=geofence,
                capabilities=capabilities,
                energy_ranking=energy_ranking,
                locker_secret=locker_secret,
                fota_notification=fota_notification,
            )

        _LOGGER.debug("Updated data for %d vehicle(s)", len(result))
        return result
