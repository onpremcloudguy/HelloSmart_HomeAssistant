"""The Hello Smart integration."""

from __future__ import annotations

import logging
from pathlib import Path

from homeassistant.components.frontend import add_extra_js_url
from homeassistant.components.http import StaticPathConfig
from homeassistant.components.lovelace import LOVELACE_DATA
from homeassistant.components.lovelace.resources import ResourceStorageCollection
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
_FRONTEND_VERSION = "0.5.0"


async def async_setup(hass: HomeAssistant, config: dict) -> bool:
    """Set up the Hello Smart integration (platform-level, before entries)."""
    # Register the static path early so the JS files are servable immediately.
    await _async_register_static_path(hass)
    return True


async def async_setup_entry(hass: HomeAssistant, entry: SmartConfigEntry) -> bool:
    """Set up Hello Smart from a config entry."""
    # Register as Lovelace resources (Lovelace is ready by entry setup time).
    await _async_register_lovelace_resources(hass)

    coordinator = SmartDataCoordinator(hass, entry)

    await coordinator.async_config_entry_first_refresh()

    hass.data.setdefault(DOMAIN, {})
    hass.data[DOMAIN][entry.entry_id] = coordinator

    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)

    entry.async_on_unload(entry.add_update_listener(_async_options_updated))

    return True


async def _async_register_static_path(hass: HomeAssistant) -> None:
    """Register the static path for serving card JS files."""
    if f"{DOMAIN}_static_registered" in hass.data:
        return

    frontend_dir = Path(__file__).parent / "frontend"
    await hass.http.async_register_static_paths(
        [StaticPathConfig(FRONTEND_URL, str(frontend_dir), cache_headers=False)]
    )
    hass.data[f"{DOMAIN}_static_registered"] = True
    _LOGGER.debug("Static path registered: %s", FRONTEND_URL)


async def _async_register_lovelace_resources(hass: HomeAssistant) -> None:
    """Register card JS as Lovelace resources so they load before cards."""
    if f"{DOMAIN}_frontend_registered" in hass.data:
        return

    # Ensure the static path is registered (idempotent).
    await _async_register_static_path(hass)

    card_urls = [
        f"{FRONTEND_RESOURCE_URL}?v={_FRONTEND_VERSION}",
        f"{FRONTEND_CHARGE_URL}?v={_FRONTEND_VERSION}",
    ]

    lovelace_data = hass.data.get(LOVELACE_DATA)
    resources = getattr(lovelace_data, "resources", None) if lovelace_data else None

    if isinstance(resources, ResourceStorageCollection):
        existing_urls = {item["url"] for item in resources.async_items()}
        # Remove old-version entries for our cards
        for item in resources.async_items():
            url = item["url"]
            if FRONTEND_URL in url and url not in card_urls:
                await resources.async_delete_item(item["id"])
                _LOGGER.debug("Removed stale Lovelace resource: %s", url)
        for url in card_urls:
            if url not in existing_urls:
                await resources.async_create_item(
                    {"res_type": "module", "url": url}
                )
                _LOGGER.debug("Added Lovelace resource: %s", url)
    else:
        _LOGGER.debug("Lovelace not in storage mode, using add_extra_js_url")
        for url in card_urls:
            add_extra_js_url(hass, url)

    hass.data[f"{DOMAIN}_frontend_registered"] = True
    _LOGGER.debug("Frontend card resources registered")


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
