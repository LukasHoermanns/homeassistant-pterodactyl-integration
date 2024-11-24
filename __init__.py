"""The Pterodactyl integration."""
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
import logging

from .const import DOMAIN, PLATFORMS, CONF_HOST, CONF_API_KEY

from .coordinator import PterodactylDataCoordinator

_LOGGER = logging.getLogger(__name__)

# ---------------------------
#   async_setup_entry
# ---------------------------
async def async_setup_entry(hass: HomeAssistant, config_entry: ConfigEntry) -> bool:
    """Set up Pterodactyl integration from a config entry."""
    if DOMAIN not in hass.data:
        hass.data[DOMAIN] = {}

    coordinator = PterodactylDataCoordinator(hass, config_entry)
    await coordinator.async_config_entry_first_refresh()

    unsub_options_update_listener = config_entry.add_update_listener(_update_listener)

    hass.data[DOMAIN][config_entry.entry_id] = {
        "coordinator": coordinator,
        "unsub_options_update_listener": unsub_options_update_listener
    }

    # Verwende `async_forward_entry_setups`, um die Plattformen zu laden
    #hass.async_create_task(
    #    hass.config_entries.async_forward_entry_setups(config_entry, PLATFORMS)
    #)
    await hass.config_entries.async_forward_entry_setups(config_entry, PLATFORMS)

    config_entry.add_update_listener(_update_listener)
    return True


# ---------------------------
#   async_unload_entry
# ---------------------------
async def async_unload_entry(hass: HomeAssistant, config_entry: ConfigEntry) -> bool:
    """Unload a config entry."""
    if unload_ok := await hass.config_entries.async_unload_platforms(config_entry, PLATFORMS):
        entry_data = hass.data[DOMAIN].pop(config_entry.entry_id, None)

        if entry_data and "unsub_options_update_listener" in entry_data:
            entry_data["unsub_options_update_listener"]()

    return unload_ok


async def async_unload_entry(
        hass: HomeAssistant, entry: ConfigEntry
) -> bool:
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

