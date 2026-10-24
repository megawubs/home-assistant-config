from datetime import timedelta

from homeassistant.core import HomeAssistant
from homeassistant.util import dt as dt_util
from pytest_homeassistant_custom_component.common import async_fire_time_changed


def parse_value(raw_value: str):
    try:
        return float(raw_value)
    except ValueError:
        return raw_value.strip('"')


def set_entity_state(hass: HomeAssistant, run_in_hass_loop, entity_id: str, state: str) -> None:
    domain = entity_id.split(".")[0]
    if domain == "input_number" and hass.services.has_service("input_number", "set_value"):
        call_action(hass, run_in_hass_loop, "input_number", "set_value", {"entity_id": entity_id, "value": float(state)})
        return

    async def async_set_state() -> None:
        current_state = hass.states.get(entity_id)
        current_attributes = dict(current_state.attributes) if current_state else {}
        hass.states.async_set(entity_id, state, current_attributes)
        await hass.async_block_till_done()

    run_in_hass_loop(async_set_state())


def set_entity_attribute(hass: HomeAssistant, run_in_hass_loop, entity_id: str, attribute: str, value) -> None:
    async def async_set_attribute() -> None:
        current_state = hass.states.get(entity_id)
        state = current_state.state if current_state else "unknown"
        attributes = dict(current_state.attributes) if current_state else {}
        attributes[attribute] = value
        hass.states.async_set(entity_id, state, attributes)
        await hass.async_block_till_done()

    run_in_hass_loop(async_set_attribute())


def call_action(hass: HomeAssistant, run_in_hass_loop, domain: str, service: str, service_data: dict) -> None:
    async def async_call_action() -> None:
        await hass.services.async_call(domain, service, service_data, blocking=True)
        await hass.async_block_till_done()

    run_in_hass_loop(async_call_action())


def let_time_pass(hass: HomeAssistant, run_in_hass_loop, seconds: int) -> None:
    async def async_let_time_pass() -> None:
        for elapsed_seconds in range(1, seconds + 1):
            async_fire_time_changed(hass, dt_util.utcnow() + timedelta(seconds=elapsed_seconds))
            await hass.async_block_till_done()

    run_in_hass_loop(async_let_time_pass())


def entity_state(hass: HomeAssistant, entity_id: str) -> str:
    state = hass.states.get(entity_id)
    assert state is not None, f"{entity_id} bestaat niet"
    return state.state


def entity_attribute(hass: HomeAssistant, entity_id: str, attribute: str):
    state = hass.states.get(entity_id)
    assert state is not None, f"{entity_id} bestaat niet"
    return state.attributes.get(attribute)
