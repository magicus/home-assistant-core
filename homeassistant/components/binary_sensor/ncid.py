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
# FIXME: while developing
DEBUG_NCID = True
if DEBUG_NCID:
    import sys
    logging.basicConfig(stream=sys.stdout)
    _LOGGER.setLevel('DEBUG')

ICON_OFF = 'mdi:phone-hangup'
ICON_ON = 'mdi:phone-in-talk'
ICON_INCOMING = 'mdi:phone-incoming'
ICON_OUTGOING = 'mdi:phone-outgoing'

STATE_UNKNOWN = 'unknown'
STATE_OFF = "on hook"
STATE_ON = "in call"
STATE_IN_PROGRESS_INCOMING = "incoming ringing"
STATE_IN_PROGRESS_OUTGOING = "outgoing ringing"

NUMBER_OUT_OF_AREA = 'OUT-OF-AREA'
NUMBER_ANONYMOUS = 'ANONYMOUS'
NUMBER_PRIVATE = 'PRIVATE'

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
        self._is_connected = False
        self.update()

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
        """Return the state of this entity."""
        return self._state

    @property
    def device_state_attributes(self):
        """Return device specific state attributes."""
        attr = {
            ATTR_NAME: self._last_name,
            ATTR_NUMBER: self._last_number
        }

        return attr

    def update(self):
        if not self._is_connected:
            # If we lost the connection, re-establish it
            self._is_connected = True
            self._thread = Thread(target=self._run_thread)
            self._thread.daemon = True
            self._thread.start()

    def _run_thread(self):
        try:
            sock = socket.create_connection((self._host, int(self._port)))
        except ConnectionError as e:
            _LOGGER.error("Cannot connect to NCID server {}:{}".format(self._host, self._port))
            self._is_connected = False
            raise e
        except Exception as e:
            _LOGGER.error("Cannot connect to NCID server {}:{}".format(self._host, self._port))
            self._is_connected = False
            raise e

        _LOGGER.info("Connected to NCID server {}:{}".format(self._host, self._port))
        for line in sock.makefile():
            if line[:3].isdigit():
                code = int(line[:3])
                message = line[4:]

                self._handle_error(code, message)
            else:
                attr = self._parse_line(line)
                self._handle_message(attr)

        sock.close()
        self._is_connected = False

    def _handle_error(self, code, message):
        _LOGGER.debug("NCID recieved status: {} {}".format(code, message))


    def _handle_message(self, attr):
        from pprint import pprint

        _LOGGER.debug("NCID recieved message: {}".format(attr))
        pprint(attr)

        # CID OUT HUP (internal hangup) BLK PID WID
        # END CIDINFO/CANCEL CIDINFO/BYE

        if attr['CMD'] == 'CID' or attr['CMD'] == 'PID':
            # Sent just ahead of incoming call, including caller ID
            # PID is same as CID, but used for certain smartphones
            name, number = self._get_caller_id(attr)
            self._state = STATE_IN_PROGRESS_INCOMING
            self.schedule_update_ha_state(force_refresh=True)
            print (name, number)

        if attr['CMD'] == 'OUT':
            # Sent when placing an outgoing call, including 'callee' ID
            name, number = self._get_caller_id(attr)
            self._state = STATE_IN_PROGRESS_OUTGOING
            self.schedule_update_ha_state(force_refresh=True)
            print("outgoing")
            print (name, number)

        if attr['CMD'] == 'CIDINFO':
            # Send for each "ring" in an incoming call,
            # and when call is picked up or terminated
            ring = int(attr['RING'])
            if ring == 0:
                # Call was answered
                self._state = STATE_ON
                self.schedule_update_ha_state(force_refresh=True)
            elif ring == -1:
                # Call stopped ringing due to other end hanging up (CANCEL)
                self._state = STATE_OFF
                self.schedule_update_ha_state(force_refresh=True)
            elif ring == -2:
                # Call has been terminated due to this side hanging up (BYE)
                print("call is terminated")
                self._state = STATE_OFF
                self.schedule_update_ha_state(force_refresh=True)
            else:
                # The incoming call is not answered, ring contains ring count.
                if self._state != STATE_IN_PROGRESS_INCOMING:
                    _LOGGER.debug("NCID internal error: CIDINFO RING {} with no call in progress".format(ring))
                    self._state = STATE_IN_PROGRESS_INCOMING
                    self.schedule_update_ha_state(force_refresh=True)

        if attr['CMD'] == 'END':
            # Sent after a call is completed
            name, number = self._get_caller_id(attr)
            if self._state != STATE_OFF:
                _LOGGER.debug("NCID internal error: END with no prior CIDINFO/-X")
                self._state = STATE_OFF
                self.schedule_update_ha_state(force_refresh=True)
            hangup_reason = attr['HTYPE'] # BYE or CANCEL
            call_direction = attr['CTYPE'] # IN or OUT
            print (name, number)

        if attr['CMD'] == 'HUP':
            # Sent when ncid automatically hangs up (e.g. blacklisted) call
            self._state = STATE_OFF
            self.schedule_update_ha_state(force_refresh=True)
            hangup_reason = ''
            call_direction = attr['CTYPE'] # IN or OUT
            print (name, number)

        if attr['CMD'] == 'MSG':
            _LOGGER.info("NCID general message: {}".format(attr['MSG']))
            _LOGGER.info("NCID message attributes: {}".format(attr))


    def _get_caller_id(self, attr):
        try:
            name = attr['NAME']
            if name == '-' or name == 'NO NAME':
                name = None
        except:
            name = None
        try:
            number = attr['NMBR']
            if number == '-' or number == 'NO-NUMBER':
                number = None
        except:
            number = None

        return name, number

    def _incoming_call(self, name, number):
        _LOGGER.info("NCID reports incoming call from {} ({})".format(number, name))
        self._last_name = name
        self._last_number = number

        self._hass.bus.fire(EVENT_INCOMING_CALL, {
                ATTR_NAME: name,
                ATTR_NUMBER: number
            })

    def _parse_line(self, line):
        cmd, rest = line.split(':', 1)
        msg = None
        if cmd == 'MSG' or cmd == '+MSG':
            # Extract the message part which is prepended to the key-value pairs.
            msg, rest = rest[1:].split('**')

        data = rest.strip().strip('*').split('*')
        attr = dict(zip(*[iter(data)] * 2))

        attr['CMD'] = cmd
        if msg:
            attr['MSG'] = msg
        return attr
