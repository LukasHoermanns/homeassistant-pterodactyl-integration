"""The Pterodactyl integration."""
import logging

from dataclasses import dataclass
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from typing import TYPE_CHECKING, List, Any
from .game_server import GameServer
from .const import DOMAIN, PLATFORMS, CONF_HOST, CONF_API_KEY
from .coordinator import PterodactylDataCoordinator
from .pterodactyl_config_entry import PterodactylData


from .pterodactyl_config_entry import PterodactylConfigEntry

_LOGGER = logging.getLogger(__name__)
_UNSUB_LIST = "unsub_options_update_listener"

async def async_setup_entry(hass: HomeAssistant, config_entry: PterodactylConfigEntry) -> bool:
    """Set up Pterodactyl integration from a config entry."""
    if DOMAIN not in hass.data:
        hass.data[DOMAIN] = {}

    #_LOGGER.setLevel(logging.DEBUG)

    coordinator = PterodactylDataCoordinator(hass, config_entry)

    unsub_options_update_listener = config_entry.add_update_listener(
        _update_listener)
    hass.data[DOMAIN][config_entry.entry_id] = {
        "unsub_options_update_listener": unsub_options_update_listener
    }

    pterodactyl_data = PterodactylData(coordinator)
    pterodactyl_data.game_server_list = await coordinator.create_server()
    config_entry.runtime_data = pterodactyl_data

    await coordinator.async_config_entry_first_refresh()
    await hass.config_entries.async_forward_entry_setups(config_entry, PLATFORMS)
    config_entry.add_update_listener(_update_listener)
    return True


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Unload a config entry."""
    if unload_ok := await hass.config_entries.async_unload_platforms(entry, PLATFORMS):
        entry = hass.data[DOMAIN].pop(entry.entry_id, None)

        if entry and "unsub_options_update_listener" in entry:
            entry["unsub_options_update_listener"]()

    return unload_ok


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Unload a config entry."""
    if unload_ok := await hass.config_entries.async_unload_platforms(entry, PLATFORMS):
        # Remove config entry from domain.
        entry_data = hass.data[DOMAIN].pop(entry.entry_id)
        # Remove options_update_listener.
        entry_data["unsub_options_update_listener"]()

    return unload_ok


async def _update_listener(hass: HomeAssistant, config_entry):
    """Update listener."""
    await hass.config_entries.async_reload(config_entry.entry_id)
