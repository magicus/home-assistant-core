"""
Support for the ncid Caller ID service.

For more details about this platform, please refer to the documentation at
https://home-assistant.io/components/binary_sensor.ncid/
"""
import logging
import socket
from threading import Thread

import voluptuous as vol

from homeassistant.components.binary_sensor import (
    BinarySensorDevice, PLATFORM_SCHEMA)

from homeassistant.const import (
    CONF_NAME, CONF_HOST, CONF_PORT)
import homeassistant.helpers.config_validation as cv

_LOGGER = logging.getLogger(__name__)

ICON_OFF = 'mdi:phone-hangup'
ICON_ON = 'mdi:phone-in-talk'
ICON_INCOMING = 'mdi:phone-incoming'
ICON_OUTGOING = 'mdi:phone-outgoing'

STATE_UNKNOWN = None
STATE_OFF = "on hook"
STATE_ON = "in call"
STATE_IN_PROGRESS_INCOMING = "incoming ringing"
STATE_IN_PROGRESS_OUTGOING = "outgoing ringing"

EVENT_INCOMING_CALL = 'ncid.incoming_call'

ATTR_NAME = "name"
ATTR_NUMBER = "number"

DEFAULT_HOST = 'localhost'
DEFAULT_PORT = '3333'
DEFAULT_NAME = 'Phone'

PLATFORM_SCHEMA = PLATFORM_SCHEMA.extend({
    vol.Optional(CONF_HOST, default=DEFAULT_HOST): cv.string,
    vol.Optional(CONF_PORT, default=DEFAULT_PORT): cv.port,
    vol.Optional(CONF_NAME, default=DEFAULT_NAME): cv.string,
})

def setup_platform(hass, config, add_devices, discovery_info=None):
    """Set up the ncid Caller ID client."""
    host = config.get(CONF_HOST)
    port = config.get(CONF_PORT)
    device_name = config.get(CONF_NAME)

    ncid_client = NcidClient(hass, host, port, device_name)

    add_devices([ncid_client])


class NcidClient(BinarySensorDevice):
    """Implementation of a ncid Caller ID client."""

    def __init__(self, hass, host, port, device_name ):
        """Set all the config values if they exist and get initial state."""
        self._hass = hass
        self._host = host
        self._port = port
        self._device_name  = device_name
        self._last_name = None
        self._last_number = None
        self._state = STATE_UNKNOWN
        self.update()

        # FIXME: Use hass.async_add_job ?
        self._thread = Thread(target = self._run_thread)
        self._thread.start()

    @property
    def icon(self):
        if self._state == STATE_ON:
            return ICON_ON
        if self._state == STATE_IN_PROGRESS_INCOMING:
            return ICON_INCOMING
        if self._state == STATE_IN_PROGRESS_OUTGOING:
            return ICON_OUTGOING
        return ICON_OFF

    @property
    def should_poll(self):
        """No polling needed."""
        return False

    @property
    def name(self):
        """Return the name of this entity."""
        return self._device_name

    @property
    def is_on(self):
        """True if the binary sensor is on."""
        return self._state != STATE_OFF and self._state != STATE_UNKNOWN

    @property
    def state(self):
        # FIXME: HACK: Just testing...
        #self._incoming_call('test', '1234')
        """Return the state of this entity."""
        return self._state

    @property
    def device_state_attributes(self):
        """Return device specific state attributes."""
        attr = {}
        attr[ATTR_NAME] = self._last_name
        attr[ATTR_NUMBER] = self._last_number

        return attr

    def _run_thread(self):
        try:
            sock = socket.create_connection((self._host, int(self._port)))
        except ConnectionError as e:
            _LOGGER.error("Cannot connect to NCID server %s:%s", self._host, self._port)
            raise e
        except Exception as e:
            _LOGGER.error("Cannot connect to NCID server %s:%s", self._host, self._port)
            raise e

        # print("CONNECTED")
        for line in sock.makefile():
            # print("recieved line: {}".format(line))
            try:
                code = int(line[:3])
                message = line[3:]

                self._handle_error(code, message)
            except:
                attr = self._parse_line(line)
                self._handle_message(attr)

        sock.close()

    def _handle_error(self, code, message):
        print("recieved code: {}, msg {}".format(code, message))

    def _handle_message(self, attr):
        from pprint import pprint

        print("handling message: {}".format(attr))
        pprint(attr)
        if attr['CMD'] == 'OUT':
            try:
                name = attr['NAME']
                if name == '-' or name == 'NO NAME':
                    name = None
            except:
                name = None

            try:
                number = attr['NMBR']
                # FIXME: copy paste error for name/number
                if number == '-' or number == 'NO NMBR':
                    number = None
            except:
                number = None

    def _incoming_call(self, name, number):
        _LOGGER.debug("NCID reports incoming call from %s (%s)", name, number)
        self._last_name = name
        self._last_number = number
        self.test_it()

        self._hass.bus.fire(EVENT_INCOMING_CALL, {
                ATTR_NAME: name,
                ATTR_NUMBER: number
            })

    def _parse_line(self, line):
        cmd, rest = line.split(':', 1)
        data = rest.strip().strip('*').split('*')
        attr = dict(zip(*[iter(data)] * 2))
        attr['CMD'] = cmd
        return attr
