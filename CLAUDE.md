# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Repository Overview

This is a Home Assistant configuration repository (version 2025.10.2) for a Dutch smart home setup. The configuration is primarily in Dutch (Nederlands), including entity names, automation aliases, and script descriptions.

## Architecture & Structure

### Configuration Split Pattern
The configuration uses Home Assistant's `!include` directive extensively to organize components:

- **Main config**: `configuration.yaml` - References all other component files
- **Modular components**: `includes/` directory contains domain-specific configurations:
  - `sensors.yaml`, `binary_sensors.yaml`, `templates.yaml`
  - `input_numbers.yaml`, `input_booleans.yaml`, `input_selects.yaml`, `input_datetimes.yaml`
  - `switches.yaml`, `covers.yaml`, `notify.yaml`
  - `rest.yaml`, `rest_command.yaml`, `shell_commands.yaml`
  - `utility_meters.yaml`, `calendar.yaml`, `homekit.yaml`
- **Top-level files**:
  - `automations.yaml` - All automations (very large file, ~4600+ lines)
  - `scripts.yaml` - Reusable scripts
  - `scenes.yaml` - Scene definitions
  - `groups.yaml` - Entity groupings

### Key Integrations & Features

**Database**: Uses external PostgreSQL database (connection via `!secret db_url` in recorder config)

**ESPHome**: Contains ESPHome device configurations in `esphome/` directory including:
- M5Paper displays for climate control
- M5Stack Core2
- Custom room dials and controls

**ZHA (Zigbee)**: Custom quirks stored in `zha/quirks/` directory with OTA updates enabled for IKEA devices

**Energy Management**: Advanced energy optimization features:
- Uses a custom Jinja macro `cheapest_energy_hours.jinja` (imported from `custom_templates/`, which is .gitignored)
- Calculates optimal times to run appliances based on energy tariffs
- Integrates with HomeConnect appliances (washer/dryer) using `homeconnect_ws.start_program` with `finish_in` attribute
- See automations.yaml:4646 and automations.yaml:4676 for examples of scheduled appliance starts

**Template Sensors**: Complex templating in `includes/templates.yaml` includes:
- Energy calculations (self-sufficiency scores, consumption tracking)
- Activity detection across multiple rooms
- Climate control optimization for air conditioning units
- Timestamp-based scheduling using trigger templates

**Blueprints**: Custom automation blueprints stored in `blueprints/automation/`

### Important Patterns

**Language**: All user-facing text is in Dutch. Entity IDs, automation aliases, script names, and comments are in Dutch.

**Secrets**: Uses `!secret` directive for sensitive data. Never commit `secrets.yaml` (gitignored).

**Binary Sensors**: Extensive use of template binary sensors with `delay_off` for activity detection (e.g., "activiteit in huis" patterns)

**Climate Control**:
- Multiple climate entities (thermostaat, airco units)
- Input numbers for temperature thresholds (verwarming_hoog, verwarming_laag, etc.)
- Dynamic temperature calculations based on outdoor conditions

**Heating Scripts**: Central heating control scripts:
- `verwarmen` - Heat house to high temperature
- `verwaring_minimaal` - Set to minimum temperature
- Similar patterns for office (kantoor) heating

**Notifications**: Mobile notifications via `notify.mobile_app_iphone_van_bram`

## Development Workflow

### Testing Configuration
```bash
# Home Assistant config check (must be run from HA container or with HA CLI)
ha core check

# For ESPHome devices
cd esphome
esphome compile <device>.yaml
esphome upload <device>.yaml
```

### Working with Automations
- Main automations are in `automations.yaml` - this file is managed by the UI
- When editing automations programmatically, be careful to preserve the YAML structure
- Each automation has a unique `id` field (UUID format)
- Automations use `triggers`, `conditions`, and `actions` (not the old `trigger`, `condition`, `action`)

### Template Development
- Template sensors use Jinja2 syntax
- Custom Jinja macros are in `custom_templates/` (gitignored - not version controlled)
- The `cheapest_energy_hours` macro is used for energy optimization scheduling
- Always test templates in Developer Tools > Template before committing

### Energy Optimization
When working with energy-based automations:
- The `sensor.current_tariff` provides current energy pricing
- Use the `cheapest_energy_hours` macro to find optimal time windows
- Pattern: Calculate `start_time`, `end_time`, then derive `hours` and `minutes` for `finish_in` parameter
- See the washer/dryer automations (around line 4640-4686) for reference implementations

## Git Workflow

**Current branch**: `trunk` (this is the main branch, not `main` or `master`)

**Ignored directories** (see .gitignore):
- `custom_components/` - Custom integrations
- `custom_templates/` - Custom Jinja macros
- `themes/` - UI themes
- `.storage/` - HA runtime storage
- ESPHome build artifacts

## Common Entity Patterns

**Activity Detection**: Binary sensors named `activiteit_*` or `beweging_*` (movement)
**Climate**: Entities prefixed with `airco_*` or containing `thermostaat`
**Energy**: Sensors containing `zonneplan_*`, `energy_*`, `power_*`
**Input Helpers**: Prefixed with `input_number.*`, `input_boolean.*`, etc.

## Context Documentation

The `.context/` directory (gitignored) contains detailed technical documentation about ongoing work, decisions, and implementation details:

- **Purpose**: Preserve conversation context, technical decisions, and implementation details for future AI sessions
- **Format**: Markdown files with descriptive names
- **Not committed**: These are local working notes that don't need version control
- **When to use**: Complex multi-session tasks, feature implementations, troubleshooting sessions

**Active context files:**
- `zolder-verlichting-zones-optimalisatie.md` - Attic lighting automation with distance-based zones
- `batterij-laden-goedkope-stroom.md` - Battery charging optimization based on electricity prices
- `troubleshooting-guide.md` - Comprehensive troubleshooting guide with lessons learned (disk management, LD2410 sensors, add-on configuration)
- `toekomstige-projecten.md` - Future project ideas and improvements

When working on existing features or debugging, check `.context/` for relevant documentation that provides background, decisions made, and current status.

**For troubleshooting:**
- Disk full / HAOS issues → See `.context/troubleshooting-guide.md`
- LD2410 sensor issues → See `.context/troubleshooting-guide.md` section on sensors
- Add-on configuration → See `.context/troubleshooting-guide.md` add-on management section

## Notes for AI Assistants

- Preserve Dutch language in all user-facing strings
- When creating new automations, use the modern `triggers`/`conditions`/`actions` format
- Always use unique IDs for automations (UUID format)
- Be mindful of the split configuration structure - changes often need to be made in `includes/` directory
- The `custom_templates/` directory exists but is not in version control - reference the macro imports in existing code
- Energy optimization automations are complex - study existing patterns before modifying
- **Document complex work**: Create/update `.context/` files for multi-session tasks or complex features
- **Check context first**: Before starting work, check if there's relevant `.context/` documentation
