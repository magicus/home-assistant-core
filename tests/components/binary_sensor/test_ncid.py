"""The tests for the ncid Caller ID binary sensor platform."""
import unittest

from homeassistant.components.binary_sensor import ncid
from homeassistant.setup import setup_component
import homeassistant.components.binary_sensor as binary_sensor
from homeassistant.const import (STATE_OFF, STATE_ON, STATE_UNKNOWN)

from tests.common import (
    get_test_home_assistant, assert_setup_component)

TEST_CONFIG = {
    binary_sensor.DOMAIN: {
        'platform': 'ncid',
        ncid.CONF_NAME: 'fake_ncid',
        ncid.CONF_HOST: 'localhost',
        ncid.CONF_PORT: 33330,
    },
}

class TestNCIDBinarySensor(unittest.TestCase):
    """Test the ncid Caller ID service."""

    def setUp(self):  # pylint: disable=invalid-name
        """Setup things to be run when tests are started."""
        self.hass = get_test_home_assistant()

    def tearDown(self):  # pylint: disable=invalid-name
        """Stop everything that was started."""
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
