import logging
from datetime import timedelta
from typing import TYPE_CHECKING, List

from homeassistant.components.sensor import SensorEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.update_coordinator import CoordinatorEntity
from homeassistant.const import STATE_ON, STATE_OFF

from .game_server import GameServer
from .coordinator import PterodactylDataCoordinator

from .pterodactyl_config_entry import PterodactylConfigEntry

from .const import DOMAIN

_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(hass: HomeAssistant, entry: PterodactylConfigEntry, async_add_entities):
    #coordinator : PterodactylDataCoordinator = hass.data[DOMAIN][entry.entry_id]["coordinator"]
    coordinator = entry.runtime_data.coordinator
    
    sensors = []
    for game_server in entry.runtime_data.game_server_list:
        sensor = APIServerSensor(coordinator, game_server)
        sensors.append(sensor)
        game_server.add_sensor(sensor)
    async_add_entities(sensors)


class APIServerSensor(CoordinatorEntity, SensorEntity):
    """
    Sensor entity that represents the status of a server.
    """

    def __init__(self, coordinator: PterodactylDataCoordinator, game_server: GameServer):
        super().__init__(coordinator)
        self._attr_name = f"Server Status: {game_server.name}"
        self._attr_unique_id = f"server_status_{game_server.identifyer}"
        self._game_server = game_server
        self._attr_device_info = game_server.device_info

    @property
    def state(self):
        """
        Return the state of the sensor.
        """
        return STATE_ON if self._game_server.state == "running" else STATE_OFF

    @property
    def extra_state_attributes(self):
        """
        Return additional state attributes.
        """
        return {
            "server_name": self._game_server.name,
            "id": self._game_server.id,
            "description": self._game_server.description,
            "state": self._game_server.state
        }
