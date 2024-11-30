from homeassistant.config_entries import ConfigEntry
from typing import TYPE_CHECKING, List, Any
from dataclasses import dataclass, field

if TYPE_CHECKING:
    from .game_server import GameServer
    from .coordinator import PterodactylDataCoordinator


type PterodactylConfigEntry = ConfigEntry[PterodactylData]


@dataclass
class PterodactylData:
    coordinator: "PterodactylDataCoordinator"
    game_server_list: List["GameServer"] = field(default_factory=list)
    other_data: dict[str, Any] = field(default_factory=dict)
