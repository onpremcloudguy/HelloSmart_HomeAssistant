"""Button entities for the Hello Smart integration."""

from __future__ import annotations

from collections.abc import Callable, Coroutine
from dataclasses import dataclass
from typing import Any

from homeassistant.components.button import ButtonEntity, ButtonEntityDescription
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import DOMAIN, SERVICE_ID_HORN_LIGHT, SERVICE_ID_WINDOW_SET
from .coordinator import SmartDataCoordinator


@dataclass(frozen=True, kw_only=True)
class SmartButtonEntityDescription(ButtonEntityDescription):
    """Describes a Hello Smart button entity."""

    press_fn: Callable[[SmartDataCoordinator, str], Coroutine[Any, Any, None]]


async def _press_horn(coordinator: SmartDataCoordinator, vin: str) -> None:
    await coordinator.async_send_vehicle_command(
        vin,
        SERVICE_ID_HORN_LIGHT,
        "start",
        [{"key": "rhl.horn", "value": "1"}],
    )


async def _press_flash(coordinator: SmartDataCoordinator, vin: str) -> None:
    await coordinator.async_send_vehicle_command(
        vin,
        SERVICE_ID_HORN_LIGHT,
        "start",
        [{"key": "rhl.flash", "value": "1"}],
    )


async def _press_find_my_car(coordinator: SmartDataCoordinator, vin: str) -> None:
    await coordinator.async_send_vehicle_command(
        vin,
        SERVICE_ID_HORN_LIGHT,
        "start",
        [
            {"key": "rhl.horn", "value": "1"},
            {"key": "rhl.flash", "value": "1"},
        ],
    )


async def _press_close_windows(coordinator: SmartDataCoordinator, vin: str) -> None:
    await coordinator.async_send_vehicle_command(
        vin,
        SERVICE_ID_WINDOW_SET,
        "start",
        [{"key": "rws.close", "value": "1"}],
    )


BUTTON_DESCRIPTIONS: list[SmartButtonEntityDescription] = [
    SmartButtonEntityDescription(
        key="smart_horn",
        translation_key="smart_horn",
        icon="mdi:bullhorn",
        press_fn=_press_horn,
    ),
    SmartButtonEntityDescription(
        key="smart_flash_lights",
        translation_key="smart_flash_lights",
        icon="mdi:car-light-high",
        press_fn=_press_flash,
    ),
    SmartButtonEntityDescription(
        key="smart_find_my_car",
        translation_key="smart_find_my_car",
        icon="mdi:car-search",
        press_fn=_press_find_my_car,
    ),
    SmartButtonEntityDescription(
        key="smart_close_windows",
        translation_key="smart_close_windows",
        icon="mdi:window-closed",
        press_fn=_press_close_windows,
    ),
]


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up Hello Smart button entities from a config entry."""
    coordinator: SmartDataCoordinator = hass.data[DOMAIN][entry.entry_id]

    entities: list[SmartButton] = []
    for vin in coordinator.data:
        for description in BUTTON_DESCRIPTIONS:
            entities.append(
                SmartButton(
                    coordinator=coordinator,
                    description=description,
                    vin=vin,
                )
            )

    async_add_entities(entities)


class SmartButton(CoordinatorEntity[SmartDataCoordinator], ButtonEntity):
    """Representation of a Hello Smart button."""

    entity_description: SmartButtonEntityDescription
    _attr_has_entity_name = True

    def __init__(
        self,
        coordinator: SmartDataCoordinator,
        description: SmartButtonEntityDescription,
        vin: str,
    ) -> None:
        """Initialize the button."""
        super().__init__(coordinator)
        self.entity_description = description
        self._vin = vin
        self._attr_unique_id = f"{vin}_{description.key}"
        self._attr_device_info = coordinator.get_device_info(vin)

    async def async_press(self) -> None:
        """Handle the button press."""
        await self.entity_description.press_fn(self.coordinator, self._vin)

    @property
    def available(self) -> bool:
        """Return True if entity is available."""
        return super().available and self._vin in self.coordinator.data
