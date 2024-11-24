from homeassistant.config_entries import CONN_CLASS_LOCAL_POLL, ConfigFlow, OptionsFlow
from homeassistant import config_entries
from homeassistant.core import callback
from .const import (
    CONF_HOST,
    CONF_API_KEY,
    CONF_HOST_DEFAULT,
    CONF_API_KEY_DEFAULT,
    CONF_SCAN_INTERVAL,
    CONF_SCAN_INTERVAL_DEFAULT,
    DOMAIN
)

from datetime import timedelta
from logging import getLogger
from typing import Any, List
import voluptuous as vol

_LOGGER = getLogger(__name__)

SCAN_INTERVAL = timedelta(seconds=30) 

@config_entries.HANDLERS.register(DOMAIN)
class PterodactylConfigFlow(ConfigFlow, domain=DOMAIN):
    """Handle a config flow for Pterodactyl."""
    VERSION = 1
    CONNECTION_CLASS = CONN_CLASS_LOCAL_POLL

    _invalid_config_reason: List[str]

    @staticmethod
    @callback
    def async_get_options_flow(config_entry):
        """Jellyfin options callback."""
        return PterodactylOptionsFlowHandler(config_entry)

    def __init__(self):
        self._errors = {}
        self._invalid_config_reason = []

    
    async def async_step_user(self, user_input=None):
        self._errors = {}
        if user_input is not None:
           return self._process_user_input(user_input)
        return await self._show_config_form()
    
    
    def _process_user_input(self, user_input):
        valid = self._validate_user_input(user_input)
        if (valid):
            return self._save_config_entry(user_input)
        else:
            return self.async_abort(reason=self._invalid_config_reason)


    def _validate_user_input(self, user_input) -> bool:
        if (self._validate_server_url(user_input[CONF_HOST]) == False):
            return False
        
        if (self._validate_api_key(user_input[CONF_API_KEY]) == False):
            return False
        return True
    

    def _validate_server_url(self, url: str) -> bool:
        if url.endswith("/"):
            url = url.removesuffix("/")
        
        if not url.startswith("https://"):
            self._invalid_config_reason.append("Host url needs to start with https://. http is not supported")
            return False
        return True
    

    def _validate_api_key(self, api_key: str):
        if api_key.startswith("ptla_"):
            self._invalid_config_reason.append("Dont use application API key. You need to use an accoutn Api key")
            return False

        if not api_key.startswith("ptlc_"):
            self._invalid_config_reason.append("Valid API keys starts with ptlc_")
            return False
        return True
    

    def _save_config_entry(self, user_input):
        return self.async_create_entry(
            title="title_test", 
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
                    vol.Optional(CONF_SCAN_INTERVAL, default=CONF_SCAN_INTERVAL_DEFAULT): int
                }
            ),
            errors=self._errors
        )

    @callback
    def _async_entry_for_username(self, username):
        """Find an existing entry for a username."""
        for entry in self._async_current_entries():
            # if entry.data.get(CONF_NPM_URL) == username:
            if entry.title == username:
                return entry
        return None


class PterodactylOptionsFlowHandler(OptionsFlow):
    def __init__(self, config_entry):
        """Init PterodactylOptionsFlowHandler."""
        self._errors = {}
        self.config_entry = config_entry
        self.options = dict(config_entry.options)

    async def async_step_init(self, user_input: dict[str, Any] | None = None):
        """Manage the options."""
        return await self.async_step_user(user_input)
    
    async def async_step_user(self, user_input=None):
        self._errors = {}

        if user_input is None:
            data_schema = {
                vol.Required(
                    CONF_HOST, default=self.config_entry.options.get(CONF_HOST, self.config_entry.data.get(CONF_HOST))
                ): str,
                vol.Required(
                    CONF_API_KEY, default=self.config_entry.options.get(CONF_API_KEY, self.config_entry.data.get(CONF_API_KEY))
                ): str,
                vol.Optional(
                    CONF_SCAN_INTERVAL, default=self.config_entry.options.get(CONF_SCAN_INTERVAL, self.config_entry.data.get(CONF_SCAN_INTERVAL))
                ): int,
            }
            
            return self.async_show_form(
            step_id="user",
            data_schema=vol.Schema(data_schema),
            errors=self._errors,
            )
    
        return self.async_create_entry(data=user_input)