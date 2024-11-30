import asyncio
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator
from homeassistant.core import HomeAssistant


from .pterodactyl_api import PterodactylApi
from .game_server import GameServer
from homeassistant.config_entries import ConfigEntry

from datetime import timedelta
import logging
import inspect
import math
from typing import TYPE_CHECKING, List

from .pterodactyl_config_entry import PterodactylConfigEntry

from .const import (
    CONF_HOST,
    CONF_API_KEY,
    CONF_UPDATE_INTERVAL
)

_LOGGER = logging.getLogger(__name__)


class PterodactylDataCoordinator(DataUpdateCoordinator):
    data: List[GameServer] = []

    def __init__(self, hass: HomeAssistant, config_entry: PterodactylConfigEntry):
        host = config_entry.data[CONF_HOST]
        api_key = config_entry.data[CONF_API_KEY]
        self.config_entry = config_entry

        self.apiHandler = PterodactylApi(host, api_key)

        super().__init__(
            hass,
            _LOGGER,
            name="APIServerDataUpdateCoordinator",
            update_interval=timedelta(
                seconds=config_entry.data[CONF_UPDATE_INTERVAL])
        )

    async def _async_update_data(self):
        _LOGGER.debug(f"Pterodactyl Coordinator update {
                      len(self.config_entry.runtime_data.game_server_list)}")
        for game_server in self.config_entry.runtime_data.game_server_list:
            await game_server.update_data()

    async def create_server(self) -> List[GameServer]:
        game_server = []
        server_response = await self.apiHandler.get_all_servers()
        for server in server_response.get("data"):
            if server != "object":
                gameServer = GameServer(server, self.apiHandler)
                game_server.append(gameServer)
        _LOGGER.debug(f"created {len(game_server)} gameservers")
        return game_server
