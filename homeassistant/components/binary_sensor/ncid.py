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
        self._incoming_call('test', '1234')
        """Return the state of this entity."""
        return self._state

    @property
    def state_attributes(self):
        """Return device specific state attributes."""
        attr = super(NcidClient, self).state_attributes
        attr[ATTR_NAME] = self._last_name
        attr[ATTR_NUMBER] = self._last_number

        return attr

    def _run_thread(self):
        try:
            sock = socket.create_connection((self._host, int(self._port)))
        except ConnectionError as e:
            _LOGGER.error("Cannot connect to NCID server %s:%s", name, number)
            raise e
        except Exception as e:
            _LOGGER.error("Cannot connect to NCID server %s:%s", name, number)
            raise e

        # print("CONNECTED")
        for line in sock.makefile():
            # print("recieved line: {}".format(line))
            try:
                value = int(line[:3])
                msg = line[3:]
                # print("recieved code: {}, msg {}".format(value, msg))
            except:
                cmd, attr = self._parse_line(line)
                name = attr['NAME']
                if  name == '-' or name == 'NO NAME':
                    name = None

                number = attr['NMBR']
                if  name == '-' or name == 'NO NAME':
                    name = None

        sock.close()

    def _incoming_call(self, name, number):
        _LOGGER.debug("NCID reports incoming call from %s (%s)", name, number)
        self._last_name = name
        self._last_number = number
        self.test_it()

        self._hass.bus.fire(EVENT_INCOMING_CALL, {
                ATTR_NAME: name,
                ATTR_NUMBER: number
            })

    def test_it(self):
        from pprint import pprint
        line = 'OUT: *DATE*01152017*TIME*0010*LINE*4901*NMBR*012345611*MESG*NONE*NAME*NO NAME*'
        attr = self._parse_line(line)
        print('cmd: {} for line: {}'.format(attr['CMD'], line))
        pprint(attr)
        line = 'CIDINFO: *LINE*4901*RING*-2*TIME*00:11:01*'
        attr = self._parse_line(line)
        print('cmd: {} for line: {}'.format(attr['CMD'], line))
        pprint(attr)
        line = 'END: *HTYPE*BYE*DATE*01152017*TIME*0011*SCALL*01/15/2017 00:10:47*ECALL*01/15/2017 00:11:01*CTYPE*IN*LINE*4901*NMBR*0123456*NAME*NONAME*'
        attr = self._parse_line(line)
        print('cmd: {} for line: {}'.format(attr['CMD'], line))
        pprint(attr)

    def _parse_line(self, line):
        cmd, rest = line.split(':', 1)
        data = rest.strip().strip('*').split('*')
        attr = dict(zip(*[iter(data)] * 2))
        attr['CMD'] = cmd
        return attr
