# Prompt voor Claude design-tooling — e-ink design system M5Paper

Plak de prompt hieronder ongewijzigd in Claude's design-tooling (Figma MCP /
"Claude design"). Hij is zelf-bevattend: alle hardware- en ESPHome-constraints
staan erin, en de gevraagde output is gespiegeld in zes secties zodat het ontwerp
1-op-1 naar de display-lambda te vertalen is.

---

```text
# Opdracht: E-ink design system voor M5Paper Home Assistant bedieningspaneel

Ontwerp een compleet, herbruikbaar **design system** voor een bestaand Home
Assistant bedieningspaneel dat draait op een originele M5Paper. Lever het op als
(a) tokens, (b) componentbibliotheek, (c) één voorbeeldscherm — bruikbaar in
Figma EN direct vertaalbaar naar ESPHome-tekencode. Maak ALLE ontwerpkeuzes zelf
(concrete hex-grijswaarden, px-maten, coördinaten, icoonset); vraag niet terug.

## 1. Doelhardware en harde beperkingen (NIET onderhandelbaar)

- **Apparaat**: originele M5Paper (1e gen, ESP32), e-ink via IT8951-controller,
  capacitieve GT911-touch, permanent op USB. Tekenen gebeurt via een C++
  "display lambda" in ESPHome.
- **Scherm**: 960 × 540 px, **landscape**. Coördinaten zijn pixels; oorsprong
  linksboven; ALLES wordt handmatig gepositioneerd — er is GEEN layout-engine,
  GEEN flexbox, GEEN auto-layout in de uitvoering.
- **E-ink, monochroom-first**: technisch 16 grijstinten (4bpp), maar snelle
  updates (DU-mode) zijn praktisch **zwart/wit (1-bit)**; volle grijsschaal
  (GC16) is traag en geeft ghosting. Ontwerp dus **hoog contrast, zwart op wit**;
  gebruik HOOGUIT 2-3 grijstinten en ALLEEN voor grote vlakken (bv. vulling van
  een actieve knop), NOOIT voor tekst, fijne details of anti-aliasing.
- **Geen animatie/feedback**: het scherm ververst alleen bij state-changes. Geen
  hover, geen transitions, geen schaduwen, geen pulse. Periodiek een volledige
  refresh tegen ghosting. Ontwerp daarom een **statische layout** waarvan alleen
  de waarden/markeringen wisselen, niet de posities.
- **"Kleur" = grijswaarde**. Geen chromatische kleur, geen CSS, geen webtech.
  Druk tokens uit als grijswaarde-hex (bv. 0x000000 zwart, 0xFFFFFF wit,
  0xC0C0C0 lichtgrijs). Dit is geen tegenspraak met "monochroom": grijswaarde-hex
  is precies wat de hardware verwacht.

## 2. Wat de uitvoering KAN tekenen (elk component MOET hiermee maakbaar zijn)

Beschikbare primitives — als een component hier niet 1-op-1 in uit te drukken is,
mag het niet in het systeem:
- `line(x1,y1,x2,y2)`
- `rectangle(x,y,w,h)` (outline) en `filled_rectangle(x,y,w,h[,color])`
- `circle(cx,cy,r)` en `filled_circle(cx,cy,r)`
- Tekst via **bitmap-fonts op vaste px-groottes**: font **Roboto** (Google
  Fonts), willekeurige px-maten. Reken op een schaal in de geest van 25 / 40 /
  80 px. Uitlijning: TOP_LEFT / CENTER / TOP_CENTER e.d.
- Iconen via **Material Design Icons** (MDI) TTF-glyphs op vaste px-maten,
  aangeroepen via codepoint (bv. `\U000F05A9`).

VERBODEN: gradients, schaduwen, anti-aliasing, afgeronde hoeken (tenzij expliciet
opgebouwd uit circle-primitives), CSS, web-componenten, iconen buiten MDI,
variabele/responsive layout.

**Touch**: aanraakzones zijn rechthoekige x/y/w/h-gebieden. Elke aanraakbare zone
moet **minimaal ~70 px hoog én breed** zijn en een **zichtbare affordance**
hebben (omkadering of gevuld vlak) — e-ink geeft geen aanraakfeedback, dus de
knop moet er als knop uitzien.

## 3. Functies die het paneel moet tonen/bedienen

Het design system moet voor al deze functies een component leveren:
- **Statusbalk (boven)**: tijd, binnentemperatuur + luchtvochtigheid,
  wifi-indicator (icoon), afsluitende scheidingslijn.
- **HVAC-blok**: grote huidige kamertemperatuur; doeltemperatuur met **− / +**
  stappers; een **mode-grid met 4 knoppen: Koel / Warm / Droog / Uit**, waarbij
  de actieve mode visueel gemarkeerd is.
- **Licht-toggle**: één grote knop met icoon + label + **AAN/UIT**-status.
- **Voertuig (VW ID.5)**: **laadpercentage (SOC)** als horizontale balk +
  percentage + bereik in km.

## 4. Gevraagde output — lever EXACT deze zes onderdelen, in deze volgorde

### 4.1 Design tokens (e-ink-realistisch)
- **Grijswaarden-palet**: zwart + wit + max 2-3 grijstinten, elk met concrete
  hex (grijswaarde). Benoem per tint de toegestane toepassing (bv. "alleen
  vulling actieve knop").
- **Stroke-weights / lijndiktes**: concrete px-waarden (bv. dun/normaal/dik) en
  waar elk gebruikt wordt. Houd lijnen dik genoeg voor e-ink (geen 1px-haarlijnen
  voor structuur).
- **Spacing-grid**: een ~8px-achtige schaal die netjes op 960×540 past; geef de
  stappen en de buitenmarges van het scherm.
- **Hoekradius-beleid**: vrijwel zeker recht (radius 0); motiveer kort en geef
  aan waar circle-primitives eventueel hoeken simuleren.
- **Typografie-schaal**: vaste px-groottes met rol (bv. label / waarde / groot
  cijfer), font Roboto, plus MDI-icoongroottes in px. Géén variabele/relatieve
  eenheden.

### 4.2 Componentbibliotheek met redline-specs
Voor ELK component: exacte px-afmetingen, paddings, font-grootte, stroke, en alle
states. En per component een expliciete **mapping naar ESPHome-primitives**
("opgebouwd uit rectangle + filled_rectangle + 2 regels tekst op posities …").
Minimaal:
- **Knop** — states default / actief (actief = gevuld vlak of dikke rand).
- **Toggle** — states AAN / UIT (duidelijk visueel verschil zonder kleur).
- **Waarde-stepper** — `[ − ]  waarde  [ + ]`, met losse touch-zones links/rechts
  (≥70px) en de waarde in het midden.
- **Voortgangs-/SOC-balk** — outline-rechthoek + binnenvulling naar percentage;
  geef hoe de vulbreedte uit het percentage volgt.
- **Statusbalk** — vaste hoogte, posities voor tijd/temp/vocht/wifi-icoon +
  scheidingslijn.
- **Icoon-set** — zie 4.3.
- **Titel/sectie-pattern** — hoe een sectiekop + scheidingslijn eruitziet.

### 4.3 Iconografie (concrete MDI-glyphs)
Geef per benodigd icoon een concrete MDI-naam **én codepoint** (`\U000Fxxxx`):
wifi, lamp/lightbulb, sneeuwvlok (koelen), vuur/vlam (verwarmen), druppel
(drogen), power (uit), plus, min, thermometer, auto/accu (voertuig). Voeg gerust
alternatieven toe en geef per icoon de aanbevolen px-grootte.

### 4.4 Eén voorbeeld-schermlayout (960 × 540, alles op één scherm)
Plaats ALLE functies uit sectie 3 samen op één 960×540 landscape-scherm:
statusbalk + HVAC-blok (met steppers en 4-knops mode-grid) + licht-toggle +
voertuig-SOC. Dit is het ruimtebudget — laat alles passen met touch-targets
≥70px. Lever het als visueel ontwerp **plus** een **coördinaten-/zone-tabel**
(element, x, y, w, h, type, font-grootte, en voor aanraakbare elementen de
touch-zone), zodat het regelrecht naar de display-lambda te vertalen is.

### 4.5 E-ink do's & don'ts (ontwerpprincipes)
Korte, concrete lijst: hoog contrast, dikke lijnen, grote raakvlakken met
zichtbare rand, geen grijs-op-grijs voor tekst/details, ghosting beperken
(statische layout, spaarzame grijsvlakken), waarden wisselen maar posities niet.

### 4.6 Levering als herbruikbaar systeem
Bundel het bovenstaande als (a) tokens, (b) componentbibliotheek, (c)
voorbeeldscherm — zo dat het in Figma herbruikbaar is én elk element direct
vertaalbaar is naar de ESPHome-primitives uit sectie 2.

## 5. Toon en formaat
Structureer met duidelijke kopjes en lijsten. Wees concreet en getalsmatig (px,
hex, codepoints). Geen kleur-, CSS- of webterminologie — alles pixel- en
e-ink-georiënteerd.
```
