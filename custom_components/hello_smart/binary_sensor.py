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
from homeassistant.const import EntityCategory
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
    # ── Doors ──────────────────────────────────────────────────────
    SmartBinarySensorEntityDescription(
        key="driver_door",
        translation_key="driver_door",
        icon="mdi:car-door",
        device_class=BinarySensorDeviceClass.DOOR,
        is_on_fn=lambda data: data.status.doors.get("driver"),
    ),
    SmartBinarySensorEntityDescription(
        key="passenger_door",
        translation_key="passenger_door",
        icon="mdi:car-door",
        device_class=BinarySensorDeviceClass.DOOR,
        is_on_fn=lambda data: data.status.doors.get("passenger"),
    ),
    SmartBinarySensorEntityDescription(
        key="rear_left_door",
        translation_key="rear_left_door",
        icon="mdi:car-door",
        device_class=BinarySensorDeviceClass.DOOR,
        is_on_fn=lambda data: data.status.doors.get("rear_left"),
    ),
    SmartBinarySensorEntityDescription(
        key="rear_right_door",
        translation_key="rear_right_door",
        icon="mdi:car-door",
        device_class=BinarySensorDeviceClass.DOOR,
        is_on_fn=lambda data: data.status.doors.get("rear_right"),
    ),
    SmartBinarySensorEntityDescription(
        key="trunk",
        translation_key="trunk",
        icon="mdi:car-back",
        device_class=BinarySensorDeviceClass.DOOR,
        is_on_fn=lambda data: data.status.doors.get("trunk"),
    ),
    # ── Windows ───────────────────────────────────────────────────
    SmartBinarySensorEntityDescription(
        key="driver_window",
        translation_key="driver_window",
        icon="mdi:car-door",
        device_class=BinarySensorDeviceClass.WINDOW,
        is_on_fn=lambda data: data.status.windows.get("driver"),
    ),
    SmartBinarySensorEntityDescription(
        key="passenger_window",
        translation_key="passenger_window",
        icon="mdi:car-door",
        device_class=BinarySensorDeviceClass.WINDOW,
        is_on_fn=lambda data: data.status.windows.get("passenger"),
    ),
    SmartBinarySensorEntityDescription(
        key="rear_left_window",
        translation_key="rear_left_window",
        icon="mdi:car-door",
        device_class=BinarySensorDeviceClass.WINDOW,
        is_on_fn=lambda data: data.status.windows.get("rear_left"),
    ),
    SmartBinarySensorEntityDescription(
        key="rear_right_window",
        translation_key="rear_right_window",
        icon="mdi:car-door",
        device_class=BinarySensorDeviceClass.WINDOW,
        is_on_fn=lambda data: data.status.windows.get("rear_right"),
    ),
    # ── Charging ──────────────────────────────────────────────────
    SmartBinarySensorEntityDescription(
        key="charger_connected",
        translation_key="charger_connected",
        icon="mdi:ev-plug-type2",
        device_class=BinarySensorDeviceClass.PLUG,
        is_on_fn=lambda data: data.status.charger_connected,
    ),
    # ── Updates ───────────────────────────────────────────────────
    SmartBinarySensorEntityDescription(
        key="update_available",
        translation_key="update_available",
        icon="mdi:package-up",
        device_class=BinarySensorDeviceClass.UPDATE,
        entity_category=EntityCategory.DIAGNOSTIC,
        is_on_fn=lambda data: data.ota.update_available,
    ),
    # ── Tyre Warnings ────────────────────────────────────────────
    SmartBinarySensorEntityDescription(
        key="tyre_warning_fl",
        translation_key="tyre_warning_fl",
        icon="mdi:car-tire-alert",
        device_class=BinarySensorDeviceClass.PROBLEM,
        is_on_fn=lambda data: data.status.tyre_warning_fl,
    ),
    SmartBinarySensorEntityDescription(
        key="tyre_warning_fr",
        translation_key="tyre_warning_fr",
        icon="mdi:car-tire-alert",
        device_class=BinarySensorDeviceClass.PROBLEM,
        is_on_fn=lambda data: data.status.tyre_warning_fr,
    ),
    SmartBinarySensorEntityDescription(
        key="tyre_warning_rl",
        translation_key="tyre_warning_rl",
        icon="mdi:car-tire-alert",
        device_class=BinarySensorDeviceClass.PROBLEM,
        is_on_fn=lambda data: data.status.tyre_warning_rl,
    ),
    SmartBinarySensorEntityDescription(
        key="tyre_warning_rr",
        translation_key="tyre_warning_rr",
        icon="mdi:car-tire-alert",
        device_class=BinarySensorDeviceClass.PROBLEM,
        is_on_fn=lambda data: data.status.tyre_warning_rr,
    ),
    # ── Connectivity ──────────────────────────────────────────────
    SmartBinarySensorEntityDescription(
        key="telematics_connected",
        translation_key="telematics_connected",
        icon="mdi:antenna",
        device_class=BinarySensorDeviceClass.CONNECTIVITY,
        entity_category=EntityCategory.DIAGNOSTIC,
        is_on_fn=lambda data: data.telematics.connected if data.telematics else None,
    ),
    # ── Safety ────────────────────────────────────────────────────
    SmartBinarySensorEntityDescription(
        key="brake_fluid_ok",
        translation_key="brake_fluid_ok",
        icon="mdi:car-brake-alert",
        device_class=BinarySensorDeviceClass.PROBLEM,
        is_on_fn=lambda data: (
            not data.status.brake_fluid_ok
            if data.status.brake_fluid_ok is not None
            else None
        ),
    ),
    # ── Accessories ───────────────────────────────────────────────
    SmartBinarySensorEntityDescription(
        key="fridge_active",
        translation_key="fridge_active",
        icon="mdi:fridge",
        device_class=BinarySensorDeviceClass.RUNNING,
        is_on_fn=lambda data: data.fridge.active if data.fridge else None,
    ),
    SmartBinarySensorEntityDescription(
        key="fragrance_active",
        translation_key="fragrance_active",
        icon="mdi:spray",
        is_on_fn=lambda data: (
            data.fragrance.active if data.fragrance
            else (data.status.fragrance_active if data.status.fragrance_active is not None else None)
        ),
    ),
    SmartBinarySensorEntityDescription(
        key="locker_open",
        translation_key="locker_open",
        icon="mdi:lock-open-variant",
        device_class=BinarySensorDeviceClass.OPENING,
        is_on_fn=lambda data: data.locker.open if data.locker else None,
    ),
    # ── Security ──────────────────────────────────────────────────
    SmartBinarySensorEntityDescription(
        key="vtm_enabled",
        translation_key="vtm_enabled",
        icon="mdi:shield-car",
        is_on_fn=lambda data: data.vtm.enabled if data.vtm else None,
    ),
    SmartBinarySensorEntityDescription(
        key="vtm_notification_enabled",
        translation_key="vtm_notification_enabled",
        icon="mdi:shield-alert",
        entity_registry_enabled_default=False,
        is_on_fn=lambda data: data.vtm.notification_enabled if data.vtm else None,
    ),
    SmartBinarySensorEntityDescription(
        key="vtm_geofence_alert",
        translation_key="vtm_geofence_alert",
        icon="mdi:shield-alert-outline",
        entity_registry_enabled_default=False,
        is_on_fn=lambda data: data.vtm.geofence_alert_enabled if data.vtm else None,
    ),
    SmartBinarySensorEntityDescription(
        key="locker_locked",
        translation_key="locker_locked",
        icon="mdi:lock",
        device_class=BinarySensorDeviceClass.LOCK,
        is_on_fn=lambda data: (
            not data.locker.locked
            if data.locker and data.locker.locked is not None
            else None
        ),
    ),
    # ── Diagnostics ───────────────────────────────────────────────
    SmartBinarySensorEntityDescription(
        key="diagnostic_active",
        translation_key="diagnostic_active",
        icon="mdi:car-wrench",
        device_class=BinarySensorDeviceClass.PROBLEM,
        entity_category=EntityCategory.DIAGNOSTIC,
        is_on_fn=lambda data: (
            data.diagnostic.status == "active"
            if data.diagnostic and data.diagnostic.status
            else None
        ),
    ),
    SmartBinarySensorEntityDescription(
        key="locker_secret_set",
        translation_key="locker_secret_set",
        icon="mdi:lock-check",
        entity_category=EntityCategory.DIAGNOSTIC,
        entity_registry_enabled_default=False,
        is_on_fn=lambda data: data.locker_secret.secret_set if data.locker_secret else None,
    ),
    SmartBinarySensorEntityDescription(
        key="fota_available",
        translation_key="fota_available",
        icon="mdi:cellphone-arrow-down",
        device_class=BinarySensorDeviceClass.UPDATE,
        entity_category=EntityCategory.DIAGNOSTIC,
        is_on_fn=lambda data: data.fota_notification.has_notification if data.fota_notification else None,
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
    for vin, vehicle_data in coordinator.data.items():
        for description in BINARY_SENSOR_DESCRIPTIONS:
            if description.is_on_fn(vehicle_data) is None:
                continue
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
