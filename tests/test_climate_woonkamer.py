import pytest
from homeassistant.core import HomeAssistant
from homeassistant.setup import async_setup_component
from pytest_bdd import given, parsers, scenarios, then, when

from climate_loader import async_setup_climate
from ha_test_helpers import call_action, entity_attribute, entity_state, set_entity_attribute, set_entity_state

scenarios("features/climate_woonkamer.feature")

WOONKAMER_CLIMATE_UNIQUE_ID = "woonkamer_klimaat"
WOONKAMER_CLIMATE_ENTITY_ID = "climate.woonkamer"
WOONKAMER_ROOM_TEMPERATURE_SENSOR = "sensor.tstat_9d4027_current_temperature"
WOONKAMER_HEATING_THRESHOLD = "input_number.airco_woonkamer_drempelwaarde_verwarmen"
WOONKAMER_COOLING_THRESHOLD = "input_number.airco_woonkamer_drempelwaarde_koelen"
HEATING_SEASON_OUTDOOR_THRESHOLD = "input_number.airco_ventileren_buitentemp_drempel"

FORCED_MODE_HELPERS = ("airco_woonkamer_moet_uit", "airco_woonkamer_moet_verwarmen", "airco_woonkamer_moet_afkoelen")
TEMPERATURE_HELPERS = {
    "airco_woonkamer_drempelwaarde_verwarmen": {"min": 16, "max": 30, "step": 0.5},
    "airco_woonkamer_drempelwaarde_koelen": {"min": 16, "max": 30, "step": 0.5},
    "airco_ventileren_buitentemp_drempel": {"min": -10, "max": 30, "step": 0.5},
}


@pytest.fixture(autouse=True)
def auto_enable_custom_integrations(enable_custom_integrations):
    yield


@pytest.fixture(autouse=True)
def woonkamer_helpers(hass: HomeAssistant, run_in_hass_loop):
    async def async_setup_helpers() -> None:
        assert await async_setup_component(hass, "input_boolean", {"input_boolean": {helper: {} for helper in FORCED_MODE_HELPERS}})
        assert await async_setup_component(hass, "input_number", {"input_number": TEMPERATURE_HELPERS})
        await hass.async_block_till_done()

    run_in_hass_loop(async_setup_helpers())


@given(parsers.parse("het is {temperature:g} graden in de woonkamer"))
def room_temperature(hass, run_in_hass_loop, temperature):
    set_entity_state(hass, run_in_hass_loop, WOONKAMER_ROOM_TEMPERATURE_SENSOR, str(temperature))


@given(parsers.parse("de verwarm-drempel van de woonkamer is {temperature:g} graden"))
def heating_threshold(hass, run_in_hass_loop, temperature):
    set_entity_state(hass, run_in_hass_loop, WOONKAMER_HEATING_THRESHOLD, str(temperature))


@given(parsers.parse("de koel-drempel van de woonkamer is {temperature:g} graden"))
def cooling_threshold(hass, run_in_hass_loop, temperature):
    set_entity_state(hass, run_in_hass_loop, WOONKAMER_COOLING_THRESHOLD, str(temperature))


@given(parsers.parse("het is stookseizoen onder {temperature:g} graden buiten"))
def heating_season_threshold(hass, run_in_hass_loop, temperature):
    set_entity_state(hass, run_in_hass_loop, HEATING_SEASON_OUTDOOR_THRESHOLD, str(temperature))


@given(parsers.parse("het is {temperature:g} graden buiten"))
def outdoor_temperature(hass, run_in_hass_loop, temperature):
    set_entity_attribute(hass, run_in_hass_loop, "weather.home", "temperature", temperature)


@given("de climate-template woonkamer is actief")
def climate_template_active(hass, run_in_hass_loop):
    run_in_hass_loop(async_setup_climate(hass, WOONKAMER_CLIMATE_UNIQUE_ID))


@when(parsers.parse("de doeltemperatuur van de woonkamer op {temperature:g} graden wordt gezet"))
def set_target_temperature(hass, run_in_hass_loop, temperature):
    call_action(hass, run_in_hass_loop, "climate", "set_temperature", {"entity_id": WOONKAMER_CLIMATE_ENTITY_ID, "temperature": temperature})


@then(parsers.parse('staat de woonkamer op "{expected_hvac_mode}"'))
def woonkamer_hvac_mode(hass, expected_hvac_mode):
    assert entity_state(hass, WOONKAMER_CLIMATE_ENTITY_ID) == expected_hvac_mode


@then(parsers.parse("toont de woonkamer een doeltemperatuur van {expected_temperature:g} graden"))
def woonkamer_target_temperature(hass, expected_temperature):
    assert entity_attribute(hass, WOONKAMER_CLIMATE_ENTITY_ID, "temperature") == expected_temperature


@then(parsers.parse("is de verwarm-drempel van de woonkamer {expected_temperature:g} graden"))
def heating_threshold_is(hass, expected_temperature):
    assert float(entity_state(hass, WOONKAMER_HEATING_THRESHOLD)) == expected_temperature


@then(parsers.parse("is de koel-drempel van de woonkamer {expected_temperature:g} graden"))
def cooling_threshold_is(hass, expected_temperature):
    assert float(entity_state(hass, WOONKAMER_COOLING_THRESHOLD)) == expected_temperature
