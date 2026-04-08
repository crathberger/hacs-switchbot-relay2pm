"""Config flow for SwitchBot Relay Switch 2PM."""
from __future__ import annotations

import logging
from typing import Any

import voluptuous as vol

from homeassistant.config_entries import ConfigFlow, ConfigFlowResult
from homeassistant.helpers.aiohttp_client import async_get_clientsession

from .api import SwitchBotAPI, SwitchBotAuthError, SwitchBotAPIError
from .const import CONF_DEVICE_ID, CONF_DEVICE_NAME, CONF_SECRET, CONF_TOKEN, DOMAIN

_LOGGER = logging.getLogger(__name__)

STEP_CREDENTIALS_SCHEMA = vol.Schema(
    {
        vol.Required(CONF_TOKEN): str,
        vol.Required(CONF_SECRET): str,
    }
)


class SwitchBotRelay2PMConfigFlow(ConfigFlow, domain=DOMAIN):
    """Handle config flow for SwitchBot Relay Switch 2PM."""

    VERSION = 1

    def __init__(self) -> None:
        self._token: str = ""
        self._secret: str = ""
        self._devices: list[dict] = []

    async def async_step_user(
        self, user_input: dict[str, Any] | None = None
    ) -> ConfigFlowResult:
        """Step 1: Ask for token + secret."""
        errors: dict[str, str] = {}

        if user_input is not None:
            self._token = user_input[CONF_TOKEN].strip()
            self._secret = user_input[CONF_SECRET].strip()

            session = async_get_clientsession(self.hass)
            api = SwitchBotAPI(self._token, self._secret, session)

            try:
                self._devices = await api.get_relay2pm_devices()
            except SwitchBotAuthError:
                errors["base"] = "invalid_auth"
            except SwitchBotAPIError:
                errors["base"] = "cannot_connect"
            except Exception:
                _LOGGER.exception("Unexpected error during credential validation")
                errors["base"] = "unknown"
            else:
                if not self._devices:
                    errors["base"] = "no_devices_found"
                elif len(self._devices) == 1:
                    # Auto-select single device
                    device = self._devices[0]
                    return await self._create_entry(device)
                else:
                    return await self.async_step_select_device()

        return self.async_show_form(
            step_id="user",
            data_schema=STEP_CREDENTIALS_SCHEMA,
            errors=errors,
            description_placeholders={
                "app_url": "SwitchBot App → Profil → Entwickleroptionen"
            },
        )

    async def async_step_select_device(
        self, user_input: dict[str, Any] | None = None
    ) -> ConfigFlowResult:
        """Step 2: Select which Relay Switch 2PM to add."""
        if user_input is not None:
            device_id = user_input[CONF_DEVICE_ID]
            device = next(d for d in self._devices if d["deviceId"] == device_id)
            return await self._create_entry(device)

        device_options = {
            d["deviceId"]: f"{d['deviceName']} ({d['deviceId']})"
            for d in self._devices
        }

        return self.async_show_form(
            step_id="select_device",
            data_schema=vol.Schema(
                {vol.Required(CONF_DEVICE_ID): vol.In(device_options)}
            ),
        )

    async def _create_entry(self, device: dict) -> ConfigFlowResult:
        device_id = device["deviceId"]
        device_name = device["deviceName"]

        await self.async_set_unique_id(device_id)
        self._abort_if_unique_id_configured()

        return self.async_create_entry(
            title=device_name,
            data={
                CONF_TOKEN: self._token,
                CONF_SECRET: self._secret,
                CONF_DEVICE_ID: device_id,
                CONF_DEVICE_NAME: device_name,
            },
        )
