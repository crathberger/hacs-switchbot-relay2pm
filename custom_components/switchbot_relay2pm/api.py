"""SwitchBot API v1.1 client."""
from __future__ import annotations

import base64
import hashlib
import hmac
import logging
import time
import uuid

import aiohttp

_LOGGER = logging.getLogger(__name__)

API_BASE = "https://api.switch-bot.com/v1.1"


class SwitchBotAuthError(Exception):
    """Raised when authentication fails."""


class SwitchBotAPIError(Exception):
    """Raised when the API returns an error."""


class SwitchBotAPI:
    """Async SwitchBot API v1.1 client."""

    def __init__(self, token: str, secret: str, session: aiohttp.ClientSession) -> None:
        self._token = token
        self._secret = secret
        self._session = session

    def _get_headers(self) -> dict:
        nonce = str(uuid.uuid4())
        t = int(round(time.time() * 1000))
        string_to_sign = f"{self._token}{t}{nonce}"
        sign = base64.b64encode(
            hmac.new(
                bytes(self._secret, "utf-8"),
                msg=bytes(string_to_sign, "utf-8"),
                digestmod=hashlib.sha256,
            ).digest()
        ).decode("utf-8")
        return {
            "Authorization": self._token,
            "Content-Type": "application/json",
            "charset": "utf8",
            "t": str(t),
            "sign": sign,
            "nonce": nonce,
        }

    async def _request(self, method: str, path: str, **kwargs) -> dict:
        url = f"{API_BASE}{path}"
        try:
            async with self._session.request(
                method, url, headers=self._get_headers(), **kwargs
            ) as resp:
                if resp.status == 401:
                    raise SwitchBotAuthError("Invalid token or secret")
                resp.raise_for_status()
                data = await resp.json()
                if data.get("statusCode") == 401:
                    raise SwitchBotAuthError("Invalid token or secret")
                if data.get("statusCode") not in (100, 200):
                    raise SwitchBotAPIError(
                        f"API error {data.get('statusCode')}: {data.get('message', 'unknown')}"
                    )
                return data.get("body", {})
        except aiohttp.ClientError as err:
            raise SwitchBotAPIError(f"Connection error: {err}") from err

    async def get_devices(self) -> list[dict]:
        body = await self._request("GET", "/devices")
        return body.get("deviceList", [])

    async def get_relay2pm_devices(self) -> list[dict]:
        devices = await self.get_devices()
        return [d for d in devices if d.get("deviceType") == "Relay Switch 2PM"]

    async def get_device_status(self, device_id: str) -> dict:
        return await self._request("GET", f"/devices/{device_id}/status")

    async def send_command(
        self, device_id: str, command: str, parameter: str = "default"
    ) -> dict:
        payload = {
            "command": command,
            "parameter": parameter,
            "commandType": "command",
        }
        return await self._request("POST", f"/devices/{device_id}/commands", json=payload)

    async def set_position(self, device_id: str, position: int) -> dict:
        """Set roller blind position. 0=fully open, 100=fully closed (SwitchBot convention)."""
        return await self.send_command(device_id, "setPosition", str(position))

    async def validate_credentials(self) -> bool:
        try:
            await self.get_devices()
            return True
        except SwitchBotAuthError:
            raise
        except Exception:
            return False
