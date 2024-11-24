"""Constants used by the Pterodactyl integration."""
from homeassistant.const import Platform

PLATFORMS = [
    Platform.SENSOR,
]

DOMAIN = "pterodactyl"

DEFAULT_HOST = "10.0.0.1"

DEFAULT_DEVICE_NAME = "Pterodactyl"
DEFAULT_SSL = False
DEFAULT_SSL_VERIFY = True

CONF_NAME= "name"
CONF_SCAN_INTERVAL="scan_interval"
CONF_HOST= "host"
CONF_API_KEY= "api"

CONF_NAME_DEFAULT= "Pterodactyl"
CONF_HOST_DEFAULT= "https://pterodactyl.example.org"
CONF_API_KEY_DEFAULT= "ptlc_...."
CONF_SCAN_INTERVAL_DEFAULT= 30