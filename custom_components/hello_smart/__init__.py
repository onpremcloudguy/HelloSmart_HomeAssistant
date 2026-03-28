"""The Hello Smart integration."""

from __future__ import annotations

import logging
from pathlib import Path

from homeassistant.components.frontend import add_extra_js_url
from homeassistant.components.http import StaticPathConfig
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import Platform
from homeassistant.core import HomeAssistant

from .const import DOMAIN
from .coordinator import SmartDataCoordinator

_LOGGER = logging.getLogger(__name__)

PLATFORMS: list[Platform] = [
    Platform.SENSOR,
    Platform.BINARY_SENSOR,
    Platform.DEVICE_TRACKER,
    Platform.LOCK,
    Platform.CLIMATE,
    Platform.SWITCH,
    Platform.BUTTON,
    Platform.NUMBER,
    Platform.SELECT,
    Platform.TIME,
]

type SmartConfigEntry = ConfigEntry[SmartDataCoordinator]


FRONTEND_URL = f"/{DOMAIN}/frontend"
FRONTEND_CARD_JS = "hello-smart-vehicle-card.js"
FRONTEND_CHARGE_JS = "hello-smart-charge-card.js"
FRONTEND_RESOURCE_URL = f"{FRONTEND_URL}/{FRONTEND_CARD_JS}"
FRONTEND_CHARGE_URL = f"{FRONTEND_URL}/{FRONTEND_CHARGE_JS}"

# Version from manifest.json for cache-busting
_FRONTEND_VERSION = "0.4.5"


async def async_setup_entry(hass: HomeAssistant, entry: SmartConfigEntry) -> bool:
    """Set up Hello Smart from a config entry."""
    coordinator = SmartDataCoordinator(hass, entry)

    await coordinator.async_config_entry_first_refresh()

    hass.data.setdefault(DOMAIN, {})
    hass.data[DOMAIN][entry.entry_id] = coordinator

    # Register the custom frontend card (once, shared across entries)
    await _async_register_frontend(hass)

    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)

    entry.async_on_unload(entry.add_update_listener(_async_options_updated))

    return True


async def _async_register_frontend(hass: HomeAssistant) -> None:
    """Register the custom Lovelace card JS as a static resource."""
    if f"{DOMAIN}_frontend_registered" in hass.data:
        return

    frontend_dir = Path(__file__).parent / "frontend"
    await hass.http.async_register_static_paths(
        [StaticPathConfig(FRONTEND_URL, str(frontend_dir), cache_headers=False)]
    )
    add_extra_js_url(hass, f"{FRONTEND_RESOURCE_URL}?v={_FRONTEND_VERSION}")
    add_extra_js_url(hass, f"{FRONTEND_CHARGE_URL}?v={_FRONTEND_VERSION}")

    hass.data[f"{DOMAIN}_frontend_registered"] = True


async def _async_options_updated(
    hass: HomeAssistant, entry: SmartConfigEntry
) -> None:
    """Reload the integration when options change."""
    await hass.config_entries.async_reload(entry.entry_id)


async def async_unload_entry(hass: HomeAssistant, entry: SmartConfigEntry) -> bool:
    """Unload a Hello Smart config entry."""
    unload_ok = await hass.config_entries.async_unload_platforms(entry, PLATFORMS)

    if unload_ok:
        hass.data[DOMAIN].pop(entry.entry_id, None)
        if not hass.data[DOMAIN]:
            hass.data.pop(DOMAIN, None)

    return unload_ok
