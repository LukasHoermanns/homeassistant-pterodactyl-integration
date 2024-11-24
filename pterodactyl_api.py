import logging
import aiohttp
import json

_LOGGER = logging.getLogger(__name__)
class PterodactylApi():

    def __init__(self, host, api_key):
        self.host = host
        self.api_key = api_key
    
    def test_connection(self):
        #TODO: verbindung testen
        return True
    
    

    async def getAllServers(self):
        api_url = f"{self.host}/api/application/servers"
        headers = {
            "Accept": "application/json",
            "Content-Type": "application/json",
            "Authorization": f"Bearer {self.api_key}"
        }
        return await self.apiRequest(api_url, headers)
        

    async def getServerResources(self, identifier):
        api_url = f"{self.host}/api/client/servers/{identifier}/resources"
        headers = {
            "Accept": "application/json",
            "Content-Type": "application/json",
            "Authorization": f"Bearer {self.api_key}"
        }
        return await self.apiRequest(api_url, headers)

    
    async def apiRequest(self, url, headers):
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(url, headers=headers) as response:
                    if response.status == 200:
                        text = await response.json()
                        _LOGGER.debug("Coordinator data: %s", json.dumps(text, indent=2))
                        return text
                    else:
                        _LOGGER.error("Failed to fetch server data, status code: %s", response.status)
                        return None
        except Exception as e:
            _LOGGER.error("Error occurred during API request: %s", e)
            return None

