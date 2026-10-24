import pytest
from homeassistant.core import HomeAssistant, ServiceCall
from pytest_bdd import given, parsers, scenarios, then
from pytest_homeassistant_custom_component.common import async_mock_service

from automation_loader import async_setup_automation, automation_config_id_for_alias
from ha_test_helpers import set_entity_state

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


@pytest.fixture
def mocked_service_calls(hass: HomeAssistant, run_in_hass_loop) -> dict[str, list[ServiceCall]]:
    async def async_mock_all_services() -> dict[str, list[ServiceCall]]:
        return {
            f"{domain}.{service}": async_mock_service(hass, domain, service)
            for domain, service in MOCKED_SERVICES
        }

    return run_in_hass_loop(async_mock_all_services())


@given("de handmatige override van de airco woonkamer staat uit")
def manual_override_off(hass, run_in_hass_loop):
    set_entity_state(hass, run_in_hass_loop, "input_boolean.airco_woonkamer_manual_override", "off")


@given("de airco woonkamer mag aan volgens het schema")
def airco_allowed_on(hass, run_in_hass_loop):
    set_entity_state(hass, run_in_hass_loop, "binary_sensor.airco_woonkamer_mag_aan", "on")


@given("afkoelen, verwarmen en ventileren zijn niet nodig")
def nothing_needed(hass, run_in_hass_loop):
    for need in ("afkoelen", "verwarmen", "ventileren"):
        set_entity_state(hass, run_in_hass_loop, f"binary_sensor.airco_woonkamer_mag_{need}", "off")


@given("afkoelen en ventileren zijn niet nodig")
def cooling_and_ventilating_not_needed(hass, run_in_hass_loop):
    for need in ("afkoelen", "ventileren"):
        set_entity_state(hass, run_in_hass_loop, f"binary_sensor.airco_woonkamer_mag_{need}", "off")


@given("verwarmen is wel nodig")
def heating_needed(hass, run_in_hass_loop):
    set_entity_state(hass, run_in_hass_loop, "binary_sensor.airco_woonkamer_mag_verwarmen", "on")


@given(parsers.parse('de automation "{automation_alias}" is actief'))
def automation_active(hass, run_in_hass_loop, mocked_service_calls, automation_alias):
    run_in_hass_loop(async_setup_automation(hass, automation_config_id_for_alias(automation_alias)))


@then("wordt de airco beneden direct uitgezet")
def airco_downstairs_turned_off(mocked_service_calls):
    turn_off_calls = mocked_service_calls["climate.turn_off"]
    assert len(turn_off_calls) == 1
    assert turn_off_calls[0].data.get("label_id") == ["airco_beneden"]


@then("wordt de airco beneden niet uitgezet")
def airco_downstairs_not_turned_off(mocked_service_calls):
    assert mocked_service_calls["climate.turn_off"] == []
