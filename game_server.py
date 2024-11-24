from .const import DOMAIN
import json
import asyncio
from .pterodactyl_api import PterodactylApi
import logging

_LOGGER = logging.getLogger(__name__)

JSON_ATTRIBUTES = "attributes"
JSON_IDENTIFIER = "identifier"

JSON_DESCRIPTION = "description"
JSON_UUID = "uuid"
JSON_ID = "id"

JSON_STATE = "current_state"
JSON_RESOURCES = "resources"


class GameServer():
    state: str = None
    cpu_usage: str = None
    cpu_usage: str = None
    stamemory_usagete: str = None
    uptime: str = None
    network_rx: str = None
    network_tx: str = None

    def __init__(self, api_response_json, api: PterodactylApi):

        if api_response_json == None:
            _LOGGER.error("got None for Server creation from Json")
            return

        self.api: PterodactylApi = api
        self.identifyer = api_response_json[JSON_ATTRIBUTES][JSON_IDENTIFIER]
        self.name = api_response_json[JSON_ATTRIBUTES]["name"]
        self.description = api_response_json[JSON_ATTRIBUTES][JSON_DESCRIPTION]
        self.uuid = api_response_json[JSON_ATTRIBUTES][JSON_UUID]
        self.id = api_response_json[JSON_ATTRIBUTES][JSON_ID]
        self.state = "unknown"

        _LOGGER.debug("load server default data")

        if self.identifyer != None:
            asyncio.create_task(self.load_resources())
        else:
            _LOGGER.error("identify None, but expected correct value")

    async def load_resources(self):
        json_resources = await self.api.get_server_resources(self.identifyer)

        _LOGGER.debug("getServerResources data: %s",
                      json.dumps(json_resources, indent=2))
        _LOGGER.debug("load state data")

        self.state = json_resources[JSON_ATTRIBUTES][JSON_STATE]
        self.cpu_usage = json_resources[JSON_ATTRIBUTES][JSON_RESOURCES]["cpu_absolute"]
        self.memory_usage = json_resources[JSON_ATTRIBUTES][JSON_RESOURCES]["memory_bytes"]
        self.disc_usage = json_resources[JSON_ATTRIBUTES][JSON_RESOURCES]["disk_bytes"]
        self.uptime = json_resources[JSON_ATTRIBUTES][JSON_RESOURCES]["uptime"]
        self.network_rx = json_resources[JSON_ATTRIBUTES][JSON_RESOURCES]["network_rx_bytes"]
        self.network_tx = json_resources[JSON_ATTRIBUTES][JSON_RESOURCES]["network_tx_bytes"]

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
