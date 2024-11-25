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
from typing import List

from .const import (
    CONF_HOST,
    CONF_API_KEY,
    CONF_UPDATE_INTERVAL
)

_LOGGER = logging.getLogger(__name__)


class PterodactylDataCoordinator(DataUpdateCoordinator):
    game_servers: List[GameServer] = []

    def __init__(self, hass: HomeAssistant, config_entry: ConfigEntry):
        host = config_entry.data[CONF_HOST]
        api_key = config_entry.data[CONF_API_KEY]

        self.apiHandler = PterodactylApi(host, api_key)
        self.game_servers = self.create_server()

        super().__init__(
            hass,
            _LOGGER,
            name="APIServerDataUpdateCoordinator",
            update_interval=timedelta(
                seconds=config_entry.data[CONF_UPDATE_INTERVAL])
        )

    async def _calculate_update_interval(self, update_interval):
        if not self.game_servers:
            self.game_servers = await self.create_server()

        RATE_LIMIT = 240
        min_interval = 60 / (RATE_LIMIT / self.game_servers.count)
        min_interval = math.ceil(min_interval)

        if update_interval < min_interval:
            _LOGGER.warning(f"Scan Interval to Low. Rate Limit is 240/min. Every Server need one Api call, so minimum interval is {
                            min_interval} beacuse your server count is {self.game_servers.count} ")
            return min_interval
        return update_interval

    async def _async_update_data(self):
        if not self.game_servers:
            self.game_servers = await self.create_server()
        _LOGGER.debug("update triggerd")
        await self.update_servers()

    async def create_server(self) -> List[GameServer]:
        self.game_servers = []
        data = await self.apiHandler.get_all_servers()
        for server in data.get("data"):
            if server != "object":
                gameServer = GameServer(server, self.apiHandler)
                self.game_servers.append(gameServer)
        return self.game_servers

    async def update_servers(self):
        if inspect.isawaitable(self.game_servers):
            await self.game_servers

        for game_server in self.game_servers:
            await game_server.update_data()
