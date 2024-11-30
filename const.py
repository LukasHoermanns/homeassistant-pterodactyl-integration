"""Constants used by the Pterodactyl integration."""
from homeassistant.const import Platform

PLATFORMS = [
    Platform.SENSOR,
    Platform.BUTTON
]

DOMAIN = "pterodactyl"
DEFAULT_DEVICE_NAME = "Pterodactyl"

CONF_NAME = "name"
CONF_NAME_DEFAULT = "Pterodactyl"

CONF_HOST = "host"
CONF_HOST_DEFAULT = "https://pterodactyl.example.org"

CONF_API_KEY = "api_key"
CONF_API_KEY_DEFAULT = "ptlc_...."

CONF_UPDATE_INTERVAL = "update_interval"
CONF_UPDATE_INTERVAL_DEFAULT = 30
