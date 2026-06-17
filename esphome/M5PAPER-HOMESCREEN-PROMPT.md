# Design-prompt — M5Paper: hoofdscherm (agenda) + navigatie naar airco

> Plak dit in claude.ai/design. **Voeg toe**: het bestand **"M5Paper E-ink Design System.html"**
> (het bindende design systeem) en, als je 'm hebt, de **foto van het huidige airco-scherm**.
>
> **Belangrijk: bouw nog NIET. Begin met mij te interviewen** over de design-richting — stel
> eerst je vragen (zie onderaan), wacht op mijn antwoorden, en ontwerp pas daarna.

---

Je bent een UI-designer die werkt binnen een **bestaand e-ink design systeem** voor een
**originele M5Paper (1e gen)** — een 960×540 e-ink display in **landscape**, bediend met
capacitieve touch. De UI wordt 1-op-1 met de hand in pixels getekend in een ESPHome
display-lambda (geen layout-engine); alles is absoluut gepositioneerd.

## Wat ik wil

Het paneel toont nu **continu het airco-bedienscherm**. Dat is meestal niet nuttig — ik
bedien de airco maar af en toe. Ik wil het paneel **twee schermen** geven:

1. **Hoofdscherm (nieuw, default):** een rustig overzicht met **agenda-items** (komende
   afspraken) als hoofdinhoud, plus een **navigatieknop naar de airco-bediening**.
2. **Airco-scherm (bestaand):** het huidige Klimaat-paneel, met een **terug-knop** naar
   het hoofdscherm. **De nachtlampjes-toggle mag eruit** (niet handig) — dat geeft ruimte,
   o.a. voor de terug-knop.

## Harde constraints (medium + design systeem — niet onderhandelbaar)

- **Canvas:** exact 960×540 px, landscape. Buitenmarge 16 px. Spacing op een **8px-raster**.
- **Kleur:** puur grijswaarden. Zwart `#000`, wit `#fff`, max één extra grijs voor grote
  vlakken (`#C0C0C0`). Géén chromatische kleur. Vierkante hoeken (radius 0).
- **Strokes:** 2 px (dun/onderstreping) · 3 px (randen/knoppen) · 4 px (nadruk).
- **Touch-targets:** elke tikbare zone **≥ 70 px** in beide richtingen, met zichtbare rand
  of vulling als affordance (e-ink geeft geen aanraakfeedback).
- **Typografie:** Roboto, vaste px-maten (geen schaling). NL: komma als decimaalteken.
- **Iconen:** Material Design Icons (codepoint), altijd zwart (of wit op een gevuld vlak).
- **Componenten uit het systeem** (hergebruiken): knop (outline/gevuld), toggle, waarde-
  stepper, statusbalk (tijd/temp/vocht/wifi + scheidingslijn), sectie-patroon (kop + korte
  2px-onderstreping). Het airco-scherm gebruikt al: mode-grid 2×2, temp- en ventilator-
  stepper als icoon-trio's, doeltemp-readout, en rechts een swing 2×3-grid.

## Technische context die je ontwerp stuurt

- **Twee schermen = één lambda met een paginastatus.** Navigeren is een tik die de
  paginastatus wisselt en het scherm hertekent. Op e-ink is een schermwissel een
  **volledige refresh** (~0,3–0,5 s, met flits) — dus navigatie is een *bewuste* actie,
  niet iets om vaak/snel te doen. Ontwerp de navigatie als duidelijke, losse knoppen
  (geen swipes, geen tabs-die-meescrollen).
- **Agenda-databron:** items komen uit Home Assistant **kalender-entiteiten**. Per item is
  betrouwbaar beschikbaar: **starttijd** (datum/tijd) en **titel**. Mogelijk ook: einde,
  hele-dag-vlag, locatie. Eén of meerdere kalenders kunnen gecombineerd worden (welke
  precies prik ik later — dat is config, geen design). Houd er rekening mee dat titels
  **lang** kunnen zijn (afkappen/ellipsis) en dat de lijst **leeg** kan zijn.
- **Statusbalk:** bestaat al (tijd, binnen-temp/vocht via on-board sensor, wifi). Denk na
  of die op beide schermen hetzelfde blijft.
- **Geen animatie/scroll:** statische layout; alleen waarden/markeringen wisselen, posities
  niet. Wat niet op één scherm past, past niet — geen scrollende lijst.

## Je opdracht — EERST interviewen, dan pas ontwerpen

Stel mij een gestructureerde set vragen over de **design-richting** voordat je iets tekent.
Dek in elk geval deze dimensies (vul aan waar je denkt dat het ontwerp er baat bij heeft):

1. **Hoofdscherm-hiërarchie** — is agenda het enige hoofdelement, of wil ik ook een grote
   klok/datum, het weer, of de binnentemperatuur prominent? Wat is het "hero"-element?
2. **Agenda-weergave** — hoeveel items tonen? Gegroepeerd per dag (Vandaag / Morgen) of
   gewoon de eerstvolgende N? Tijd + titel, of ook locatie/kalender-bron? Hoe hele-dag-
   afspraken tonen? Welk tijdvenster (alleen vandaag, vandaag+morgen, komende N dagen)?
   Hoe ziet "geen afspraken" eruit?
3. **Navigatie** — hoe ga ik van hoofdscherm → airco (knop met label, icoon, waar op het
   scherm)? Hoe terug? Welk scherm toont het paneel standaard/na inactiviteit; en wil ik
   automatisch terugkeren naar het hoofdscherm na X tijd?
4. **Statusbalk** — op beide schermen identiek houden? Of op het hoofdscherm vervangen door
   een grotere klok/datum (en is de balk-tijd dan dubbel)?
5. **Airco-scherm na verwijderen nachtlampjes** — wat doe ik met die vrijgekomen ruimte
   rechtsboven? (Bijv. terug-knop daar, of de swing-grid laten ademen.)
6. **Toon/stijl** — moet het hoofdscherm rustiger/luchtiger ogen dan het airco-scherm
   (meer witruimte), of juist informatiedicht?

Stel de vragen compact en concreet (met jouw aanbeveling per vraag waar je een sterke
voorkeur hebt). Als ik heb geantwoord, lever je:

- **twee 960×540 e-ink mockups** (hoofdscherm + herzien airco-scherm) in de stijl van het
  design systeem (pure grijswaarden, absoluut gepositioneerd), met de navigatie zichtbaar;
- per scherm een **coördinaten-/redline-tabel** (element + touch-zone: x, y, w, h, font,
  type), zodat ik het 1-op-1 naar de ESPHome-lambda kan overnemen;
- een korte redenering bij je layout-/ritmekeuzes (raster, witruimte, leesbaarheid).
