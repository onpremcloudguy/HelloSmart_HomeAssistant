"""Time entities for the Hello Smart integration."""

from __future__ import annotations

from collections.abc import Callable, Coroutine
from dataclasses import dataclass
from datetime import time as dt_time
from typing import Any

from homeassistant.components.time import TimeEntity, TimeEntityDescription
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import DOMAIN
from .coordinator import SmartDataCoordinator
from .models import VehicleData


@dataclass(frozen=True, kw_only=True)
class SmartTimeEntityDescription(TimeEntityDescription):
    """Describes a Hello Smart time entity."""

    set_value_fn: Callable[
        [SmartDataCoordinator, str, dt_time], Coroutine[Any, Any, None]
    ]
    native_value_fn: Callable[[VehicleData], dt_time | None]
    available_fn: Callable[[VehicleData], bool]


def _parse_time_str(time_str: str) -> dt_time | None:
    """Parse an HH:MM or HH:MM:SS time string to a time object."""
    if not time_str:
        return None
    try:
        parts = time_str.split(":")
        return dt_time(int(parts[0]), int(parts[1]))
    except (ValueError, IndexError):
        return None


async def _set_charging_start(
    coordinator: SmartDataCoordinator, vin: str, value: dt_time
) -> None:
    account = coordinator.account
    if account is None:
        return
    time_str = value.strftime("%H:%M")
    await coordinator._api.async_set_charging_reservation(
        account, vin, {"startTime": time_str}
    )
    data = coordinator.data.get(vin)
    if data and data.charging_reservation:
        data.charging_reservation.start_time = time_str


async def _set_charging_end(
    coordinator: SmartDataCoordinator, vin: str, value: dt_time
) -> None:
    account = coordinator.account
    if account is None:
        return
    time_str = value.strftime("%H:%M")
    await coordinator._api.async_set_charging_reservation(
        account, vin, {"endTime": time_str}
    )
    data = coordinator.data.get(vin)
    if data and data.charging_reservation:
        data.charging_reservation.end_time = time_str


async def _set_climate_schedule_time(
    coordinator: SmartDataCoordinator, vin: str, value: dt_time
) -> None:
    account = coordinator.account
    if account is None:
        return
    time_str = value.strftime("%H:%M")
    await coordinator._api.async_set_climate_schedule(
        account, vin, {"scheduledTime": time_str}
    )
    data = coordinator.data.get(vin)
    if data and data.climate_schedule:
        data.climate_schedule.scheduled_time = time_str


TIME_DESCRIPTIONS: list[SmartTimeEntityDescription] = [
    SmartTimeEntityDescription(
        key="smart_charging_start",
        translation_key="smart_charging_start",
        icon="mdi:battery-clock",
        set_value_fn=_set_charging_start,
        native_value_fn=lambda data: _parse_time_str(
            data.charging_reservation.start_time
        )
        if data.charging_reservation
        else None,
        available_fn=lambda data: data.charging_reservation is not None,
    ),
    SmartTimeEntityDescription(
        key="smart_charging_end",
        translation_key="smart_charging_end",
        icon="mdi:battery-clock-outline",
        set_value_fn=_set_charging_end,
        native_value_fn=lambda data: _parse_time_str(
            data.charging_reservation.end_time
        )
        if data.charging_reservation
        else None,
        available_fn=lambda data: data.charging_reservation is not None,
    ),
    SmartTimeEntityDescription(
        key="smart_climate_schedule_time",
        translation_key="smart_climate_schedule_time",
        icon="mdi:clock-outline",
        set_value_fn=_set_climate_schedule_time,
        native_value_fn=lambda data: _parse_time_str(
            data.climate_schedule.scheduled_time
        )
        if data.climate_schedule
        else None,
        available_fn=lambda data: data.climate_schedule is not None,
    ),
]


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up Hello Smart time entities from a config entry."""
    coordinator: SmartDataCoordinator = hass.data[DOMAIN][entry.entry_id]

    entities: list[SmartTime] = []
    for vin, vehicle_data in coordinator.data.items():
        for description in TIME_DESCRIPTIONS:
            if not description.available_fn(vehicle_data):
                continue
            entities.append(
                SmartTime(
                    coordinator=coordinator,
                    description=description,
                    vin=vin,
                )
            )

    async_add_entities(entities)


class SmartTime(CoordinatorEntity[SmartDataCoordinator], TimeEntity):
    """Representation of a Hello Smart time entity."""

    entity_description: SmartTimeEntityDescription
    _attr_has_entity_name = True

    def __init__(
        self,
        coordinator: SmartDataCoordinator,
        description: SmartTimeEntityDescription,
        vin: str,
    ) -> None:
        """Initialize the time entity."""
        super().__init__(coordinator)
        self.entity_description = description
        self._vin = vin
        self._attr_unique_id = f"{vin}_{description.key}"
        self._attr_device_info = coordinator.get_device_info(vin)

    @property
    def native_value(self) -> dt_time | None:
        """Return the current time value."""
        data = self.coordinator.data.get(self._vin)
        if data is None:
            return None
        return self.entity_description.native_value_fn(data)

    async def async_set_value(self, value: dt_time) -> None:
        """Set the time value."""
        await self.entity_description.set_value_fn(
            self.coordinator, self._vin, value
        )
        self.async_write_ha_state()

    @property
    def available(self) -> bool:
        """Return True if entity is available."""
        if not super().available:
            return False
        data = self.coordinator.data.get(self._vin)
        if data is None:
            return False
        return self.entity_description.available_fn(data)
