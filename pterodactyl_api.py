import logging
import aiohttp
import json

from typing import Dict, Any

_LOGGER = logging.getLogger(__name__)


class PterodactylApi():
    def __init__(self, host, api_key):
        self.api_key = api_key
        self.host = host

    async def test_connection(self) -> bool:
        # TODO: verbindung testen
        return True

    async def get_all_servers(self) -> Dict[str, Any]:
        api_url = f"{self.host}/api/application/servers"
        return await self._api_request(api_url, self._get_headers())

    async def get_server_resources(self, identifier) -> Dict[str, Any]:
        api_url = f"{self.host}/api/client/servers/{identifier}/resources"
        return await self._api_request(api_url, self._get_headers())

    async def start_server(self, identifier) -> None:
        api_url = f"{
            self.host}/api/client/servers/{identifier}/power?signal=start"
        return await self._api_post(api_url, self._get_headers())

    async def stop_server(self, identifier) -> None:
        api_url = f"{
            self.host}/api/client/servers/{identifier}/power?signal=stop"
        return await self._api_post(api_url, self._get_headers())

    def _get_headers(self) -> Dict[str, str]:
        return {
            "Accept": "application/json",
            "Content-Type": "application/json",
            "Authorization": f"Bearer {self.api_key}"
        }

    async def _api_request(self, url: str, headers: Dict[str, str]) -> Dict[str, Any]:
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(url, headers=headers) as response:
                    return await self._parse_response(response)
        except aiohttp.ClientError as e:
            _LOGGER.error("Client error occurred during API request: %s", e)
        except Exception as e:
            _LOGGER.error(
                "Unexpected error occurred during API request: %s", e)
            return {}

    async def _api_post(self, url: str, headers: Dict[str, str]) -> None:
        try:
            async with aiohttp.ClientSession() as session:
                async with session.post(url, headers=headers) as response:
                    if response.status == 204:
                        return
                    else:
                        _LOGGER.error(
                            "Failed to fetch server data, status code: %s", response.status)
        except aiohttp.ClientError as e:
            _LOGGER.error("Client error occurred during API request: %s", e)
        except Exception as e:
            _LOGGER.error(
                "Unexpected error occurred during API request: %s", e)
            return {}

    async def _parse_response(self, response: aiohttp.ClientResponse) -> Dict[str, Any]:
        if response.status == 200:
            try:
                json_response = await response.json()
                _LOGGER.debug("Coordinator data: %s",
                              json.dumps(json_response, indent=2))
                return json_response
            except aiohttp.ContentTypeError:
                _LOGGER.error("Invalid content type received, expected JSON.")
        else:
            _LOGGER.error(
                "Failed to fetch server data, status code: %s", response.status)
        return {}
