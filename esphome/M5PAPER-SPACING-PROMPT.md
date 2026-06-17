# Design-prompt — M5Paper airco-paneel: spacing-verfijning linkerpaneel

> Plak dit in claude.ai/design. **Voeg de bijgevoegde foto toe** (het paneel zoals het er
> nu uit ziet) en, als je 'm hebt, het bestand **"M5Paper E-ink Design System.html"** —
> dat is het design systeem waarbinnen dit moet blijven.

---

Je bent een UI-designer die werkt binnen een **bestaand e-ink design systeem** voor een
**originele M5Paper (1e gen)** — een 960×540 e-ink display in **landscape**, bediend met
capacitieve touch. De UI wordt 1-op-1 met de hand in pixels getekend in een ESPHome
display-lambda (geen layout-engine), dus alles is absoluut gepositioneerd.

Ik ben tevreden met het ontwerp; ik wil **alleen de verticale spacing/ritme van het
linker "Klimaat"-paneel verfijnen**. Op de bijgevoegde foto zie je dat de
**doeltemperatuur-stepper** en de **ventilator-stepper** te dicht onder elkaar staan
(slechts ~10 px tussen de temp-knoppen en het "Ventilator"-label). Het mag rustiger en
evenwichtiger ademen. Layout, functies en componenten blijven verder hetzelfde — dit is
puur een spacing-/ritme-pass.

## Harde constraints (medium + design systeem)

- **Canvas:** exact 960×540 px, landscape. Buitenmarge 16 px. Spacing op een **8px-raster**.
- **Kleur:** puur grijswaarden. Zwart `#000`, wit `#fff`, en max één extra grijs voor grote
  vlakken (`#C0C0C0`). Géén chromatische kleur. Vierkante hoeken (radius 0).
- **Strokes:** 2 px (dun, onderstreping) · 3 px (randen/knoppen) · 4 px (nadruk).
- **Touch-targets:** elke tikbare zone **≥ 70 px** in beide richtingen, met zichtbare rand
  of vulling als affordance.
- **Typografie:** Roboto, vaste px-maten (geen schaling). De grote numerieke fonts hebben
  een beperkte glyph-set (cijfers, komma, `°`, `-`). NL: komma als decimaalteken.
- **Iconen:** Material Design Icons, altijd zwart (of wit op een gevuld vlak).
- **Componenten** (uit het design systeem, ongewijzigd gebruiken):
  - *Waarde-stepper:* `[ − ]  waarde  [ + ]` — losse touch-zones, middenzone niet tikbaar.
  - *Mode-knop:* 3 px outline (default) / zwart gevuld + witte inhoud (actief).
  - *Sectie-patroon:* kop (Roboto bold) + korte 2 px onderstreping.
- **Render-realiteit:** e-ink ververst traag en partieel; houd elementen ruim gescheiden
  zodat een herteken-rechthoek van één control niet de buurcontrol raakt. Witruimte is hier
  functioneel, niet alleen esthetisch.

## Huidige layout (display-coördinaten, wat NU op het scherm staat)

**Statusbalk** (h60): tijd `14:32` @ (24,11); thermometer-icoon + binnen-temp; water-icoon
+ vocht; wifi-icoon rechts; 3 px scheidingslijn op y60.

**Linker "Klimaat"-paneel** — outline-rechthoek (16, 76, 600, 448). Dít is de zone die
herzien moet worden:

| Element | Positie (x,y) | Detail |
|---|---|---|
| "Klimaat" (kop, b28) | 40, 90 | + onderstreping 2px @ (40,128) w110 |
| Kamertemperatuur (groot, l120) | 28, 144 | bv. "24,2°" — domineert links, ~120 px hoog |
| "Huidige temperatuur" (22) | 40, 276 | label onder de grote temp |
| "Doeltemperatuur" (m24) | 330, 140 | rechter subkolom |
| doeltemp-waarde (m56) | 330, 168 | bv. "19,5°" |
| Temp − knop | rect (330, 230, 92, 80) | min-icoon |
| Temp + knop | rect (508, 230, 92, 80) | plus-icoon |
| "Ventilator" (m24) | 330, 320 | ← staat krap onder de temp-knoppen |
| Fan − knop | rect (330, 348, 84, 72) | min-icoon |
| Fan-waarde (b28) | 462, 360 | "Auto" / "1".."4", tussen de knoppen |
| Fan + knop | rect (510, 348, 84, 72) | plus-icoon |
| Mode-grid (4× knop, 126×92) | y 428 | Koel(40) · Warm(182) · Droog(324) · Uit(466) |

De **knelpunten**: tussen de temp-knoppen (eindigen y310) en "Ventilator" (y320) zit maar
10 px; tussen dat label (y320) en de fan-knoppen (y348) maar ~4 px. De rechter subkolom
(x≈330–600) voelt opgepropt, terwijl het mode-grid onderaan en de grote temp links er
losjes bij staan — het verticale ritme klopt niet.

**Rechterkolom** (ongewijzigd, alleen ter referentie): nachtlampjes-toggle (632, 76, 312,
120) bovenaan; daaronder sectie "Stand" + een 2×3 grid van swing-knoppen (verticale
louver-standen) tot y516.

## Wat ik van je wil

Een **herziene verticale indeling van het linker Klimaat-paneel** die:

1. de doeltemp-stepper en de ventilator-stepper duidelijk laat ademen (consistente,
   ruime gaps op het 8px-raster; geen 10px-knelpunten);
2. een rustig, leesbaar verticaal ritme geeft over het hele paneel (grote temp + label,
   doeltemp-blok, ventilator-blok, mode-grid) — elementen mogen herschikt of opnieuw
   uitgelijnd worden zolang alle functies behouden blijven en alles binnen het paneel
   (16,76,600,448) en de touch-target-eis (≥70px) past;
3. volledig binnen het design systeem blijft (zelfde componenten, tokens, strokes, fonts).

Lever het als een **960×540 e-ink mockup in dezelfde stijl als het design systeem**
(pure grijswaarden, absoluut gepositioneerd) **plus een coördinaten-/redline-tabel**
(x, y, w, h per element en per touch-zone), zodat ik het direct kan overnemen in de
ESPHome-lambda. Werk alleen het linkerpaneel uit; laat statusbalk en rechterkolom zoals ze
zijn (toon ze evt. grijs/ingeklapt als context). Geef kort je redenering bij de
spacing-keuzes (welk ritme/raster je aanhoudt en waarom).
