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
        is_on_fn=lambda data: data.telematics.connected if data.telematics else False,
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
            else False
        ),
    ),
    # ── Accessories ───────────────────────────────────────────────
    SmartBinarySensorEntityDescription(
        key="fridge_active",
        translation_key="fridge_active",
        icon="mdi:fridge",
        device_class=BinarySensorDeviceClass.RUNNING,
        is_on_fn=lambda data: data.fridge.active if data.fridge else False,
    ),
    SmartBinarySensorEntityDescription(
        key="fragrance_active",
        translation_key="fragrance_active",
        icon="mdi:spray",
        is_on_fn=lambda data: (
            data.fragrance.active if data.fragrance
            else (data.status.fragrance_active if data.status.fragrance_active is not None else False)
        ),
    ),
    SmartBinarySensorEntityDescription(
        key="locker_open",
        translation_key="locker_open",
        icon="mdi:lock-open-variant",
        device_class=BinarySensorDeviceClass.OPENING,
        is_on_fn=lambda data: data.locker.open if data.locker else False,
    ),
    # ── Security ──────────────────────────────────────────────────
    SmartBinarySensorEntityDescription(
        key="vtm_enabled",
        translation_key="vtm_enabled",
        icon="mdi:shield-car",
        is_on_fn=lambda data: data.vtm.enabled if data.vtm else False,
    ),
    SmartBinarySensorEntityDescription(
        key="vtm_notification_enabled",
        translation_key="vtm_notification_enabled",
        icon="mdi:shield-alert",
        entity_registry_enabled_default=False,
        is_on_fn=lambda data: data.vtm.notification_enabled if data.vtm else False,
    ),
    SmartBinarySensorEntityDescription(
        key="vtm_geofence_alert",
        translation_key="vtm_geofence_alert",
        icon="mdi:shield-alert-outline",
        entity_registry_enabled_default=False,
        is_on_fn=lambda data: data.vtm.geofence_alert_enabled if data.vtm else False,
    ),
    SmartBinarySensorEntityDescription(
        key="locker_locked",
        translation_key="locker_locked",
        icon="mdi:lock",
        device_class=BinarySensorDeviceClass.LOCK,
        is_on_fn=lambda data: (
            not data.locker.locked
            if data.locker and data.locker.locked is not None
            else False
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
            else False
        ),
    ),
    SmartBinarySensorEntityDescription(
        key="locker_secret_set",
        translation_key="locker_secret_set",
        icon="mdi:lock-check",
        entity_category=EntityCategory.DIAGNOSTIC,
        entity_registry_enabled_default=False,
        is_on_fn=lambda data: data.locker_secret.secret_set if data.locker_secret else False,
    ),
    SmartBinarySensorEntityDescription(
        key="fota_available",
        translation_key="fota_available",
        icon="mdi:cellphone-arrow-down",
        device_class=BinarySensorDeviceClass.UPDATE,
        entity_category=EntityCategory.DIAGNOSTIC,
        is_on_fn=lambda data: data.fota_notification.has_notification if data.fota_notification else False,
    ),
    # ── Lights (from runningStatus) ───────────────────────────────────
    SmartBinarySensorEntityDescription(
        key="low_beam",
        translation_key="low_beam",
        icon="mdi:car-light-dimmed",
        device_class=BinarySensorDeviceClass.LIGHT,
        is_on_fn=lambda data: data.status.light_low_beam,
    ),
    SmartBinarySensorEntityDescription(
        key="high_beam",
        translation_key="high_beam",
        icon="mdi:car-light-high",
        device_class=BinarySensorDeviceClass.LIGHT,
        is_on_fn=lambda data: data.status.light_high_beam,
    ),
    SmartBinarySensorEntityDescription(
        key="daytime_running_lights",
        translation_key="daytime_running_lights",
        icon="mdi:car-light-dimmed",
        device_class=BinarySensorDeviceClass.LIGHT,
        is_on_fn=lambda data: data.status.light_drl,
    ),
    SmartBinarySensorEntityDescription(
        key="front_fog_light",
        translation_key="front_fog_light",
        icon="mdi:car-light-fog",
        device_class=BinarySensorDeviceClass.LIGHT,
        is_on_fn=lambda data: data.status.light_front_fog,
    ),
    SmartBinarySensorEntityDescription(
        key="rear_fog_light",
        translation_key="rear_fog_light",
        icon="mdi:car-light-fog",
        device_class=BinarySensorDeviceClass.LIGHT,
        is_on_fn=lambda data: data.status.light_rear_fog,
    ),
    SmartBinarySensorEntityDescription(
        key="position_light_front",
        translation_key="position_light_front",
        icon="mdi:car-parking-lights",
        device_class=BinarySensorDeviceClass.LIGHT,
        entity_registry_enabled_default=False,
        is_on_fn=lambda data: data.status.light_position_front,
    ),
    SmartBinarySensorEntityDescription(
        key="position_light_rear",
        translation_key="position_light_rear",
        icon="mdi:car-parking-lights",
        device_class=BinarySensorDeviceClass.LIGHT,
        entity_registry_enabled_default=False,
        is_on_fn=lambda data: data.status.light_position_rear,
    ),
    SmartBinarySensorEntityDescription(
        key="turn_indicator_left",
        translation_key="turn_indicator_left",
        icon="mdi:arrow-left-bold",
        device_class=BinarySensorDeviceClass.LIGHT,
        is_on_fn=lambda data: data.status.light_turn_left,
    ),
    SmartBinarySensorEntityDescription(
        key="turn_indicator_right",
        translation_key="turn_indicator_right",
        icon="mdi:arrow-right-bold",
        device_class=BinarySensorDeviceClass.LIGHT,
        is_on_fn=lambda data: data.status.light_turn_right,
    ),
    SmartBinarySensorEntityDescription(
        key="reverse_light",
        translation_key="reverse_light",
        icon="mdi:car-light-dimmed",
        device_class=BinarySensorDeviceClass.LIGHT,
        is_on_fn=lambda data: data.status.light_reverse,
    ),
    SmartBinarySensorEntityDescription(
        key="stop_light",
        translation_key="stop_light",
        icon="mdi:car-brake-alert",
        device_class=BinarySensorDeviceClass.LIGHT,
        is_on_fn=lambda data: data.status.light_stop,
    ),
    SmartBinarySensorEntityDescription(
        key="hazard_lights",
        translation_key="hazard_lights",
        icon="mdi:hazard-lights",
        device_class=BinarySensorDeviceClass.LIGHT,
        is_on_fn=lambda data: data.status.light_hazard,
    ),
    SmartBinarySensorEntityDescription(
        key="ahbc",
        translation_key="ahbc",
        icon="mdi:car-light-high",
        device_class=BinarySensorDeviceClass.LIGHT,
        entity_registry_enabled_default=False,
        is_on_fn=lambda data: data.status.light_ahbc,
    ),
    SmartBinarySensorEntityDescription(
        key="afs",
        translation_key="afs",
        icon="mdi:car-light-high",
        device_class=BinarySensorDeviceClass.LIGHT,
        entity_registry_enabled_default=False,
        is_on_fn=lambda data: data.status.light_afs,
    ),
    SmartBinarySensorEntityDescription(
        key="ahl",
        translation_key="ahl",
        icon="mdi:car-light-high",
        device_class=BinarySensorDeviceClass.LIGHT,
        entity_registry_enabled_default=False,
        is_on_fn=lambda data: data.status.light_ahl,
    ),
    SmartBinarySensorEntityDescription(
        key="highway_light",
        translation_key="highway_light",
        icon="mdi:highway",
        device_class=BinarySensorDeviceClass.LIGHT,
        entity_registry_enabled_default=False,
        is_on_fn=lambda data: data.status.light_highway,
    ),
    SmartBinarySensorEntityDescription(
        key="corner_light",
        translation_key="corner_light",
        icon="mdi:car-light-dimmed",
        device_class=BinarySensorDeviceClass.LIGHT,
        entity_registry_enabled_default=False,
        is_on_fn=lambda data: data.status.light_corner,
    ),
    SmartBinarySensorEntityDescription(
        key="welcome_light",
        translation_key="welcome_light",
        icon="mdi:lightbulb-on",
        device_class=BinarySensorDeviceClass.LIGHT,
        is_on_fn=lambda data: data.status.light_welcome,
    ),
    SmartBinarySensorEntityDescription(
        key="goodbye_light",
        translation_key="goodbye_light",
        icon="mdi:lightbulb-on",
        device_class=BinarySensorDeviceClass.LIGHT,
        is_on_fn=lambda data: data.status.light_goodbye,
    ),
    SmartBinarySensorEntityDescription(
        key="home_safe_light",
        translation_key="home_safe_light",
        icon="mdi:home-lightbulb",
        device_class=BinarySensorDeviceClass.LIGHT,
        is_on_fn=lambda data: data.status.light_home_safe,
    ),
    SmartBinarySensorEntityDescription(
        key="approach_light",
        translation_key="approach_light",
        icon="mdi:lightbulb-on",
        device_class=BinarySensorDeviceClass.LIGHT,
        is_on_fn=lambda data: data.status.light_approach,
    ),
    SmartBinarySensorEntityDescription(
        key="light_show_active",
        translation_key="light_show_active",
        icon="mdi:lightbulb-group",
        device_class=BinarySensorDeviceClass.LIGHT,
        is_on_fn=lambda data: data.status.light_show,
    ),
    SmartBinarySensorEntityDescription(
        key="all_weather_light",
        translation_key="all_weather_light",
        icon="mdi:weather-partly-cloudy",
        device_class=BinarySensorDeviceClass.LIGHT,
        entity_registry_enabled_default=False,
        is_on_fn=lambda data: data.status.light_all_weather,
    ),
    SmartBinarySensorEntityDescription(
        key="flash_light",
        translation_key="flash_light",
        icon="mdi:flash",
        device_class=BinarySensorDeviceClass.LIGHT,
        entity_registry_enabled_default=False,
        is_on_fn=lambda data: data.status.light_flash,
    ),
    # ── Safety / Locks ────────────────────────────────────────────────
    SmartBinarySensorEntityDescription(
        key="door_lock_driver",
        translation_key="door_lock_driver",
        icon="mdi:car-door-lock",
        device_class=BinarySensorDeviceClass.LOCK,
        is_on_fn=lambda data: (
            data.status.door_lock_driver == 0
            if data.status.door_lock_driver is not None
            else False
        ),
    ),
    SmartBinarySensorEntityDescription(
        key="door_lock_passenger",
        translation_key="door_lock_passenger",
        icon="mdi:car-door-lock",
        device_class=BinarySensorDeviceClass.LOCK,
        is_on_fn=lambda data: (
            data.status.door_lock_passenger == 0
            if data.status.door_lock_passenger is not None
            else False
        ),
    ),
    SmartBinarySensorEntityDescription(
        key="door_lock_rear_left",
        translation_key="door_lock_rear_left",
        icon="mdi:car-door-lock",
        device_class=BinarySensorDeviceClass.LOCK,
        is_on_fn=lambda data: (
            data.status.door_lock_driver_rear == 0
            if data.status.door_lock_driver_rear is not None
            else False
        ),
    ),
    SmartBinarySensorEntityDescription(
        key="door_lock_rear_right",
        translation_key="door_lock_rear_right",
        icon="mdi:car-door-lock",
        device_class=BinarySensorDeviceClass.LOCK,
        is_on_fn=lambda data: (
            data.status.door_lock_passenger_rear == 0
            if data.status.door_lock_passenger_rear is not None
            else False
        ),
    ),
    SmartBinarySensorEntityDescription(
        key="trunk_locked",
        translation_key="trunk_locked",
        icon="mdi:car-back",
        device_class=BinarySensorDeviceClass.LOCK,
        is_on_fn=lambda data: (
            data.status.trunk_locked == 0
            if data.status.trunk_locked is not None
            else False
        ),
    ),
    SmartBinarySensorEntityDescription(
        key="engine_hood",
        translation_key="engine_hood",
        icon="mdi:car",
        device_class=BinarySensorDeviceClass.OPENING,
        is_on_fn=lambda data: data.status.engine_hood_open,
    ),
    SmartBinarySensorEntityDescription(
        key="electric_park_brake",
        translation_key="electric_park_brake",
        icon="mdi:car-brake-parking",
        is_on_fn=lambda data: data.status.electric_park_brake,
    ),
    SmartBinarySensorEntityDescription(
        key="tank_flap",
        translation_key="tank_flap",
        icon="mdi:gas-station",
        device_class=BinarySensorDeviceClass.OPENING,
        is_on_fn=lambda data: data.status.tank_flap_open,
    ),
    SmartBinarySensorEntityDescription(
        key="srs_crash",
        translation_key="srs_crash",
        icon="mdi:car-emergency",
        device_class=BinarySensorDeviceClass.SAFETY,
        entity_category=EntityCategory.DIAGNOSTIC,
        is_on_fn=lambda data: data.status.srs_crash,
    ),
    SmartBinarySensorEntityDescription(
        key="seatbelt_driver",
        translation_key="seatbelt_driver",
        icon="mdi:seatbelt",
        is_on_fn=lambda data: data.status.seatbelt_driver,
    ),
    SmartBinarySensorEntityDescription(
        key="seatbelt_passenger",
        translation_key="seatbelt_passenger",
        icon="mdi:seatbelt",
        is_on_fn=lambda data: data.status.seatbelt_passenger,
    ),
    SmartBinarySensorEntityDescription(
        key="seatbelt_rear_left",
        translation_key="seatbelt_rear_left",
        icon="mdi:seatbelt",
        entity_registry_enabled_default=False,
        is_on_fn=lambda data: data.status.seatbelt_rear_left,
    ),
    SmartBinarySensorEntityDescription(
        key="seatbelt_rear_right",
        translation_key="seatbelt_rear_right",
        icon="mdi:seatbelt",
        entity_registry_enabled_default=False,
        is_on_fn=lambda data: data.status.seatbelt_rear_right,
    ),
    SmartBinarySensorEntityDescription(
        key="seatbelt_rear_middle",
        translation_key="seatbelt_rear_middle",
        icon="mdi:seatbelt",
        entity_registry_enabled_default=False,
        is_on_fn=lambda data: data.status.seatbelt_rear_middle,
    ),
    SmartBinarySensorEntityDescription(
        key="charge_lid_ac",
        translation_key="charge_lid_ac",
        icon="mdi:ev-plug-type2",
        device_class=BinarySensorDeviceClass.OPENING,
        is_on_fn=lambda data: data.status.charge_lid_ac_open,
    ),
    SmartBinarySensorEntityDescription(
        key="charge_lid_dc",
        translation_key="charge_lid_dc",
        icon="mdi:ev-plug-ccs2",
        device_class=BinarySensorDeviceClass.OPENING,
        is_on_fn=lambda data: data.status.charge_lid_dc_open,
    ),
    # ── Climate Status ────────────────────────────────────────────────
    SmartBinarySensorEntityDescription(
        key="pre_climate_active",
        translation_key="pre_climate_active",
        icon="mdi:air-conditioner",
        device_class=BinarySensorDeviceClass.RUNNING,
        is_on_fn=lambda data: data.status.pre_climate_active,
    ),
    SmartBinarySensorEntityDescription(
        key="defrost_active",
        translation_key="defrost_active",
        icon="mdi:snowflake-melt",
        device_class=BinarySensorDeviceClass.RUNNING,
        is_on_fn=lambda data: data.status.defrost_active,
    ),
    SmartBinarySensorEntityDescription(
        key="air_blower_active",
        translation_key="air_blower_active",
        icon="mdi:fan",
        device_class=BinarySensorDeviceClass.RUNNING,
        is_on_fn=lambda data: data.status.air_blower_active,
    ),
    SmartBinarySensorEntityDescription(
        key="climate_overheat_protection",
        translation_key="climate_overheat_protection",
        icon="mdi:thermometer-alert",
        device_class=BinarySensorDeviceClass.RUNNING,
        is_on_fn=lambda data: data.status.climate_overheat_protection,
    ),
    SmartBinarySensorEntityDescription(
        key="sunroof_open",
        translation_key="sunroof_open",
        icon="mdi:window-open-variant",
        device_class=BinarySensorDeviceClass.OPENING,
        is_on_fn=lambda data: data.status.sunroof_open,
    ),
    SmartBinarySensorEntityDescription(
        key="sun_curtain_rear_open",
        translation_key="sun_curtain_rear_open",
        icon="mdi:curtains",
        device_class=BinarySensorDeviceClass.OPENING,
        entity_registry_enabled_default=False,
        is_on_fn=lambda data: data.status.sun_curtain_rear_open,
    ),
    SmartBinarySensorEntityDescription(
        key="curtain_open",
        translation_key="curtain_open",
        icon="mdi:curtains",
        device_class=BinarySensorDeviceClass.OPENING,
        entity_registry_enabled_default=False,
        is_on_fn=lambda data: data.status.curtain_open,
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
