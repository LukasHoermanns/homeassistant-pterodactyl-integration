from homeassistant.config_entries import CONN_CLASS_LOCAL_POLL, ConfigFlow, OptionsFlow
from homeassistant import config_entries
from homeassistant.core import callback
from .const import (
    CONF_HOST,
    CONF_API_KEY,
    CONF_HOST_DEFAULT,
    CONF_API_KEY_DEFAULT,
    CONF_UPDATE_INTERVAL,
    CONF_UPDATE_INTERVAL_DEFAULT,
    DEFAULT_DEVICE_NAME,
    DOMAIN
)

from typing import Any
import voluptuous as vol


@config_entries.HANDLERS.register(DOMAIN)
class PterodactylConfigFlow(ConfigFlow, domain=DOMAIN):
    """Handle a config flow for Pterodactyl."""
    VERSION = 1
    CONNECTION_CLASS = CONN_CLASS_LOCAL_POLL

    @staticmethod
    @callback
    def async_get_options_flow(config_entry):
        """Jellyfin options callback."""
        return PterodactylOptionsFlowHandler(config_entry)

    def __init__(self):
        self._errors = {}

    async def async_step_user(self, user_input=None):
        self._errors = {}

        if user_input is None:
            return await self._show_config_form()

        return await self._handle_user_input(user_input)

    async def _handle_user_input(self, user_input):
        valid = self._validate_user_input(user_input)
        if valid:
            return self._save_config_entry(user_input)
        else:
            await self._show_config_form()

    def _validate_user_input(self, user_input) -> bool:
        if self._validate_server_url(user_input[CONF_HOST]) == False:
            return False

        if self._validate_api_key(user_input[CONF_API_KEY]) == False:
            return False
        return True

    def _validate_server_url(self, url: str) -> bool:
        if url.endswith("/"):
            url = url.removesuffix("/")

        if not url.startswith("https://"):
            self._errors["host"] = "Host url needs to start with https://. http is not supported"
            return False
        return True

    def _validate_api_key(self, api_key: str) -> bool:
        if api_key.startswith("ptla_"):
            self._errors["api_key"] = "Dont use application API key. You need to use an accoutn Api key"
            return False

        if not api_key.startswith("ptlc_"):
            self._errors["api_key"] = "Valid API keys starts with ptlc_"
            return False
        return True

    def _save_config_entry(self, user_input):
        return self.async_create_entry(
            title=DEFAULT_DEVICE_NAME,
            data=user_input
        )

    async def _show_config_form(self):
        """Show the configuration form."""
        return self.async_show_form(
            step_id="user",
            data_schema=vol.Schema(
                {
                    vol.Required(CONF_HOST, default=CONF_HOST_DEFAULT): str,
                    vol.Required(CONF_API_KEY, default=CONF_API_KEY_DEFAULT): str,
                    vol.Optional(CONF_UPDATE_INTERVAL, default=CONF_UPDATE_INTERVAL_DEFAULT): int
                }
            ),
            errors=self._errors
        )


class PterodactylOptionsFlowHandler(OptionsFlow):
    def __init__(self, config_entry):
        """Init PterodactylOptionsFlowHandler."""
        self._errors = {}
        self.config_entry = config_entry
        self.options = dict(config_entry.options)

    async def async_step_init(self, user_input: dict[str, Any] | None = None):
        return await self.async_step_user(user_input)

    async def async_step_user(self, user_input=None):
        self._errors = {}

        if user_input is None:
            data_schema = {
                vol.Required(
                    CONF_HOST, default=self.config_entry.options.get(
                        CONF_HOST, self.config_entry.data.get(CONF_HOST))
                ): str,
                vol.Required(
                    CONF_API_KEY, default=self.config_entry.options.get(
                        CONF_API_KEY, self.config_entry.data.get(CONF_API_KEY))
                ): str,
                vol.Optional(
                    CONF_UPDATE_INTERVAL, default=self.config_entry.options.get(
                        CONF_UPDATE_INTERVAL, self.config_entry.data.get(CONF_UPDATE_INTERVAL))
                ): int,
            }

            return self.async_show_form(
                step_id="user",
                data_schema=vol.Schema(data_schema),
                errors=self._errors,
            )

        return self.async_create_entry(data=user_input)
