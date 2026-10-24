import os
from pathlib import Path
from typing import Any

from homeassistant.core import HomeAssistant
from homeassistant.setup import async_setup_component
from homeassistant.util.yaml import load_yaml

REPOSITORY_ROOT = Path(__file__).resolve().parent.parent
DEFAULT_CLIMATE_PATH = REPOSITORY_ROOT / "includes" / "climate.yaml"


def climate_path() -> Path:
    return Path(os.environ.get("CLIMATE_YAML_PATH", DEFAULT_CLIMATE_PATH))


def load_climate_config(climate_unique_id: str) -> dict[str, Any]:
    for climate_config in load_yaml(climate_path()):
        if climate_config.get("unique_id") == climate_unique_id:
            return climate_config
    raise LookupError(f"Climate met unique_id {climate_unique_id} niet gevonden in {climate_path()}")


async def async_setup_climate(hass: HomeAssistant, climate_unique_id: str) -> None:
    climate_config = load_climate_config(climate_unique_id)
    assert await async_setup_component(hass, "climate", {"climate": [climate_config]})
    await hass.async_block_till_done()
