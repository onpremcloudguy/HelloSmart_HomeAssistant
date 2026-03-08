"""Select entities for the Hello Smart integration."""

from __future__ import annotations

from collections.abc import Callable, Coroutine
from dataclasses import dataclass
from typing import Any

from homeassistant.components.select import SelectEntity, SelectEntityDescription
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import DOMAIN, SERVICE_ID_SEAT_HEAT, SERVICE_ID_SEAT_VENT
from .coordinator import SmartDataCoordinator
from .models import VehicleData

SEAT_HEAT_OPTIONS = ["off", "low", "medium", "high"]
SEAT_HEAT_LEVEL_MAP = {"off": "0", "low": "1", "medium": "2", "high": "3"}
SEAT_HEAT_REVERSE_MAP = {0: "off", 1: "low", 2: "medium", 3: "high"}

SEAT_VENT_OPTIONS = ["off", "low", "medium", "high"]
SEAT_VENT_LEVEL_MAP = {"off": "0", "low": "1", "medium": "2", "high": "3"}
SEAT_VENT_REVERSE_MAP = {0: "off", 1: "low", 2: "medium", 3: "high"}


@dataclass(frozen=True, kw_only=True)
class SmartSelectEntityDescription(SelectEntityDescription):
    """Describes a Hello Smart select entity."""

    select_option_fn: Callable[
        [SmartDataCoordinator, str, str], Coroutine[Any, Any, None]
    ]
    current_option_fn: Callable[[VehicleData], str | None]
    seat_key: str


async def _set_seat_heat(
    coordinator: SmartDataCoordinator, vin: str, seat_key: str, level: str,
) -> None:
    """Send seat heating command."""
    await coordinator.async_send_vehicle_command(
        vin,
        SERVICE_ID_SEAT_HEAT,
        "start",
        [
            {"key": "rsh.seat", "value": seat_key},
            {"key": "rsh.level", "value": SEAT_HEAT_LEVEL_MAP[level]},
        ],
    )


async def _set_seat_vent(
    coordinator: SmartDataCoordinator, vin: str, seat_key: str, level: str,
) -> None:
    """Send seat ventilation command."""
    await coordinator.async_send_vehicle_command(
        vin,
        SERVICE_ID_SEAT_VENT,
        "start",
        [
            {"key": "rsv.seat", "value": seat_key},
            {"key": "rsv.level", "value": SEAT_VENT_LEVEL_MAP[level]},
        ],
    )


SELECT_DESCRIPTIONS: tuple[SmartSelectEntityDescription, ...] = (
    SmartSelectEntityDescription(
        key="driver_seat_heating_control",
        translation_key="driver_seat_heating_control",
        icon="mdi:car-seat-heater",
        options=SEAT_HEAT_OPTIONS,
        seat_key="front-left",
        select_option_fn=lambda coord, vin, option: _set_seat_heat(
            coord, vin, "front-left", option,
        ),
        current_option_fn=lambda data: SEAT_HEAT_REVERSE_MAP.get(
            data.status.driver_seat_heating or 0, "off",
        ),
    ),
    SmartSelectEntityDescription(
        key="passenger_seat_heating_control",
        translation_key="passenger_seat_heating_control",
        icon="mdi:car-seat-heater",
        options=SEAT_HEAT_OPTIONS,
        seat_key="front-right",
        select_option_fn=lambda coord, vin, option: _set_seat_heat(
            coord, vin, "front-right", option,
        ),
        current_option_fn=lambda data: SEAT_HEAT_REVERSE_MAP.get(
            data.status.passenger_seat_heating or 0, "off",
        ),
    ),
    SmartSelectEntityDescription(
        key="steering_wheel_heating_control",
        translation_key="steering_wheel_heating_control",
        icon="mdi:steering",
        options=SEAT_HEAT_OPTIONS,
        seat_key="steering_wheel",
        select_option_fn=lambda coord, vin, option: _set_seat_heat(
            coord, vin, "steering_wheel", option,
        ),
        current_option_fn=lambda data: SEAT_HEAT_REVERSE_MAP.get(
            data.status.steering_wheel_heating or 0, "off",
        ),
    ),
    # ── Seat Ventilation ────────────────────────────────────────────────
    SmartSelectEntityDescription(
        key="driver_seat_ventilation_control",
        translation_key="driver_seat_ventilation_control",
        icon="mdi:car-seat-cooler",
        options=SEAT_VENT_OPTIONS,
        seat_key="front-left",
        select_option_fn=lambda coord, vin, option: _set_seat_vent(
            coord, vin, "front-left", option,
        ),
        current_option_fn=lambda data: SEAT_VENT_REVERSE_MAP.get(
            data.status.driver_seat_ventilation or 0, "off",
        ),
    ),
)


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up Hello Smart select entities from a config entry."""
    coordinator: SmartDataCoordinator = hass.data[DOMAIN][entry.entry_id]

    entities: list[SmartSelectEntity] = []
    for vin in coordinator.data:
        for description in SELECT_DESCRIPTIONS:
            entities.append(
                SmartSelectEntity(
                    coordinator=coordinator,
                    description=description,
                    vin=vin,
                )
            )

    async_add_entities(entities)


class SmartSelectEntity(CoordinatorEntity[SmartDataCoordinator], SelectEntity):
    """Representation of a Hello Smart select entity."""

    entity_description: SmartSelectEntityDescription
    _attr_has_entity_name = True

    def __init__(
        self,
        coordinator: SmartDataCoordinator,
        description: SmartSelectEntityDescription,
        vin: str,
    ) -> None:
        """Initialize the select entity."""
        super().__init__(coordinator)
        self.entity_description = description
        self._vin = vin
        self._attr_unique_id = f"{vin}_{description.key}"
        self._attr_device_info = coordinator.get_device_info(vin)

    @property
    def current_option(self) -> str | None:
        """Return the current selected option."""
        data = self.coordinator.data.get(self._vin)
        if data is None:
            return None
        return self.entity_description.current_option_fn(data)

    async def async_select_option(self, option: str) -> None:
        """Change the selected option."""
        await self.entity_description.select_option_fn(
            self.coordinator, self._vin, option,
        )

    @property
    def available(self) -> bool:
        """Return True if entity is available."""
        return super().available and self._vin in self.coordinator.data
