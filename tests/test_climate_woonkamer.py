import pytest
from homeassistant.core import HomeAssistant
from homeassistant.setup import async_setup_component
from pytest_bdd import given, parsers, scenarios, then, when

from climate_loader import async_setup_climate

scenarios("features/climate_woonkamer.feature")

WOONKAMER_CLIMATE_UNIQUE_ID = "woonkamer_klimaat"
WOONKAMER_CLIMATE_ENTITY_ID = "climate.woonkamer"
FORCED_MODE_FLAGS = ("moet_uit", "moet_verwarmen", "moet_afkoelen")

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
        assert await async_setup_component(
            hass,
            "input_boolean",
            {"input_boolean": {f"airco_woonkamer_{forced_mode_flag}": {} for forced_mode_flag in FORCED_MODE_FLAGS}},
        )
        assert await async_setup_component(hass, "input_number", {"input_number": TEMPERATURE_HELPERS})
        await hass.async_block_till_done()

    run_in_hass_loop(async_setup_helpers())


def call_service(hass: HomeAssistant, run_in_hass_loop, domain: str, service: str, service_data: dict) -> None:
    async def async_call_service() -> None:
        await hass.services.async_call(domain, service, service_data, blocking=True)
        await hass.async_block_till_done()

    run_in_hass_loop(async_call_service())


def set_state(hass: HomeAssistant, run_in_hass_loop, entity_id: str, state: str, attributes: dict | None = None) -> None:
    async def async_set_state() -> None:
        hass.states.async_set(entity_id, state, attributes)
        await hass.async_block_till_done()

    run_in_hass_loop(async_set_state())


def set_input_number(hass: HomeAssistant, run_in_hass_loop, helper_name: str, value: float) -> None:
    call_service(hass, run_in_hass_loop, "input_number", "set_value", {"entity_id": f"input_number.{helper_name}", "value": value})


def turn_on_only_forced_mode_flag(hass: HomeAssistant, run_in_hass_loop, active_forced_mode_flag: str | None) -> None:
    for forced_mode_flag in FORCED_MODE_FLAGS:
        service = "turn_on" if forced_mode_flag == active_forced_mode_flag else "turn_off"
        call_service(hass, run_in_hass_loop, "input_boolean", service, {"entity_id": f"input_boolean.airco_woonkamer_{forced_mode_flag}"})


@given(parsers.parse("het is {temperature:g} graden in de woonkamer"))
def room_temperature(hass, run_in_hass_loop, temperature):
    set_state(hass, run_in_hass_loop, "sensor.tstat_9d4027_current_temperature", str(temperature))


@given(parsers.parse("de verwarm-drempel van de woonkamer is {temperature:g} graden"))
def heating_threshold(hass, run_in_hass_loop, temperature):
    set_input_number(hass, run_in_hass_loop, "airco_woonkamer_drempelwaarde_verwarmen", temperature)


@given(parsers.parse("de koel-drempel van de woonkamer is {temperature:g} graden"))
def cooling_threshold(hass, run_in_hass_loop, temperature):
    set_input_number(hass, run_in_hass_loop, "airco_woonkamer_drempelwaarde_koelen", temperature)


@given(parsers.parse("het is stookseizoen onder {temperature:g} graden buiten"))
def heating_season_threshold(hass, run_in_hass_loop, temperature):
    set_input_number(hass, run_in_hass_loop, "airco_ventileren_buitentemp_drempel", temperature)


@given(parsers.parse("het is {temperature:g} graden buiten"))
def outdoor_temperature(hass, run_in_hass_loop, temperature):
    set_state(hass, run_in_hass_loop, "weather.home", "cloudy", {"temperature": temperature})


@given("geen geforceerde stand staat aan")
def no_forced_mode(hass, run_in_hass_loop):
    turn_on_only_forced_mode_flag(hass, run_in_hass_loop, None)


@given("geforceerd verwarmen staat aan")
def forced_heating_on(hass, run_in_hass_loop):
    turn_on_only_forced_mode_flag(hass, run_in_hass_loop, "moet_verwarmen")


@given("geforceerd afkoelen staat aan")
def forced_cooling_on(hass, run_in_hass_loop):
    turn_on_only_forced_mode_flag(hass, run_in_hass_loop, "moet_afkoelen")


@given("de woonkamer moet uit")
def forced_off(hass, run_in_hass_loop):
    turn_on_only_forced_mode_flag(hass, run_in_hass_loop, "moet_uit")


@given(parsers.parse('de airco woonkamer staat op "{hvac_mode}"'))
def airco_unit_hvac_mode(hass, run_in_hass_loop, hvac_mode):
    set_state(hass, run_in_hass_loop, "climate.airco_woonkamer", hvac_mode)


@given("de climate-template woonkamer is actief")
def climate_template_active(hass, run_in_hass_loop):
    run_in_hass_loop(async_setup_climate(hass, WOONKAMER_CLIMATE_UNIQUE_ID))


@when(parsers.parse("de doeltemperatuur van de woonkamer op {temperature:g} graden wordt gezet"))
def set_target_temperature(hass, run_in_hass_loop, temperature):
    call_service(hass, run_in_hass_loop, "climate", "set_temperature", {"entity_id": WOONKAMER_CLIMATE_ENTITY_ID, "temperature": temperature})


@then(parsers.parse('staat de woonkamer op "{expected_hvac_mode}"'))
def woonkamer_hvac_mode(hass, expected_hvac_mode):
    assert hass.states.get(WOONKAMER_CLIMATE_ENTITY_ID).state == expected_hvac_mode


@then(parsers.parse("toont de woonkamer een doeltemperatuur van {expected_temperature:g} graden"))
def woonkamer_target_temperature(hass, expected_temperature):
    assert hass.states.get(WOONKAMER_CLIMATE_ENTITY_ID).attributes["temperature"] == expected_temperature


@then(parsers.parse("is de verwarm-drempel van de woonkamer {expected_temperature:g} graden"))
def heating_threshold_is(hass, expected_temperature):
    assert float(hass.states.get("input_number.airco_woonkamer_drempelwaarde_verwarmen").state) == expected_temperature


@then(parsers.parse("is de koel-drempel van de woonkamer {expected_temperature:g} graden"))
def cooling_threshold_is(hass, expected_temperature):
    assert float(hass.states.get("input_number.airco_woonkamer_drempelwaarde_koelen").state) == expected_temperature


@then("staat geforceerd verwarmen uit")
def forced_heating_off(hass):
    assert hass.states.get("input_boolean.airco_woonkamer_moet_verwarmen").state == "off"
