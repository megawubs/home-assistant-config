# Automation-tests

BDD-tests (Gherkin, Nederlands) voor automations uit `automations.yaml`, gedraaid met
`pytest-bdd` en `pytest-homeassistant-custom-component` in een test-Home Assistant.

## Draaien

```bash
uv run pytest
```

- De versie van `pytest-homeassistant-custom-component` in `pyproject.toml` pint de Home Assistant-versie: houd die gelijk aan de live HA.
- `AUTOMATIONS_YAML_PATH=<pad>` laat de tests een ander automations-bestand gebruiken.

## Opbouw

- `features/*.feature`: de eisen als scenario's.
- `test_*.py`: step-definities; services zoals `climate.turn_off` worden gemockt.
- `automation_loader.py`: laadt één automation op id of alias en zet die op in de test-`hass`.
