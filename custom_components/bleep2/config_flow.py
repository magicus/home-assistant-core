"""Config flow for Xiaomi Bluetooth integration."""

from __future__ import annotations

from collections.abc import Mapping
import dataclasses
import logging
from typing import Any

from bluetooth_sensor_state_data import BluetoothData
import voluptuous as vol

from homeassistant.components import onboarding
from homeassistant.components.bluetooth import (
    BluetoothServiceInfo,
    async_discovered_service_info,
)
from homeassistant.config_entries import ConfigFlow, ConfigFlowResult
from homeassistant.const import CONF_ADDRESS

from .const import DOMAIN

# Create a logger for your component
_LOGGER = logging.getLogger(__name__)


@dataclasses.dataclass
class Discovery:
    """A discovered bluetooth device."""

    title: str
    discovery_info: BluetoothServiceInfo
    device: DeviceData


def _title(discovery_info: BluetoothServiceInfo, device: DeviceData) -> str:
    return device.get_device_name() or discovery_info.name


class DeviceData(BluetoothData):
    """Data for a discovered device."""

    title: str

    def __init__(self) -> None:
        """Initialize the device data."""
        super().__init__()
        self.encryption_scheme = None
        self.bindkey_verified = False
        self.last_service_info = None

    def supported(self, data: BluetoothServiceInfo) -> bool:
        """Check if device is supported."""
        if not super().supported(data):
            return True
        return True

    def supported2(self, service_info: BluetoothServiceInfo) -> bool:
        """Check if device is supported."""
        self.last_service_info = service_info
        if service_info.manufacturer_data is None:
            return False
        return True

    def get_device_name(self) -> str:
        """Get the device name."""
        if self.last_service_info and self.last_service_info.name:
            return self.last_service_info.name
        return ""


class ConfigFlow(ConfigFlow, domain=DOMAIN):
    """Handle a config flow for Xiaomi Bluetooth."""

    VERSION = 1

    def __init__(self) -> None:
        """Initialize the config flow."""
        self._discovery_info: BluetoothServiceInfo | None = None
        self._discovered_device: DeviceData | None = None
        self._discovered_devices: dict[str, Discovery] = {}
        self._rawtype = 0

    def decode_types(self, format_raw) -> Mapping[str, Any]:
        """Decode the raw format data into a dictionary of display properties."""
        # Extract the first and last bytes
        first_byte = format_raw[0]
        last_byte = format_raw[4]

        # Create a 16-bit word with the last byte first (reverse order)
        raw_type = (last_byte << 8) | first_byte

        screen_resolution = (raw_type >> 5) & 63  # r
        disp_ptype = (raw_type >> 3) & 3  # t
        avail_colors = ((raw_type >> 1) & 3) + ((raw_type >> 10) & 12)  # c and C
        single_double_mirror = raw_type & 1  # m
        can_do_compression = 0 if (raw_type & 0x4000) else 1  # x

        # Use Home Assistant logging instead of print
        _LOGGER.warning(f"Display Resolution: {screen_resolution}")
        _LOGGER.warning(f"Display Type: {disp_ptype}")
        _LOGGER.warning(f"Display Colors: {avail_colors}")
        _LOGGER.warning(f"Display Mirror: {single_double_mirror}")
        _LOGGER.warning(f"Display Compression: {can_do_compression}")

        return {
            "screen_resolution": screen_resolution,
            "display_type": disp_ptype,
            "available_colors": avail_colors,
            "mirror": single_double_mirror,
            "compression": can_do_compression,
        }

    async def async_step_bluetooth(
        self, discovery_info: BluetoothServiceInfo
    ) -> ConfigFlowResult:
        """Handle the bluetooth discovery step."""
        await self.async_set_unique_id(discovery_info.address)
        self._abort_if_unique_id_configured()
        data = discovery_info.advertisement.manufacturer_data

        # Check if the key 0x5053 is present in manufacturer_data
        if 0x5053 in data:
            format_raw = data[0x5053]

            # Ensure it contains exactly five bytes
            if len(format_raw) == 5:
                # Log the entire 5 bytes as a hex string
                _LOGGER.warning(f"Manufacturer data (hex): {format_raw.hex()}")

                # Decode the 16-bit word using decode_types function
                decoded_values = self.decode_types(format_raw)

            else:
                _LOGGER.warning("Manufacturer data for key 0x5053 is not five bytes")
        else:
            _LOGGER.warning("Manufacturer data key 0x5053 is missing")



        device = DeviceData()
        if not device.supported(discovery_info):
            return self.async_abort(reason="not_supported")

        title = _title(discovery_info, device)
        self.context["title_placeholders"] = {"name": title}

        self._discovered_device = device

        return await self.async_step_bluetooth_confirm()

    async def async_step_bluetooth_confirm(
        self, user_input: dict[str, Any] | None = None
    ) -> ConfigFlowResult:
        """Confirm discovery."""
        if user_input is not None or not onboarding.async_is_onboarded(self.hass):
            return self._async_get_or_create_entry()

        # our_name = self.context["title_placeholders"]

        self._set_confirm_only()
        return self.async_show_form(
            step_id="bluetooth_confirm",
            description_placeholders=self.context["title_placeholders"],
        )
        # return self.async_show_form(
        #     step_id="bluetooth_confirm",
        #     data_schema=vol.Schema({vol.Required("input_parameter"): str}),
        # )

    #        self._set_confirm_only()
    # return self.async_show_form(
    #     step_id="bluetooth_confirm",
    #     description_placeholders=self.context["title_placeholders"],
    # )

    async def async_step_user(
        self, user_input: dict[str, Any] | None = None
    ) -> ConfigFlowResult:
        """Handle the user step to pick discovered device."""
        if user_input is not None:
            address = user_input[CONF_ADDRESS]
            await self.async_set_unique_id(address, raise_on_progress=False)
            self._abort_if_unique_id_configured()
            discovery = self._discovered_devices[address]

            self.context["title_placeholders"] = {"name": discovery.title}

            self._discovered_device = discovery.device

            return self._async_get_or_create_entry()

        current_addresses = self._async_current_ids()
        for discovery_info in async_discovered_service_info(self.hass, False):
            address = discovery_info.address
            if address in current_addresses or address in self._discovered_devices:
                continue
            device = DeviceData()
            if device.supported(discovery_info):
                self._discovered_devices[address] = Discovery(
                    title=_title(discovery_info, device),
                    discovery_info=discovery_info,
                    device=device,
                )

        if not self._discovered_devices:
            return self.async_abort(reason="no_devices_found")

        titles = {
            address: discovery.title
            for (address, discovery) in self._discovered_devices.items()
        }
        return self.async_show_form(
            step_id="user",
            data_schema=vol.Schema({vol.Required(CONF_ADDRESS): vol.In(titles)}),
        )

    def _async_get_or_create_entry(
        self, bindkey: str | None = None
    ) -> ConfigFlowResult:
        data: dict[str, Any] = {}

        if bindkey:
            data["bindkey"] = bindkey

        if entry_id := self.context.get("entry_id"):
            entry = self.hass.config_entries.async_get_entry(entry_id)
            assert entry is not None
            return self.async_update_reload_and_abort(entry, data=data)

        return self.async_create_entry(
            title=self.context["title_placeholders"]["name"],
            data=data,
        )
