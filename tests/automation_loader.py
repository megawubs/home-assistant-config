import os
from pathlib import Path
from typing import Any

from homeassistant.core import HomeAssistant
from homeassistant.setup import async_setup_component
from homeassistant.util.yaml import load_yaml

REPOSITORY_ROOT = Path(__file__).resolve().parent.parent
DEFAULT_AUTOMATIONS_PATH = REPOSITORY_ROOT / "automations.yaml"


def automations_path() -> Path:
    return Path(os.environ.get("AUTOMATIONS_YAML_PATH", DEFAULT_AUTOMATIONS_PATH))


def load_automation_config(automation_config_id: str) -> dict[str, Any]:
    all_automation_configs = load_yaml(automations_path())
    for automation_config in all_automation_configs:
        if str(automation_config.get("id")) == automation_config_id:
            return automation_config
    raise LookupError(f"Automation met id {automation_config_id} niet gevonden in {automations_path()}")


def automation_config_id_for_alias(automation_alias: str) -> str:
    for automation_config in load_yaml(automations_path()):
        if automation_config.get("alias") == automation_alias:
            return str(automation_config["id"])
    raise LookupError(f"Automation met alias {automation_alias!r} niet gevonden in {automations_path()}")


async def async_setup_automation(hass: HomeAssistant, automation_config_id: str) -> None:
    automation_config = load_automation_config(automation_config_id)
    assert await async_setup_component(hass, "automation", {"automation": [automation_config]})
    await hass.async_block_till_done()
