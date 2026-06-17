# M5Paper Airco-paneel — ESPHome

Bedieningspaneel op een **originele M5Paper (1e gen, ESP32-D0WDQ6-V3)** met e-ink
(IT8951) en capacitieve touch (GT911). Permanent via USB gevoed.

Config: [`m5paper-airco.yaml`](m5paper-airco.yaml) · helpers: [`hfiles/m5paper_airco.h`](hfiles/m5paper_airco.h)

## Twee schermen + navigatie

Het paneel heeft twee schermen (één display-lambda, geschakeld via de global
`current_screen`: 0 = hoofdscherm, 1 = airco). **Default = hoofdscherm.** De
navigatie-/terug-knop staat op beide schermen op exact dezelfde plek (`648,416,280,92`,
rechtsonder) en toggelt het scherm. Na **~2 min inactiviteit** op het airco-scherm springt
het paneel automatisch terug naar het hoofdscherm (`idle_min`-teller, gereset bij elke tik).
Een schermwissel is een bewuste, volledige e-ink-refresh.

**Hoofdscherm:** datum-hero links (weekdag/dag/maand uit de RTC + "N afspraken vandaag") en
rechts de agenda — vandaag-events, op tijd gesorteerd, met "Hele dag"-badge en "+N meer
vandaag"-teller; lege staat = "Geen afspraken vandaag". Rechtsonder de **Klimaat ›**-knop.

> **Agenda-databron — vereist HA-deploy.** De agenda komt van de template-sensor
> `sensor.m5paper_agenda` (toegevoegd in [`includes/templates.yaml`](../includes/templates.yaml)):
> een trigger-based sensor die elke 5 min `calendar.get_events` aanroept voor
> `calendar.gezin` / `bram` / `maninne` / `jozua` / `anne_lize`, samenvoegt + sorteert, en
> afvlakt naar `state` (count) + attributen `more` en `i1`..`i4` ("HH:MM|titel", lege tijd =
> hele-dag, titel voorgekapt op 30). ESPHome leest die via `${agenda_entity}`. **Tot deze
> sensor op de live HA staat (config deployen + `template.reload`), toont het hoofdscherm
> "Geen afspraken vandaag".** Geen werk/privé-onderscheid (werkagenda staat op een ander
> scherm).

## Airco-scherm — functies

| Zone | Entity | Actie |
|------|--------|-------|
| Kamertemperatuur (groot) | `sensor.luchtkwaliteitsensor_zolder_temperatuur` | losse master-bedroom sensor (nauwkeuriger dan airco-intern) |
| Doeltemp readout + Temp − / + | `climate.airco_boven` | `climate.set_temperature` (±0,5 °C) |
| Ventilator − / + | `climate.airco_boven` | `climate.set_fan_mode` → stappen door `auto / 1 Lowest / 2 Low / 3 High / 4 Highest` |
| Koel / Warm / Droog / Uit (2×2) | `climate.airco_boven` | `climate.set_hvac_mode` → `cool` / `heat` / `dry` / `off` |
| Stand (swing, 2×3) | `climate.airco_boven` | `climate.set_swing_mode` → `Up/Down Auto` / `Highest` / `Middle` / `Normal` / `Lowest` / `3D Auto` |
| ‹ Terug | — | terug naar hoofdscherm (zelfde knop-plek als Klimaat ›) |

Boven (beide schermen): statusbalk (tijd, on-board temp/vocht via SHT30, wifi-indicator).
Layout is **landscape 960×540** (de M5Paper-behuizing is staand → het paneel staat dwars).
De **nachtlampjes-toggle is verwijderd** (de lamp heeft al een eigen schakelaar); de
swing-grid is daardoor omhoog geschoven (rijen y150/238/326).

> De **horizontale** swing zit níet op het paneel (bewuste keuze). De climate-entiteit
> claimt de feature-bit niet (`supported_features=425`), maar de integratie biedt 'm wél
> via een aparte select: `select.airco_boven_horizontal_swing_direction` (8 standen,
> `select.select_option`). Bewust weggelaten omdat die zelden wordt versteld — instellen
> kan via HA zelf. De **verticale** swing op het paneel gebruikt `climate.set_swing_mode`
> (= `select.airco_boven_vertical_swing_direction`). Lamp (`switch.slaapkamer`) en VW ID.5
> zijn eruit gehaald: de lamp heeft al een eigen schakelaar ernaast.

---

## Waarom de oude config nooit werkte (en wat gefixt is)

Twee blokkades op **ESPHome 2026.3.0**, beide opgelost:

1. **GT911 touch — config faalde.** ESPHome 2026.3.0 (PR #14358) eist dat de
   GT911 `interrupt_pin` output-capable is. De M5Paper bedraadt die op **GPIO36**,
   wat *input-only* is → validatie-fout. **Fix:** `interrupt_pin` weggelaten → de
   GT911 valt terug op **polling** (door ESPHome-maintainers bevestigd in
   [esphome#14953](https://github.com/esphome/esphome/issues/14953)). Bij USB-voeding
   is polling prima.

2. **Boot-crashloop in de e-ink driver.** `IT8951ESensor::clear()` schrijft de hele
   framebuffer (960×540÷4 = **129.600** SPI-transacties) in één blokkerende lus tijdens
   `on_boot`. Dat duurt > 5 s → **task-watchdog timeout** → abort → boot loop → safe mode.
   Dit is dé reden dat het apparaat "nooit goed werkte". **Fix:** `App.feed_wdt()` in de lus.

3. **Trage redraw hongerde de API/touch uit → acties werkten niet.** Dezelfde lussen
   toggelden CS per woord (130k losse SPI-transacties ≈ **27 s** per redraw). Tijdens
   die blokkades werd de native API niet bediend (`api took a long time (27826 ms)`) en
   de GT911 niet gepold → `homeassistant.action`-calls kwamen nooit aan en tikken gingen
   verloren. **Fix:** burst-write — bouw de woorden in `should_write_buffer_` (gealloceerd
   maar verder ongebruikt) en stuur ze in **één `write_array16`** met één `0x0000`
   write-data preamble (pack-write staat aan via `I80CPCR`). Redraw ≈ 27 s → ~2 s.

4. **Touch 90° geroteerd + gespiegeld t.o.v. het display.** De GT911 (native 540×960
   portret) lijnt niet vanzelf uit op de 960×540 landscape-framebuffer: empirisch
   (hoek-tikken) is `display_x ↔ raw_y` recht en `display_y ↔ raw_x` geïnverteerd.
   Tikken landden buiten de zones. **Fix:** `transform: {swap_xy: true, mirror_y: true}`
   op de touchscreen (zones blijven in display-coördinaten).

Daarnaast was de `it8951e` al lokaal gepatcht voor 2026.x: `get_loop_priority()` is geen
`override` meer (de methode is uit de baseclass verwijderd). Alle driver-patches staan in
[`components/it8951e/it8951e.cpp`](components/it8951e/it8951e.cpp).

---

## Feedback-snelheid: optimistic UI + partial refresh

E-ink is traag (de waveform-tijd is fysica), dus de waargenomen reactiesnelheid is in
twee lagen aangepakt:

1. **Optimistic UI (YAML).** Bij een tik wordt direct een lokale "pending"-staat gezet
   (`opt_mode`/`opt_target`/`opt_light`) en hertekend, vóórdat HA antwoordt. De display-
   lambda leest die pending-staat als die gezet is, anders de echte HA-staat.

2. **Double-flash suppressie (YAML).** De reconcile-handlers (`on_value`/`on_state` van
   `airco_hvac_mode`, `airco_target_temp`, `light_state`) tekenen alleen opnieuw als HA
   **afwijkt** van de optimistic gok. Bevestigt HA de gok, dan wordt de tweede flash
   overgeslagen. Eén flash per actie i.p.v. twee.

3. **Diff-based partial refresh + DU4 (driver).** `write_display()` vergelijkt de nieuwe
   framebuffer met de laatst getoonde (`last_buffer_`) en ververst **alleen de kleinste
   gewijzigde rechthoek** (4-uitgelijnd op x én y) met de **DU4-waveform (~120 ms)** i.p.v.
   het hele scherm met DU (~260 ms). Niets veranderd → géén flash. Boot en de 15-min/BTN
   anti-ghosting-refresh forceren een volledige schone **GC16**-refresh (`force_full_`,
   ook gezet door `clear()`).
   - De waveform staat in één constante: `PARTIAL_UPDATE_MODE` bovenin
     [`it8951e.cpp`](components/it8951e/it8951e.cpp). Oogt DU4-tekst gewassen (lager
     contrast, 4-niveau) of rendert de LUT mode 6 niet → zet hem op `UPDATE_MODE_DU`
     (260 ms, 2-niveau, crisp); de partial-region-winst blijft dan behouden.
   - **Gratis check:** in rust roept elke 60s-sensor `component.update` aan, ook bij
     ongewijzigde waarde. Met de diff levert dat een lege rechthoek → early return → géén
     flash. Stopt het paneel in rust met flashen per minuut, dan werkt de diff. Bij een tik
     hoort alleen het knop-vlak te verversen.

> **IT8951 is niet native in ESPHome** (status juni 2026) — een external component
> blijft nodig. We gebruiken `razqqm/m5paper_esphome` voor `m5paper`+`bm8563` en de
> lokaal gepatchte `it8951e`.

---

## Hardware — pinout (geverifieerd op dit toestel)

| Functie | Pin |
|---|---|
| SPI CLK / MOSI / MISO | GPIO14 / GPIO12 / GPIO13 |
| IT8951 CS / RESET / BUSY | GPIO15 / GPIO23 / GPIO27 |
| I²C SDA / SCL (GT911 + SHT30 + BM8563) | GPIO21 / GPIO22 |
| GT911 interrupt | GPIO36 — **niet gebruiken** (input-only; polling i.p.v.) |
| M5Paper battery/main power | GPIO5 / GPIO2 |
| Knoppen links / BTN / rechts | GPIO39 / GPIO38 / GPIO37 |
| Batterijspanning (ADC) | GPIO35 |
| Display native (rotation 0) | **960 × 540** (landscape) |

---

## Flashen vanaf de Mac

Vanuit de map `esphome/` met de venv (`.venv/bin/esphome`). Het toestel verschijnt als
`/dev/cu.usbserial-XXXX` (hier: `/dev/cu.usbserial-01FFB077`).

```bash
# 1. (eenmalig / na elke wijziging) valideren
.venv/bin/esphome config m5paper-airco.yaml

# 2. compileren
.venv/bin/esphome compile m5paper-airco.yaml

# 3. flashen via USB (eerste keer altijd serial)
.venv/bin/esphome upload m5paper-airco.yaml --device /dev/cu.usbserial-01FFB077

# of compile + upload + logs in één stap:
.venv/bin/esphome run m5paper-airco.yaml --device /dev/cu.usbserial-01FFB077

# serial-logs los bekijken (touch-coördinaten verschijnen hier):
.venv/bin/esphome logs m5paper-airco.yaml --device /dev/cu.usbserial-01FFB077
```

Na de eerste serial-flash kan het toestel **OTA** (mits WiFi werkt — zie hieronder):
laat `--device` dan weg.

Handige knoppen op het toestel:
- **BTN (midden, GPIO38):** forceer een volledige verversing (wist e-ink ghosting).
- Volledige reset elke 15 min automatisch tegen ghosting.

---

## Touch coördinaten-mapping

De GT911 is native **540×960 (portret)** en staat **90° gedraaid + gespiegeld** t.o.v. de
960×540 landscape-framebuffer. Empirisch bepaald door de vier getekende hoeken aan te
tikken (display-positie → ruwe touch):

| Getekende hoek | display (x,y) | raw (x,y) |
|---|---|---|
| Linksboven (klok) | 0, 0 | ~516, ~30 |
| Rechtsboven (lamp) | 960, 0 | ~510, ~940 |
| Linksonder (Uit) | 0, 540 | ~10, ~25 |
| Rechtsonder (km) | 960, 540 | ~38, ~900 |

→ `display_x ↔ raw_y` (recht), `display_y ↔ raw_x` (geïnverteerd). Daarom op de
touchscreen:

```yaml
transform:
  swap_xy: true
  mirror_x: false
  mirror_y: true
```

Daarmee leveren de touch-coördinaten exact display-coördinaten, en kloppen de zones
hieronder (die in display-coördinaten gedefinieerd zijn) 1-op-1 met de getekende layout.

**Airco-scherm — touch-zones** (display-coördinaten 960×540). Doeltemp staat als readout
rechtsboven, de mode-knoppen in een 2×2-raster, en de temp-/ventilator-stepper als
**icoon-trio's** (`[−] [icoon (+ waarde)] [+]`) op dezelfde twee rijen als de modes — één
strak knoppen-raster. Rechtsboven (waar de nachtlampjes-toggle zat) staat nu de swing-grid;
de **terug-knop** deelt de positie met de Klimaat-knop van het hoofdscherm.

```
 (0,0)                                                       (960,0)
   ┌── 19:52 ──────────── 25,5°C  55%  wifi ──────────────────┐  statusbalk h60
   ├──────────────────────────────────┬───────────────────────┤
   │ Klimaat            🌡 18,0°       │  Stand ───              │
   │   21,0°            Doeltemp.      │  ┌─────────┬─────────┐ │
   │   Huidige temp                    │  │Op/Neer  │ Hoogst  │ │ swing 2×3
   │  ┌────┬────┐  ┌──┬───┬──┐         │  │Midden   │ Normaal │ │ 648/796, w132
   │  │Koel│Warm│  │− │ 🌡 │+ │ y322   │  │Laagst   │ 3D Auto │ │ rijen y150/238/326
   │  │Droog│Uit│  │− │🌀1│+ │ y416   │  └─────────┴─────────┘ │
   │  └────┴────┘  └──┴───┴──┘         │  ┌────────────────────┐│
   │  40   180     330 .. 528          │  │   ‹ Terug          ││ 648–928 / 416–508
   └──────────────────────────────────┴───┴────────────────────┴┘
```

| Zone | x_min–x_max | y_min–y_max |
|------|-------------|-------------|
| Navigatie (Klimaat › / ‹ Terug) | 648–928 | 416–508 |
| Temp − | 330–402 | 322–406 |
| Temp + | 528–600 | 322–406 |
| Ventilator − | 330–402 | 416–500 |
| Ventilator + | 528–600 | 416–500 |
| Koel | 40–164 | 322–406 |
| Warm | 180–304 | 322–406 |
| Droog | 40–164 | 416–500 |
| Uit | 180–304 | 416–500 |
| Swing Op/Neer | 648–780 | 150–226 |
| Swing Hoogst | 796–928 | 150–226 |
| Swing Midden | 648–780 | 238–314 |
| Swing Normaal | 796–928 | 238–314 |
| Swing Laagst | 648–780 | 326–402 |
| Swing 3D Auto | 796–928 | 326–402 |

> Alle airco-zones vuren alleen als `current_screen == 1`; de navigatie-zone werkt op beide
> schermen. Op het hoofdscherm is de enige tikbare zone de Klimaat ›-knop (zelfde coördinaten).

> De calibratie-`on_touch`-log (tik → `x/y` + `raw_x/raw_y`) is verwijderd nu de zones
> kloppen. Moet je later opnieuw meten, zet 'm dan tijdelijk terug in de `touchscreen:`
> `on_touch:` met `ESP_LOGI("touch", "x=%d y=%d raw_x=%d raw_y=%d", touch.x, touch.y, touch.x_raw, touch.y_raw);`.

---

## Openstaande punten / let op

- **WiFi-secrets zijn dummy.** `esphome/secrets.yaml` bevat `wifi_ssid: "dummy_ssid"`.
  Zonder echte WiFi verbindt het toestel **niet** met Home Assistant → airco/licht/SOC
  tonen `--` en de touch-acties doen niets. **Zet hier je echte WiFi-gegevens in** en
  flash opnieuw om het paneel functioneel te maken.
- **Device-identiteit.** Deze config gebruikt bewust `name: m5paper-slaapkamer` + dezelfde
  API-key/OTA-password als de oude `m5paper-slaapkamer.yaml`, zodat HA dit als **hetzelfde
  apparaat** adopteert. Wil je een los apparaat? Geef een eigen `name` en nieuwe keys.
- **Eindcontrole na WiFi.** Tik met logs aan elke knop aan en bevestig dat de juiste
  airco-/licht-actie in HA volgt; de `on_touch`-log maakt dat eenvoudig.
- **Oude bestanden.** `m5paper-slaapkamer.yaml` (met de kapotte `interrupt_pin: GPIO36`)
  staat er nog als referentie. Verwijder zodra dit paneel bevalt.
