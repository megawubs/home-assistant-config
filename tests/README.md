# Automation-tests

BDD-tests (Gherkin, Nederlands) voor automations uit `automations.yaml` en de climate-template
uit `includes/climate.yaml`, gedraaid met `pytest-bdd` en `pytest-homeassistant-custom-component`
in een test-Home Assistant.

## Draaien

```bash
uv run pytest
```

- De versie van `pytest-homeassistant-custom-component` in `pyproject.toml` pint de Home Assistant-versie: houd die gelijk aan de live HA.
- `AUTOMATIONS_YAML_PATH=<pad>` laat de tests een ander automations-bestand gebruiken.
- `CLIMATE_YAML_PATH=<pad>` laat de tests een ander climate-bestand gebruiken, bv. de vorige versie:
  `git show HEAD:includes/climate.yaml > /tmp/climate.yaml && CLIMATE_YAML_PATH=/tmp/climate.yaml uv run pytest`.

## Opbouw

- `features/*.feature`: de eisen als scenario's.
- `test_*.py`: step-definities; services zoals `climate.turn_off` worden gemockt.
- `automation_loader.py`: laadt één automation op id of alias en zet die op in de test-`hass`.
- `climate_loader.py`: laadt één climate-entry op `unique_id` uit `includes/climate.yaml` en zet die op.
- `conftest.py`: gedeelde fixtures, en voegt `vendor/*/custom_components` toe aan de `custom_components` van de test-HA.

## Gevendorde custom integration

Custom integrations staan als git-submodule onder `vendor/`, vastgezet op dezelfde versie als live (HACS):

- `vendor/hass-template-climate`: [jcwillox/hass-template-climate](https://github.com/jcwillox/hass-template-climate) op tag `v1.4.2`.

Na een clone: `git submodule update --init`. Bijwerken na een update in HACS:

```bash
git -C tests/vendor/hass-template-climate fetch --tags
git -C tests/vendor/hass-template-climate checkout <nieuwe-tag>
uv run pytest
```

## Stappen

- **Generiek** (`conftest.py`), bruikbaar in elke feature:
  - `Gegeven de entity "<entity_id>" staat op "<state>"`
  - `Gegeven de entity "<entity_id>" heeft attribuut "<attribuut>" met waarde <waarde>`
  - `Als de entity "<entity_id>" op "<state>" wordt gezet` (laat daarna 60 s verstrijken voor `delay`s)
  - `Dan staat de entity "<entity_id>" op "<state>"`
  - `Dan heeft de entity "<entity_id>" attribuut "<attribuut>" met waarde <waarde>`
- **Domein** (`conftest.py` als ze door meerdere features gebruikt worden, anders in `test_*.py`):
  woorden voor gedrag, zoals `geforceerd verwarmen staat aan`. Ze roepen alleen functies uit
  `ha_test_helpers.py` aan en bevatten geen eigen logica.

