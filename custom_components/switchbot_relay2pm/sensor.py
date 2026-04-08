"""Sensor entities for SwitchBot Relay Switch 2PM (power monitoring)."""
from __future__ import annotations

from dataclasses import dataclass
from typing import Callable

from homeassistant.components.sensor import (
    SensorDeviceClass,
    SensorEntity,
    SensorEntityDescription,
    SensorStateClass,
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import UnitOfElectricCurrent, UnitOfElectricPotential, UnitOfPower
from homeassistant.core import HomeAssistant
from homeassistant.helpers.device_registry import DeviceInfo
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity, DataUpdateCoordinator

from .api import SwitchBotAPI
from .const import CONF_DEVICE_ID, CONF_DEVICE_NAME, DOMAIN


@dataclass(frozen=True, kw_only=True)
class SwitchBotSensorDescription(SensorEntityDescription):
    value_fn: Callable[[dict], float | int | str | None]


SENSORS: tuple[SwitchBotSensorDescription, ...] = (
    SwitchBotSensorDescription(
        key="switch1_power",
        name="Kanal 1 Leistung",
        device_class=SensorDeviceClass.POWER,
        state_class=SensorStateClass.MEASUREMENT,
        native_unit_of_measurement=UnitOfPower.WATT,
        suggested_display_precision=1,
        value_fn=lambda d: d.get("switch1Power"),
    ),
    SwitchBotSensorDescription(
        key="switch2_power",
        name="Kanal 2 Leistung",
        device_class=SensorDeviceClass.POWER,
        state_class=SensorStateClass.MEASUREMENT,
        native_unit_of_measurement=UnitOfPower.WATT,
        suggested_display_precision=1,
        value_fn=lambda d: d.get("switch2Power"),
    ),
    SwitchBotSensorDescription(
        key="switch1_voltage",
        name="Kanal 1 Spannung",
        device_class=SensorDeviceClass.VOLTAGE,
        state_class=SensorStateClass.MEASUREMENT,
        native_unit_of_measurement=UnitOfElectricPotential.VOLT,
        suggested_display_precision=0,
        entity_registry_enabled_default=False,
        value_fn=lambda d: d.get("switch1Voltage"),
    ),
    SwitchBotSensorDescription(
        key="switch2_voltage",
        name="Kanal 2 Spannung",
        device_class=SensorDeviceClass.VOLTAGE,
        state_class=SensorStateClass.MEASUREMENT,
        native_unit_of_measurement=UnitOfElectricPotential.VOLT,
        suggested_display_precision=0,
        entity_registry_enabled_default=False,
        value_fn=lambda d: d.get("switch2Voltage"),
    ),
    SwitchBotSensorDescription(
        key="switch1_current",
        name="Kanal 1 Stromstärke",
        device_class=SensorDeviceClass.CURRENT,
        state_class=SensorStateClass.MEASUREMENT,
        native_unit_of_measurement=UnitOfElectricCurrent.MILLIAMPERE,
        suggested_display_precision=0,
        entity_registry_enabled_default=False,
        value_fn=lambda d: d.get("switch1ElectricCurrent"),
    ),
    SwitchBotSensorDescription(
        key="switch2_current",
        name="Kanal 2 Stromstärke",
        device_class=SensorDeviceClass.CURRENT,
        state_class=SensorStateClass.MEASUREMENT,
        native_unit_of_measurement=UnitOfElectricCurrent.MILLIAMPERE,
        suggested_display_precision=0,
        entity_registry_enabled_default=False,
        value_fn=lambda d: d.get("switch2ElectricCurrent"),
    ),
    SwitchBotSensorDescription(
        key="position",
        name="Position",
        state_class=SensorStateClass.MEASUREMENT,
        native_unit_of_measurement="%",
        suggested_display_precision=0,
        entity_registry_enabled_default=False,
        value_fn=lambda d: d.get("position"),
    ),
)


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    data = hass.data[DOMAIN][entry.entry_id]
    async_add_entities(
        SwitchBotRelay2PMSensor(
            coordinator=data["coordinator"],
            description=desc,
            device_id=data["device_id"],
            device_name=entry.data[CONF_DEVICE_NAME],
        )
        for desc in SENSORS
    )


class SwitchBotRelay2PMSensor(CoordinatorEntity, SensorEntity):
    """A sensor entity for SwitchBot Relay Switch 2PM."""

    _attr_has_entity_name = True

    def __init__(
        self,
        coordinator: DataUpdateCoordinator,
        description: SwitchBotSensorDescription,
        device_id: str,
        device_name: str,
    ) -> None:
        super().__init__(coordinator)
        self.entity_description = description
        self._attr_unique_id = f"{device_id}_{description.key}"
        self._attr_device_info = DeviceInfo(
            identifiers={(DOMAIN, device_id)},
            name=device_name,
            manufacturer="SwitchBot",
            model="Relay Switch 2PM",
        )

    @property
    def native_value(self) -> float | int | str | None:
        if self.coordinator.data is None:
            return None
        return self.entity_description.value_fn(self.coordinator.data)
