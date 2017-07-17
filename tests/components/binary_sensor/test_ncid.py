"""The tests for the ncid Caller ID binary sensor platform."""
import socketserver
import threading
import unittest

from homeassistant.components.binary_sensor import ncid
from homeassistant.setup import setup_component
import homeassistant.components.binary_sensor as binary_sensor
from homeassistant.const import (STATE_OFF, STATE_ON, STATE_UNKNOWN)

from tests.common import (
    get_test_home_assistant, assert_setup_component)

TEST_HOST = 'localhost'
TEST_PORT = 33331

TEST_CONFIG = {
    binary_sensor.DOMAIN: {
        'platform': 'ncid',
        ncid.CONF_NAME: 'fake_ncid',
        ncid.CONF_HOST: TEST_HOST,
        ncid.CONF_PORT: TEST_PORT,
    },
}

class FakeNCIDServer:
    class ReuseAddressThreadingTCPServer(socketserver.ThreadingTCPServer):
        allow_reuse_address = True

    class MyNCIDHandler(socketserver.StreamRequestHandler):
        def handle(self):
            print("in handle")
            # output = 'CIDINFO: *LINE*4901*RING*-2*TIME*00:11:01*'
            output = 'OUT: *DATE*01152017*TIME*0010*LINE*4901*NMBR*012345611*MESG*NONE*NAME*NO NAME*'

            self.wfile.write(bytearray(output, 'utf8'))
            self.wfile.flush()

    def __init__(self, address):
        self._server = FakeNCIDServer.ReuseAddressThreadingTCPServer(address, FakeNCIDServer.MyNCIDHandler)

    def start(self):
        self._server_thread = threading.Thread(target=self._server.serve_forever)
        self._server_thread.daemon = True
        self._server_thread.start()

    def stop(self):
        self._server.shutdown()
        self._server_thread.join()

class TestNCIDBinarySensor(unittest.TestCase):
    """Test the ncid Caller ID service."""

    def setUp(self):  # pylint: disable=invalid-name
        """Setup things to be run when tests are started."""
        self.hass = get_test_home_assistant()
        self.server = FakeNCIDServer((TEST_HOST, TEST_PORT))
        self.server.start()

    def tearDown(self):  # pylint: disable=invalid-name
        """Stop everything that was started."""
        self.server.stop()
        self.hass.stop()

    def test_setup_platform_valid_config(self):
        """Check a valid configuration."""
        with assert_setup_component(1, binary_sensor.DOMAIN):
            assert setup_component(
                self.hass, binary_sensor.DOMAIN, TEST_CONFIG)

    def test_default_sensor_value(self):
        """Test the default sensor value."""
        with assert_setup_component(1, binary_sensor.DOMAIN):
            assert setup_component(
                self.hass, binary_sensor.DOMAIN, TEST_CONFIG)

        state = self.hass.states.get('binary_sensor.fake_ncid')
        self.assertEqual(STATE_UNKNOWN, state.state)
