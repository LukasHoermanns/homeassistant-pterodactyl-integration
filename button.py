import asyncio
import logging

from homeassistant.helpers.entity import EntityCategory
from homeassistant.core import HomeAssistant
from homeassistant.components.button import (
    ButtonEntity,
    ButtonEntityDescription,
)

from .pterodactyl_config_entry import PterodactylConfigEntry
from .coordinator import PterodactylDataCoordinator
from .game_server import GameServer

_LOGGER = logging.getLogger(__name__)

STOP_BUTTON_DESCRIPTION = ButtonEntityDescription(
    key="stop",
    icon="mdi:stop",
    translation_key="stop",
    entity_category=EntityCategory.CONFIG,
)
START_BUTTON_DESCRIPTION = ButtonEntityDescription(
    key="start",
    icon="mdi:play",
    translation_key="start",
    entity_category=EntityCategory.CONFIG,
)


async def async_setup_entry(hass: HomeAssistant, entry: PterodactylConfigEntry, async_add_entities):
    coordinator = entry.runtime_data.coordinator
    buttons = []

    for game_server in entry.runtime_data.game_server_list:
        buttons.append(PterodactylStartButton(coordinator, game_server))
        buttons.append(PterodactylStopButton(coordinator, game_server))
    async_add_entities(buttons)


class PterodactylButton(ButtonEntity):
    def __init__(
            self,
            coordinator: PterodactylDataCoordinator,
            game_server: GameServer
    ) -> None:
       # super().__init__(coordinator)
        self.coordinator = coordinator
        self.game_server = game_server
        self._attr_unique_id = (
            f"{game_server.identifyer}_{
                self.entity_description.translation_key}"
        )
        self._attr_device_info = game_server.device_info

    async def poll_server_until_status_Changed(self, state: str):
        last_state = self.game_server.state
        for _ in range(20):
            await self.game_server.update_data()
            if self.game_server.state != last_state:
                self.game_server.update_all_sensors()
                last_state = self.game_server.state
                _LOGGER.debug(f"State changed to {last_state}")

            if self.game_server.state == state:
                _LOGGER.debug("Break, new status reached")
                break

            await asyncio.sleep(2)


class PterodactylStartButton(PterodactylButton):
    def __init__(self, coordinator, game_server):
        super().__init__(coordinator, game_server)

    entity_description = START_BUTTON_DESCRIPTION

    @property
    def available(self) -> bool:
        # TODO: return available state
        return True

    async def async_press(self) -> None:
        identifier = self.game_server.identifyer
        await self.coordinator.apiHandler.start_server(identifier)
        await self.poll_server_until_status_Changed("running")


class PterodactylStopButton(PterodactylButton):
    def __init__(self, coordinator, game_server):
        super().__init__(coordinator, game_server)

    entity_description = STOP_BUTTON_DESCRIPTION

    @property
    def available(self) -> bool:
        # TODO: return available state
        return True

    async def async_press(self) -> None:
        identifier = self.game_server.identifyer
        await self.coordinator.apiHandler.stop_server(identifier)
        await self.poll_server_until_status_Changed("offline")
