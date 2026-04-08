"""Cover entity for SwitchBot Relay Switch 2PM in roller blind mode."""
from __future__ import annotations

import logging

from homeassistant.components.cover import (
    CoverDeviceClass,
    CoverEntity,
    CoverEntityFeature,
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.device_registry import DeviceInfo
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity, DataUpdateCoordinator

from .api import SwitchBotAPI
from .const import CONF_DEVICE_ID, CONF_DEVICE_NAME, DOMAIN

_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    data = hass.data[DOMAIN][entry.entry_id]
    async_add_entities(
        [
            SwitchBotRelay2PMCover(
                coordinator=data["coordinator"],
                api=data["api"],
                device_id=data["device_id"],
                device_name=entry.data[CONF_DEVICE_NAME],
                entry_id=entry.entry_id,
            )
        ]
    )


class SwitchBotRelay2PMCover(CoordinatorEntity, CoverEntity):
    """SwitchBot Relay Switch 2PM as a roller blind cover entity."""

    _attr_device_class = CoverDeviceClass.SHUTTER
    _attr_supported_features = (
        CoverEntityFeature.OPEN
        | CoverEntityFeature.CLOSE
        | CoverEntityFeature.SET_POSITION
        | CoverEntityFeature.STOP
    )
    _attr_has_entity_name = True
    _attr_name = None  # Use device name as entity name

    def __init__(
        self,
        coordinator: DataUpdateCoordinator,
        api: SwitchBotAPI,
        device_id: str,
        device_name: str,
        entry_id: str,
    ) -> None:
        super().__init__(coordinator)
        self._api = api
        self._device_id = device_id
        self._device_name = device_name
        self._attr_unique_id = f"{device_id}_cover"
        self._attr_device_info = DeviceInfo(
            identifiers={(DOMAIN, device_id)},
            name=device_name,
            manufacturer="SwitchBot",
            model="Relay Switch 2PM",
        )

    @property
    def current_cover_position(self) -> int | None:
        """Return current position in HA convention: 0=closed, 100=open."""
        if self.coordinator.data is None:
            return None
        pos = self.coordinator.data.get("position")
        if pos is None:
            return None
        # SwitchBot: 0=open, 100=closed → invert for HA
        return 100 - int(pos)

    @property
    def is_closed(self) -> bool | None:
        pos = self.current_cover_position
        if pos is None:
            return None
        return pos == 0

    @property
    def is_opening(self) -> bool:
        return False  # SwitchBot API doesn't expose movement state

    @property
    def is_closing(self) -> bool:
        return False

    @property
    def extra_state_attributes(self) -> dict:
        if self.coordinator.data is None:
            return {}
        return {
            "calibrated": self.coordinator.data.get("calibrate"),
            "stuck": self.coordinator.data.get("isStuck"),
            "online": self.coordinator.data.get("online"),
        }

    async def async_open_cover(self, **kwargs) -> None:
        """Open the cover (SwitchBot position 0 = fully open)."""
        await self._api.set_position(self._device_id, 0)
        await self.coordinator.async_request_refresh()

    async def async_close_cover(self, **kwargs) -> None:
        """Close the cover (SwitchBot position 100 = fully closed)."""
        await self._api.set_position(self._device_id, 100)
        await self.coordinator.async_request_refresh()

    async def async_set_cover_position(self, **kwargs) -> None:
        """Set cover to a specific position (HA: 0=closed, 100=open)."""
        ha_position = kwargs["position"]
        sb_position = 100 - ha_position  # invert for SwitchBot convention
        await self._api.set_position(self._device_id, sb_position)
        await self.coordinator.async_request_refresh()

    async def async_stop_cover(self, **kwargs) -> None:
        """Stop cover movement by sending setPosition to current position."""
        current_sb_pos = None
        if self.coordinator.data is not None:
            current_sb_pos = self.coordinator.data.get("position")
        if current_sb_pos is not None:
            await self._api.set_position(self._device_id, int(current_sb_pos))
        await self.coordinator.async_request_refresh()
