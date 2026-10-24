from datetime import timedelta

import pytest
from homeassistant.core import HomeAssistant, ServiceCall
from homeassistant.util import dt as dt_util
from pytest_bdd import given, parsers, scenarios, then, when
from pytest_homeassistant_custom_component.common import async_fire_time_changed, async_mock_service

from automation_loader import async_setup_automation, automation_config_id_for_alias

scenarios("features/airco_woonkamer.feature")

MOCKED_SERVICES = [
    ("climate", "turn_off"),
    ("climate", "turn_on"),
    ("climate", "set_hvac_mode"),
    ("climate", "set_temperature"),
    ("climate", "set_fan_mode"),
    ("climate", "set_swing_mode"),
    ("select", "select_option"),
    ("input_datetime", "set_datetime"),
    ("input_boolean", "turn_on"),
    ("input_boolean", "turn_off"),
    ("notify", "mobile_app_iphone_van_bram"),
]

SECONDS_TO_LET_SCRIPT_DELAYS_PASS = 60


@pytest.fixture
def mocked_service_calls(hass: HomeAssistant, run_in_hass_loop) -> dict[str, list[ServiceCall]]:
    async def async_mock_all_services() -> dict[str, list[ServiceCall]]:
        return {
            f"{domain}.{service}": async_mock_service(hass, domain, service)
            for domain, service in MOCKED_SERVICES
        }

    return run_in_hass_loop(async_mock_all_services())


def set_state(hass: HomeAssistant, run_in_hass_loop, entity_id: str, state: str) -> None:
    async def async_set_state() -> None:
        hass.states.async_set(entity_id, state)
        await hass.async_block_till_done()

    run_in_hass_loop(async_set_state())


@given("de handmatige override van de airco woonkamer staat uit")
def manual_override_off(hass, run_in_hass_loop):
    set_state(hass, run_in_hass_loop, "input_boolean.airco_woonkamer_manual_override", "off")


@given("de airco woonkamer mag aan volgens het schema")
def airco_allowed_on(hass, run_in_hass_loop):
    set_state(hass, run_in_hass_loop, "binary_sensor.airco_woonkamer_mag_aan", "on")


@given(parsers.parse("geforceerd verwarmen staat {forced_state}"))
def forced_heating_state(hass, run_in_hass_loop, forced_state):
    set_state(hass, run_in_hass_loop, "input_boolean.airco_woonkamer_moet_verwarmen", "on" if forced_state == "aan" else "off")


@given(parsers.parse("geforceerd afkoelen staat {forced_state}"))
def forced_cooling_state(hass, run_in_hass_loop, forced_state):
    set_state(hass, run_in_hass_loop, "input_boolean.airco_woonkamer_moet_afkoelen", "on" if forced_state == "aan" else "off")


@given("afkoelen, verwarmen en ventileren zijn niet nodig")
def nothing_needed(hass, run_in_hass_loop):
    for need in ("afkoelen", "verwarmen", "ventileren"):
        set_state(hass, run_in_hass_loop, f"binary_sensor.airco_woonkamer_mag_{need}", "off")


@given("afkoelen en ventileren zijn niet nodig")
def cooling_and_ventilating_not_needed(hass, run_in_hass_loop):
    for need in ("afkoelen", "ventileren"):
        set_state(hass, run_in_hass_loop, f"binary_sensor.airco_woonkamer_mag_{need}", "off")


@given("verwarmen is wel nodig")
def heating_needed(hass, run_in_hass_loop):
    set_state(hass, run_in_hass_loop, "binary_sensor.airco_woonkamer_mag_verwarmen", "on")


@given(parsers.parse('de airco woonkamer staat op "{hvac_mode}"'))
def airco_hvac_mode(hass, run_in_hass_loop, hvac_mode):
    for climate_entity_id in ("climate.airco_woonkamer", "climate.airco_keuken"):
        set_state(hass, run_in_hass_loop, climate_entity_id, hvac_mode)


@given(parsers.parse('de automation "{automation_alias}" is actief'))
def automation_active(hass, run_in_hass_loop, mocked_service_calls, automation_alias):
    run_in_hass_loop(async_setup_automation(hass, automation_config_id_for_alias(automation_alias)))


@when("geforceerd verwarmen wordt uitgezet")
def forced_heating_turned_off(hass, run_in_hass_loop):
    set_state(hass, run_in_hass_loop, "input_boolean.airco_woonkamer_moet_verwarmen", "off")

    async def async_let_script_delays_pass() -> None:
        for elapsed_seconds in range(1, SECONDS_TO_LET_SCRIPT_DELAYS_PASS + 1):
            async_fire_time_changed(hass, dt_util.utcnow() + timedelta(seconds=elapsed_seconds))
            await hass.async_block_till_done()

    run_in_hass_loop(async_let_script_delays_pass())


@then("wordt de airco beneden direct uitgezet")
def airco_downstairs_turned_off(mocked_service_calls):
    turn_off_calls = mocked_service_calls["climate.turn_off"]
    assert len(turn_off_calls) == 1
    assert turn_off_calls[0].data.get("label_id") == ["airco_beneden"]


@then("wordt de airco beneden niet uitgezet")
def airco_downstairs_not_turned_off(mocked_service_calls):
    assert mocked_service_calls["climate.turn_off"] == []

