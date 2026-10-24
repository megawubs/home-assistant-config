import importlib
import sys
from pathlib import Path

import pytest
from homeassistant.const import ENTITY_MATCH_ALL
from homeassistant.core import HomeAssistant

VENDOR_PATH = Path(__file__).resolve().parent / "vendor"
for vendored_custom_components_path in sorted(VENDOR_PATH.glob("*/custom_components")):
    vendored_repository_path = str(vendored_custom_components_path.parent)
    if vendored_repository_path not in sys.path:
        sys.path.insert(0, vendored_repository_path)
importlib.import_module("custom_components")


@pytest.fixture
def run_in_hass_loop(hass: HomeAssistant):
    def run_coroutine(coroutine):
        return hass.loop.run_until_complete(coroutine)

    yield run_coroutine

    if hass.services.has_service("automation", "turn_off"):
        run_coroutine(hass.services.async_call("automation", "turn_off", {"entity_id": ENTITY_MATCH_ALL}, blocking=True))
