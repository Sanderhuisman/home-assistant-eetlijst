import logging

import homeassistant.helpers.config_validation as cv
import voluptuous as vol
from homeassistant.components.sensor import PLATFORM_SCHEMA
from homeassistant.const import (
    ATTR_ATTRIBUTION,
    CONF_PASSWORD,
    CONF_USERNAME,
    CONF_SENSORS,
    STATE_UNAVAILABLE
)
from homeassistant.helpers.entity import Entity
from homeassistant.util import Throttle

import homeassistant.util.dt as dt_util

from .helpers import EetlijstApi
from .const import (
    CONF_UTILISATION_CONDITIONS,
    CONF_UTILISATION_DEADLINE,
    CONF_UTILISATION_NOTICEBOARD,
    CONF_ATTRIBUTION
)

_LOGGER = logging.getLogger(__name__)

CONF_UTILISATION_CONDITIONS_KEYS = list(
    CONF_UTILISATION_CONDITIONS.keys())

PLATFORM_SCHEMA = PLATFORM_SCHEMA.extend({
    vol.Required(CONF_USERNAME): cv.string,
    vol.Required(CONF_PASSWORD): cv.string,

    vol.Optional(CONF_SENSORS, default=CONF_UTILISATION_CONDITIONS_KEYS):
        vol.All(cv.ensure_list, [
                vol.In(CONF_UTILISATION_CONDITIONS_KEYS)]),
})

def setup_platform(hass, config, add_entities, discovery_info = None):
    """Set up the Eetlijst Sensor."""

    username = config.get(CONF_USERNAME)
    password = config.get(CONF_PASSWORD)

    try:
        api = EetlijstApi(username=username, password=password)

        sensors = [EetlijstSensorEntity(api, api.accountname, variable)
               for variable in config.get(CONF_SENSORS) if variable in CONF_UTILISATION_CONDITIONS]

        # Handle all persons
        for resident in api.residents:
            sensors.append(EetlijstSensorPerson(api, api.accountname, resident))

        add_entities(sensors, True)
    except:  # noqa: E722 pylint: disable=bare-except
        _LOGGER.error("Error setting up Eetlijst sensor")

class EetlijstSensorPerson(Entity):
    """Representation of a Eetlijst Sensor."""

    def __init__(self, api, accountname, resident):
        """Initialize the sensor."""
        self.var_units = None
        self.var_icon = 'mdi:stove'
        self.accountname = accountname
        self.resident = resident
        self._api = api
        self._state = None

    @property
    def name(self):
        """Return the name of the sensor, if any."""
        return "{} {}".format(self.accountname, self.resident)

    @property
    def unique_id(self):
        """Return a unique ID."""
        return 'eetlijst_' + self.name.lower().replace(" ", "_").replace("-", "_")

    @property
    def icon(self):
        """Icon to use in the frontend, if any."""
        return self.var_icon

    @property
    def state(self):
        """Return the state of the sensor."""

        # get status of today
        status = self._api.statuses[0].statuses[self.resident]
        if status is None:
            value = "?"
        elif status == 0:
            value = "No dinner"
        elif status == 1:
            value = "Cook"
        elif status == -1:
            value = "Dinner"
        elif status > 1:
            value = "Cook + %d" % (status - 1)
        elif status < -1:
            value = "Dinner + %d" % (-1 * status - 1)
        return value

    @property
    def unit_of_measurement(self):
        """Return the unit the value is expressed in."""
        return self.var_units

    def update(self):
        """Get the latest data for the states."""
        if self._api is not None:
            self._api.update()

    @property
    def device_state_attributes(self):
        """Return the state attributes."""
        return {
            ATTR_ATTRIBUTION: CONF_ATTRIBUTION,
        }


class EetlijstSensorEntity(Entity):
    """Representation of a Eetlijst Sensor."""

    def __init__(self, api, accountname : str, variable):
        """Initialize the sensor."""
        self._api = api
        self._accountname = accountname
        self._state = None

        self._var_id = variable
        self._var_name = CONF_UTILISATION_CONDITIONS[variable][0]
        self._var_unit = CONF_UTILISATION_CONDITIONS[variable][1]
        self._var_icon = CONF_UTILISATION_CONDITIONS[variable][2]
        self._var_class = CONF_UTILISATION_CONDITIONS[variable][3]

    @property
    def name(self):
        """Return the name of the sensor, if any."""
        return "{} {}".format(self._accountname, self._var_name)

    @property
    def unique_id(self):
        """Return a unique ID."""
        return 'eetlijst_' + self.name.lower().replace(" ", "_").replace("-", "_")

    @property
    def icon(self):
        """Icon to use in the frontend, if any."""
        return self._var_icon

    @property
    def state(self):
        """Return the state of the sensor."""

        state = STATE_UNAVAILABLE
        if self._var_id == CONF_UTILISATION_DEADLINE:
            # get status of today
            if self._api.statuses[0].deadline:
                state = dt_util.as_local(self._api.statuses[0].deadline).isoformat()
            else:
                state = None
        elif self._var_id == CONF_UTILISATION_NOTICEBOARD:
            state = self._api.get_noticeboard()
        return state

    @property
    def device_class(self) -> str:
        """Return the class of this sensor."""
        return self._var_class

    @property
    def unit_of_measurement(self) -> str:
        """Return the unit the value is expressed in."""
        return self._var_unit

    def update(self):
        """Get the latest data for the states."""
        if self._api is not None:
            self._api.update()

    @property
    def device_state_attributes(self):
        """Return the state attributes."""
        return {
            ATTR_ATTRIBUTION: CONF_ATTRIBUTION,
        }
