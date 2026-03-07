"""Binary sensor entities for the Hello Smart integration."""

from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass
from typing import Any

from homeassistant.components.binary_sensor import (
    BinarySensorDeviceClass,
    BinarySensorEntity,
    BinarySensorEntityDescription,
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import DOMAIN
from .coordinator import SmartDataCoordinator
from .models import VehicleData


@dataclass(frozen=True, kw_only=True)
class SmartBinarySensorEntityDescription(BinarySensorEntityDescription):
    """Describes a Hello Smart binary sensor entity."""

    is_on_fn: Callable[[VehicleData], bool | None]


BINARY_SENSOR_DESCRIPTIONS: tuple[SmartBinarySensorEntityDescription, ...] = (
    # Door sensors
    SmartBinarySensorEntityDescription(
        key="driver_door",
        translation_key="driver_door",
        device_class=BinarySensorDeviceClass.DOOR,
        is_on_fn=lambda data: data.status.doors.get("driver"),
    ),
    SmartBinarySensorEntityDescription(
        key="passenger_door",
        translation_key="passenger_door",
        device_class=BinarySensorDeviceClass.DOOR,
        is_on_fn=lambda data: data.status.doors.get("passenger"),
    ),
    SmartBinarySensorEntityDescription(
        key="rear_left_door",
        translation_key="rear_left_door",
        device_class=BinarySensorDeviceClass.DOOR,
        is_on_fn=lambda data: data.status.doors.get("rear_left"),
    ),
    SmartBinarySensorEntityDescription(
        key="rear_right_door",
        translation_key="rear_right_door",
        device_class=BinarySensorDeviceClass.DOOR,
        is_on_fn=lambda data: data.status.doors.get("rear_right"),
    ),
    SmartBinarySensorEntityDescription(
        key="trunk",
        translation_key="trunk",
        device_class=BinarySensorDeviceClass.DOOR,
        is_on_fn=lambda data: data.status.doors.get("trunk"),
    ),
    # Window sensors
    SmartBinarySensorEntityDescription(
        key="driver_window",
        translation_key="driver_window",
        device_class=BinarySensorDeviceClass.WINDOW,
        is_on_fn=lambda data: data.status.windows.get("driver"),
    ),
    SmartBinarySensorEntityDescription(
        key="passenger_window",
        translation_key="passenger_window",
        device_class=BinarySensorDeviceClass.WINDOW,
        is_on_fn=lambda data: data.status.windows.get("passenger"),
    ),
    SmartBinarySensorEntityDescription(
        key="rear_left_window",
        translation_key="rear_left_window",
        device_class=BinarySensorDeviceClass.WINDOW,
        is_on_fn=lambda data: data.status.windows.get("rear_left"),
    ),
    SmartBinarySensorEntityDescription(
        key="rear_right_window",
        translation_key="rear_right_window",
        device_class=BinarySensorDeviceClass.WINDOW,
        is_on_fn=lambda data: data.status.windows.get("rear_right"),
    ),
    # Charging connected
    SmartBinarySensorEntityDescription(
        key="charger_connected",
        translation_key="charger_connected",
        device_class=BinarySensorDeviceClass.PLUG,
        is_on_fn=lambda data: data.status.charger_connected,
    ),
    # OTA update available
    SmartBinarySensorEntityDescription(
        key="update_available",
        translation_key="update_available",
        device_class=BinarySensorDeviceClass.UPDATE,
        is_on_fn=lambda data: data.ota.update_available,
    ),
)


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up Hello Smart binary sensor entities from a config entry."""
    coordinator: SmartDataCoordinator = hass.data[DOMAIN][entry.entry_id]

    entities: list[SmartBinarySensorEntity] = []
    for vin in coordinator.data:
        for description in BINARY_SENSOR_DESCRIPTIONS:
            entities.append(
                SmartBinarySensorEntity(
                    coordinator=coordinator,
                    description=description,
                    vin=vin,
                )
            )

    async_add_entities(entities)


class SmartBinarySensorEntity(
    CoordinatorEntity[SmartDataCoordinator], BinarySensorEntity
):
    """Representation of a Hello Smart binary sensor."""

    entity_description: SmartBinarySensorEntityDescription
    _attr_has_entity_name = True

    def __init__(
        self,
        coordinator: SmartDataCoordinator,
        description: SmartBinarySensorEntityDescription,
        vin: str,
    ) -> None:
        """Initialize the binary sensor."""
        super().__init__(coordinator)
        self.entity_description = description
        self._vin = vin
        self._attr_unique_id = f"{vin}_{description.key}"
        self._attr_device_info = coordinator.get_device_info(vin)

    @property
    def is_on(self) -> bool | None:
        """Return True if the binary sensor is on."""
        data = self.coordinator.data.get(self._vin)
        if data is None:
            return None
        return self.entity_description.is_on_fn(data)

    @property
    def available(self) -> bool:
        """Return True if entity is available."""
        return super().available and self._vin in self.coordinator.data
