"""Device tracker entity for the Hello Smart integration."""

from __future__ import annotations

from homeassistant.components.device_tracker import SourceType
from homeassistant.components.device_tracker.config_entry import TrackerEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import DOMAIN
from .coordinator import SmartDataCoordinator


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up Hello Smart device tracker entities from a config entry."""
    coordinator: SmartDataCoordinator = hass.data[DOMAIN][entry.entry_id]

    entities: list[SmartDeviceTracker] = [
        SmartDeviceTracker(coordinator=coordinator, vin=vin)
        for vin in coordinator.data
    ]

    async_add_entities(entities)


class SmartDeviceTracker(CoordinatorEntity[SmartDataCoordinator], TrackerEntity):
    """Representation of a Hello Smart vehicle tracker."""

    _attr_has_entity_name = True
    _attr_name = "Location"

    def __init__(
        self,
        coordinator: SmartDataCoordinator,
        vin: str,
    ) -> None:
        """Initialize the device tracker."""
        super().__init__(coordinator)
        self._vin = vin
        self._attr_unique_id = f"{vin}_location"
        self._attr_device_info = coordinator.get_device_info(vin)

    @property
    def source_type(self) -> SourceType:
        """Return the source type."""
        return SourceType.GPS

    @property
    def latitude(self) -> float | None:
        """Return the latitude of the vehicle."""
        data = self.coordinator.data.get(self._vin)
        if data is None:
            return None
        return data.status.latitude

    @property
    def longitude(self) -> float | None:
        """Return the longitude of the vehicle."""
        data = self.coordinator.data.get(self._vin)
        if data is None:
            return None
        return data.status.longitude

    @property
    def available(self) -> bool:
        """Return True if entity is available (has GPS data)."""
        if not super().available or self._vin not in self.coordinator.data:
            return False
        data = self.coordinator.data[self._vin]
        return data.status.latitude is not None and data.status.longitude is not None
