"""Config flow for the Hello Smart integration."""

from __future__ import annotations

import logging
from typing import Any

import voluptuous as vol

from homeassistant.config_entries import (
    ConfigEntry,
    ConfigFlow,
    ConfigFlowResult,
    OptionsFlow,
)
from homeassistant.const import CONF_EMAIL, CONF_PASSWORD, CONF_REGION
from homeassistant.helpers.aiohttp_client import async_get_clientsession

from .auth import AuthenticationError, async_login_eu, async_login_intl
from .const import DEFAULT_SCAN_INTERVAL, DOMAIN, MIN_SCAN_INTERVAL
from .models import Region

_LOGGER = logging.getLogger(__name__)

CONF_SCAN_INTERVAL = "scan_interval"

USER_SCHEMA = vol.Schema(
    {
        vol.Required(CONF_EMAIL): str,
        vol.Required(CONF_PASSWORD): str,
        vol.Required(CONF_REGION, default=Region.INTL): vol.In(
            {Region.EU: "EU", Region.INTL: "INTL"}
        ),
    }
)


class SmartConfigFlow(ConfigFlow, domain=DOMAIN):
    """Handle a config flow for Hello Smart."""

    VERSION = 1

    async def async_step_user(
        self, user_input: dict[str, Any] | None = None
    ) -> ConfigFlowResult:
        """Handle the initial user step — credentials and region."""
        errors: dict[str, str] = {}

        if user_input is not None:
            email = user_input[CONF_EMAIL]
            password = user_input[CONF_PASSWORD]
            region = user_input[CONF_REGION]

            # Detect duplicate accounts (FR-020)
            unique_id = f"{email}_{region}"
            await self.async_set_unique_id(unique_id)
            self._abort_if_unique_id_configured()

            session = async_get_clientsession(self.hass)

            try:
                if region == Region.INTL:
                    account = await async_login_intl(session, email, password)
                else:
                    account = await async_login_eu(session, email, password)
            except AuthenticationError:
                errors["base"] = "invalid_auth"
            except Exception:
                _LOGGER.exception("Unexpected error during authentication")
                errors["base"] = "cannot_connect"
            else:
                return self.async_create_entry(
                    title=email,
                    data={
                        CONF_EMAIL: email,
                        CONF_PASSWORD: password,
                        CONF_REGION: region,
                        "api_access_token": account.api_access_token,
                        "api_refresh_token": account.api_refresh_token,
                        "api_user_id": account.api_user_id,
                        "api_client_id": account.api_client_id,
                        "device_id": account.device_id,
                    },
                    options={
                        CONF_SCAN_INTERVAL: DEFAULT_SCAN_INTERVAL,
                    },
                )

        return self.async_show_form(
            step_id="user",
            data_schema=USER_SCHEMA,
            errors=errors,
        )

    @staticmethod
    def async_get_options_flow(
        config_entry: ConfigEntry,
    ) -> SmartOptionsFlowHandler:
        """Return the options flow handler."""
        return SmartOptionsFlowHandler(config_entry)


class SmartOptionsFlowHandler(OptionsFlow):
    """Handle options flow for Hello Smart."""

    def __init__(self, config_entry: ConfigEntry) -> None:
        self._config_entry = config_entry

    async def async_step_init(
        self, user_input: dict[str, Any] | None = None
    ) -> ConfigFlowResult:
        """Manage the scan interval option."""
        if user_input is not None:
            return self.async_create_entry(data=user_input)

        current_interval = self._config_entry.options.get(
            CONF_SCAN_INTERVAL, DEFAULT_SCAN_INTERVAL
        )

        return self.async_show_form(
            step_id="init",
            data_schema=vol.Schema(
                {
                    vol.Required(
                        CONF_SCAN_INTERVAL,
                        default=current_interval,
                    ): vol.All(vol.Coerce(int), vol.Range(min=MIN_SCAN_INTERVAL)),
                }
            ),
        )
