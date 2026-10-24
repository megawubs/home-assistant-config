import importlib
import sys
from pathlib import Path

import pytest
from homeassistant.const import ENTITY_MATCH_ALL
from homeassistant.core import HomeAssistant
from pytest_bdd import given, parsers, then, when

from ha_test_helpers import (
    entity_attribute,
    entity_state,
    let_time_pass,
    parse_value,
    set_entity_attribute,
    set_entity_state,
)

VENDOR_PATH = Path(__file__).resolve().parent / "vendor"
for vendored_custom_components_path in sorted(VENDOR_PATH.glob("*/custom_components")):
    vendored_repository_path = str(vendored_custom_components_path.parent)
    if vendored_repository_path not in sys.path:
        sys.path.insert(0, vendored_repository_path)
importlib.import_module("custom_components")

SECONDS_TO_LET_SCRIPT_DELAYS_PASS = 60
WOONKAMER_FORCED_MODE_FLAGS = {
    "verwarmen": "input_boolean.airco_woonkamer_moet_verwarmen",
    "afkoelen": "input_boolean.airco_woonkamer_moet_afkoelen",
    "uit": "input_boolean.airco_woonkamer_moet_uit",
}


@pytest.fixture
def run_in_hass_loop(hass: HomeAssistant):
    def run_coroutine(coroutine):
        return hass.loop.run_until_complete(coroutine)

    yield run_coroutine

    if hass.services.has_service("automation", "turn_off"):
        run_coroutine(hass.services.async_call("automation", "turn_off", {"entity_id": ENTITY_MATCH_ALL}, blocking=True))


@given(parsers.parse('de entity "{entity_id}" staat op "{state}"'))
def given_entity_state(hass, run_in_hass_loop, entity_id, state):
    set_entity_state(hass, run_in_hass_loop, entity_id, state)


@given(parsers.parse('de entity "{entity_id}" heeft attribuut "{attribute}" met waarde {value}'))
def given_entity_attribute(hass, run_in_hass_loop, entity_id, attribute, value):
    set_entity_attribute(hass, run_in_hass_loop, entity_id, attribute, parse_value(value))


@when(parsers.parse('de entity "{entity_id}" op "{state}" wordt gezet'))
def when_entity_state_changes(hass, run_in_hass_loop, entity_id, state):
    set_entity_state(hass, run_in_hass_loop, entity_id, state)
    let_time_pass(hass, run_in_hass_loop, SECONDS_TO_LET_SCRIPT_DELAYS_PASS)


@then(parsers.parse('staat de entity "{entity_id}" op "{expected_state}"'))
def then_entity_state(hass, entity_id, expected_state):
    assert entity_state(hass, entity_id) == expected_state


@then(parsers.parse('heeft de entity "{entity_id}" attribuut "{attribute}" met waarde {expected_value}'))
def then_entity_attribute(hass, entity_id, attribute, expected_value):
    assert entity_attribute(hass, entity_id, attribute) == parse_value(expected_value)


@given(parsers.parse('de airco woonkamer staat op "{hvac_mode}"'))
def airco_woonkamer_hvac_mode(hass, run_in_hass_loop, hvac_mode):
    for climate_entity_id in ("climate.airco_woonkamer", "climate.airco_keuken"):
        set_entity_state(hass, run_in_hass_loop, climate_entity_id, hvac_mode)


@given(parsers.parse("geforceerd {forced_mode} staat {on_or_off}"))
def forced_mode_state(hass, run_in_hass_loop, forced_mode, on_or_off):
    set_entity_state(hass, run_in_hass_loop, WOONKAMER_FORCED_MODE_FLAGS[forced_mode], "on" if on_or_off == "aan" else "off")


@given("geen geforceerde stand staat aan")
def no_forced_mode(hass, run_in_hass_loop):
    for forced_mode_flag in WOONKAMER_FORCED_MODE_FLAGS.values():
        set_entity_state(hass, run_in_hass_loop, forced_mode_flag, "off")


@given("de woonkamer moet uit")
def woonkamer_forced_off(hass, run_in_hass_loop):
    set_entity_state(hass, run_in_hass_loop, WOONKAMER_FORCED_MODE_FLAGS["uit"], "on")


@then(parsers.parse("staat geforceerd {forced_mode} {on_or_off}"))
def forced_mode_is(hass, forced_mode, on_or_off):
    assert entity_state(hass, WOONKAMER_FORCED_MODE_FLAGS[forced_mode]) == ("on" if on_or_off == "aan" else "off")


@when("geforceerd verwarmen wordt uitgezet")
def forced_heating_turned_off(hass, run_in_hass_loop):
    when_entity_state_changes(hass, run_in_hass_loop, WOONKAMER_FORCED_MODE_FLAGS["verwarmen"], "off")
