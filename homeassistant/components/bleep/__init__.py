"""Support for HA bleep (BLE ePaper)."""

from homeassistant import core
import homeassistant.helpers.config_validation as cv
from homeassistant.helpers.typing import ConfigType

DOMAIN = "bleep"
CONFIG_SCHEMA = cv.empty_config_schema(DOMAIN)


async def async_setup(hass: core.HomeAssistant, config: ConfigType) -> bool:
    """Set up the HA bleep (BLE ePaper) component."""
    # @TODO: Add setup code.
    return True
