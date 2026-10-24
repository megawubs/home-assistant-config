# language: nl
Functionaliteit: Climate-template Woonkamer
  De climate-template woonkamer is een proxy voor de automation "Airco Woonkamer":
  de thermostaatkaart bedient de moet_*-vlaggen en drempelwaarden, niet de unit zelf.
  Automatisch (geen vlag aan) betekent: de automation beslist. De kaart toont dan
  altijd "auto" en de doeltemperatuur die de automation op dat moment gebruikt.

  Achtergrond:
    Gegeven het is 20 graden in de woonkamer
    En de verwarm-drempel van de woonkamer is 21 graden
    En de koel-drempel van de woonkamer is 25 graden
    En het is stookseizoen onder 12 graden buiten

  Scenario: Automatisch toont auto, ook als de unit verwarmt
    De automation heeft zelf voor verwarmen gekozen; dat is geen keuze van de bewoner,
    dus de kaart blijft op auto staan.
    Gegeven geen geforceerde stand staat aan
    En het is 5 graden buiten
    En de airco woonkamer staat op "heat"
    En de climate-template woonkamer is actief
    Dan staat de woonkamer op "auto"

  Scenario: Automatisch in het stookseizoen toont en wijzigt de verwarm-drempel
    In het stookseizoen verwarmt de automation naar de verwarm-drempel. Een andere
    doeltemperatuur kiezen past die drempel aan en laat de automation beslissen,
    in plaats van verwarmen te forceren.
    Gegeven geen geforceerde stand staat aan
    En het is 5 graden buiten
    En de airco woonkamer staat op "heat"
    En de climate-template woonkamer is actief
    Dan toont de woonkamer een doeltemperatuur van 21 graden
    Als de doeltemperatuur van de woonkamer op 22 graden wordt gezet
    Dan is de verwarm-drempel van de woonkamer 22 graden
    En is de koel-drempel van de woonkamer 25 graden
    En staat geforceerd verwarmen uit
    En staat de woonkamer op "auto"

  Scenario: Automatisch buiten het stookseizoen toont en wijzigt de koel-drempel
    Gegeven geen geforceerde stand staat aan
    En het is 20 graden buiten
    En de airco woonkamer staat op "cool"
    En de climate-template woonkamer is actief
    Dan toont de woonkamer een doeltemperatuur van 25 graden
    Als de doeltemperatuur van de woonkamer op 23 graden wordt gezet
    Dan is de koel-drempel van de woonkamer 23 graden
    En is de verwarm-drempel van de woonkamer 21 graden
    En staat de woonkamer op "auto"

  Scenario: Geforceerd verwarmen toont en wijzigt de verwarm-drempel, ook buiten het stookseizoen
    Gegeven geforceerd verwarmen staat aan
    En het is 20 graden buiten
    En de airco woonkamer staat op "heat"
    En de climate-template woonkamer is actief
    Dan staat de woonkamer op "heat"
    En toont de woonkamer een doeltemperatuur van 21 graden
    Als de doeltemperatuur van de woonkamer op 22 graden wordt gezet
    Dan is de verwarm-drempel van de woonkamer 22 graden

  Scenario: Geforceerd afkoelen toont de koel-drempel, ook in het stookseizoen
    Gegeven geforceerd afkoelen staat aan
    En het is 5 graden buiten
    En de airco woonkamer staat op "cool"
    En de climate-template woonkamer is actief
    Dan staat de woonkamer op "cool"
    En toont de woonkamer een doeltemperatuur van 25 graden

  Scenario: Geforceerd verwarmen terwijl de unit uit staat toont uit
    De automation zet de unit uit als er een raam open staat; de kaart laat zien
    dat er op dit moment niet verwarmd wordt.
    Gegeven geforceerd verwarmen staat aan
    En het is 5 graden buiten
    En de airco woonkamer staat op "off"
    En de climate-template woonkamer is actief
    Dan staat de woonkamer op "off"

  Scenario: Moet uit toont uit, ook als de unit nog draait
    Gegeven de woonkamer moet uit
    En het is 5 graden buiten
    En de airco woonkamer staat op "heat"
    En de climate-template woonkamer is actief
    Dan staat de woonkamer op "off"
