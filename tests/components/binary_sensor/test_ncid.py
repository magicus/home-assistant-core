"""The tests for the ncid Caller ID binary sensor platform."""
import queue
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
        def __init__(self, *args, **kwargs):
            self.allow_reuse_address = True
            super(FakeNCIDServer.ReuseAddressThreadingTCPServer, self).__init__(*args, **kwargs)
            self.output_queue = queue.Queue()
            self.shutdown_handler = False

        def send(self, line):
            self.output_queue.put(line)

        def shutdown(self):
            super(FakeNCIDServer.ReuseAddressThreadingTCPServer, self).shutdown()
            self.shutdown_handler = True

    class MyNCIDHandler(socketserver.StreamRequestHandler):
        def _send_line(self, line):
            self.wfile.write(bytearray(line + '\n', 'utf8'))
            self.wfile.flush()

        def handle(self):
            while not self.server.shutdown_handler:
                while not self.server.output_queue.empty():
                    line = self.server.output_queue.get()
                    print("will output {}".format(line))
                    self._send_line(line)

    def __init__(self, address):
        self.server = FakeNCIDServer.ReuseAddressThreadingTCPServer(address, FakeNCIDServer.MyNCIDHandler)
        self.server_thread = threading.Thread(target=self.server.serve_forever)
        self.server_thread.daemon = True

    def start(self):
        self.server_thread.start()

    def stop(self):
        self.server.shutdown()
        self.server_thread.join()

    def send(self, line):
        self.server.send(line)

class TestNCIDBinarySensor(unittest.TestCase):
    """Test the ncid Caller ID service."""

    def setUp(self):  # pylint: disable=invalid-name
        """Setup things to be run when tests are started."""
        self.hass = get_test_home_assistant()
        self.server = FakeNCIDServer((TEST_HOST, TEST_PORT))
        self.server.start()
        #self.server.send('CIDINFO: *LINE*4901*RING*-2*TIME*00:11:01*')
        output = 'OUT: *DATE*01152017*TIME*0010*LINE*4901*NMBR*012345611*MESG*NONE*NAME*NO NAME*'
        self.server.send(output + 'CNT*1*')
        self.server.send(output + 'CNT*2*')
        self.server.send(output + 'CNT*3*')

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
