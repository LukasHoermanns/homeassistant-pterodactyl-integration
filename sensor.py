import logging

from homeassistant.helpers.entity import EntityCategory
from homeassistant.helpers.update_coordinator import CoordinatorEntity
from homeassistant.components.sensor import SensorEntity
from homeassistant.const import STATE_ON, STATE_OFF, STATE_UNAVAILABLE, UnitOfInformation, UnitOfTime
from homeassistant.core import HomeAssistant

from .pterodactyl_config_entry import PterodactylConfigEntry
from .coordinator import PterodactylDataCoordinator
from .game_server import GameServer


_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(hass: HomeAssistant, entry: PterodactylConfigEntry, async_add_entities):
    coordinator = entry.runtime_data.coordinator
    sensors = []
    for game_server in entry.runtime_data.game_server_list:
        sensor = GameServerStateSensor(coordinator, game_server)
        sensors.append(sensor)
        game_server.add_sensor(sensor)
        sensors.append(GameServerCpuUsageSensor(coordinator, game_server))
        sensors.append(GameServerRamUsageSensor(coordinator, game_server))
        sensors.append(GameServerDiskUsageSensor(coordinator, game_server))
        sensors.append(GameServerNetworkDownloadSensor(
            coordinator, game_server))
        sensors.append(GameServerNetworkUploadSensor(coordinator, game_server))
        sensors.append(GameServerUpTimeSensor(coordinator, game_server))
    async_add_entities(sensors)


class GameServerSensor(CoordinatorEntity, SensorEntity):
    def __init__(self, coordinator: PterodactylDataCoordinator, game_server: GameServer, type: str):
        super().__init__(coordinator)
        self._attr_name = f"{game_server.name} {type}"
        self._attr_unique_id = f"{game_server.identifyer}_{
            type.replace(" ", "_").lower()}"
        self._game_server = game_server
        self._attr_device_info = game_server.device_info

    @property
    def entity_category(self):
        return EntityCategory.DIAGNOSTIC


class GameServerStateSensor(GameServerSensor):
    def __init__(self, coordinator: PterodactylDataCoordinator, game_server: GameServer):
        super().__init__(coordinator, game_server, "State")

    @property
    def state(self):
        return self._game_server.state

    @property
    def extra_state_attributes(self):
        """
        Return additional state attributes.
        """
        return {
            "id": self._game_server.id,
            "identifyer": self._game_server.identifyer,
            "description": self._game_server.description
        }


class GameServerCpuUsageSensor(GameServerSensor):
    def __init__(self, coordinator: PterodactylDataCoordinator, game_server: GameServer):
        super().__init__(coordinator, game_server, "CPU usage")
        self._attr_icon = "mdi:cpu-64-bit"

    @property
    def state(self):
        cpu_usage = self._game_server.cpu_usage
        if cpu_usage is None:
            return STATE_UNAVAILABLE
        return float(round(cpu_usage, 2))

    @property
    def unit_of_measurement(self):
        return "%"

    @property
    def state_class(self):
        return "measurement"


class GameServerRamUsageSensor(GameServerSensor):
    def __init__(self, coordinator: PterodactylDataCoordinator, game_server: GameServer):
        super().__init__(coordinator, game_server, "RAM usage")
        self._attr_icon = "mdi:memory"

    @property
    def state(self):
        memory_usage = self._game_server.memory_usage
        return get_gb_value(memory_usage, 2)

    @property
    def unit_of_measurement(self):
        return UnitOfInformation.GIGABYTES


class GameServerDiskUsageSensor(GameServerSensor):
    def __init__(self, coordinator: PterodactylDataCoordinator, game_server: GameServer):
        super().__init__(coordinator, game_server, "Disk usage")
        self._attr_icon = "mdi:harddisk"

    @property
    def state(self):
        disk_usage = self._game_server.disk_usage
        return get_gb_value(disk_usage, 2)

    @property
    def unit_of_measurement(self):
        return UnitOfInformation.GIGABYTES


class GameServerNetworkDownloadSensor(GameServerSensor):
    def __init__(self, coordinator: PterodactylDataCoordinator, game_server: GameServer):
        super().__init__(coordinator, game_server, "Network download")
        self._attr_icon = "mdi:download"

    @property
    def state(self):
        download = self._game_server.network_rx
        return get_gb_value(download, 3)

    @property
    def unit_of_measurement(self):
        return UnitOfInformation.GIGABYTES


class GameServerNetworkUploadSensor(GameServerSensor):
    def __init__(self, coordinator: PterodactylDataCoordinator, game_server: GameServer):
        super().__init__(coordinator, game_server, "Network upload")
        self._attr_icon = "mdi:upload"

    @property
    def state(self):
        upload = self._game_server.network_tx
        return get_gb_value(upload, 3)

    @property
    def unit_of_measurement(self):
        return UnitOfInformation.GIGABYTES


class GameServerUpTimeSensor(GameServerSensor):
    def __init__(self, coordinator: PterodactylDataCoordinator, game_server: GameServer):
        super().__init__(coordinator, game_server, "Uptime")
        self._attr_icon = "mdi:timer"

    @property
    def state(self):
        uptime = self._game_server.uptime
        if uptime is None:
            return STATE_UNAVAILABLE
        return round(uptime / 1000)

    @property
    def unit_of_measurement(self):
        return UnitOfTime.SECONDS

    @property
    def device_class(self):
        return "duration"


def get_gb_value(value, dezimal: int):
    if value is None:
        return STATE_UNAVAILABLE
    return f"{value / (1024 ** 3):.{dezimal}f}"
