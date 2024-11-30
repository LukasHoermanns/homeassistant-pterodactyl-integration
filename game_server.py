import logging
import json
import asyncio

from typing import List, TYPE_CHECKING
if TYPE_CHECKING:
    from .sensor import APIServerSensor

from .pterodactyl_api import PterodactylApi
from .const import DOMAIN


_LOGGER = logging.getLogger(__name__)

JSON_DESCRIPTION = "description"
JSON_ATTRIBUTES = "attributes"
JSON_IDENTIFIER = "identifier"
JSON_STATE = "current_state"
JSON_RESOURCES = "resources"
JSON_UUID = "uuid"
JSON_NAME = "name"
JSON_ID = "id"


class GameServer():
    def __init__(self, api_response_json, api: PterodactylApi):
        if api_response_json == None:
            _LOGGER.error("got None for Server creation from Json")
            return

        self.api: PterodactylApi = api

        self.description = api_response_json[JSON_ATTRIBUTES][JSON_DESCRIPTION]
        self.identifyer = api_response_json[JSON_ATTRIBUTES][JSON_IDENTIFIER]
        self.name = api_response_json[JSON_ATTRIBUTES][JSON_NAME]
        self.uuid = api_response_json[JSON_ATTRIBUTES][JSON_UUID]
        self.id = api_response_json[JSON_ATTRIBUTES][JSON_ID]
        self.sensors: List["APIServerSensor"] = []
        self.state = "unknown"

        _LOGGER.debug("loaded server default data")

        if self.identifyer != None:
            asyncio.create_task(self.load_resources())
        else:
            _LOGGER.error("identify None, but expected correct value")

    def add_sensor(self, sensor: "APIServerSensor"):
        self.sensors.append(sensor)

    def update_all_sensors(self):
        for sensor in self.sensors:
            sensor.async_write_ha_state()

    async def load_resources(self):
        json_resources = await self.api.get_server_resources(self.identifyer)

        _LOGGER.debug("getServerResources data: %s",
                      json.dumps(json_resources, indent=2))

        self.state = json_resources[JSON_ATTRIBUTES][JSON_STATE]
        self.network_rx = json_resources[JSON_ATTRIBUTES][JSON_RESOURCES]["network_rx_bytes"]
        self.network_tx = json_resources[JSON_ATTRIBUTES][JSON_RESOURCES]["network_tx_bytes"]
        self.memory_usage = json_resources[JSON_ATTRIBUTES][JSON_RESOURCES]["memory_bytes"]
        self.cpu_usage = json_resources[JSON_ATTRIBUTES][JSON_RESOURCES]["cpu_absolute"]
        self.disc_usage = json_resources[JSON_ATTRIBUTES][JSON_RESOURCES]["disk_bytes"]
        self.uptime = json_resources[JSON_ATTRIBUTES][JSON_RESOURCES]["uptime"]

    async def update_data(self):
        await self.load_resources()

    @property
    def device_info(self):
        """
        Return the device information for the game server.
        """
        return {
            "identifiers": {(DOMAIN, self.uuid)},
            "name": self.name,
            "manufacturer": "Pterodactyl",
            "model": "Game Server",
        }
