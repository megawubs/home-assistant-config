# language: nl
Functionaliteit: Airco Woonkamer
  Als bewoner wil ik dat de airco in de woonkamer en keuken direct uitgaat
  wanneer ik een geforceerde modus uitzet en er niets te doen is,
  zodat de airco niet onnodig blijft draaien.

  Achtergrond:
    Gegeven de handmatige override van de airco woonkamer staat uit
    En de airco woonkamer mag aan volgens het schema
    En geforceerd verwarmen staat aan
    En geforceerd afkoelen staat uit

  Scenario: Automatisch kiezen terwijl er niets te doen is zet de airco direct uit
    Gegeven afkoelen, verwarmen en ventileren zijn niet nodig
    En de airco woonkamer staat op "heat"
    En de automation "Airco Woonkamer" is actief
    Als geforceerd verwarmen wordt uitgezet
    Dan wordt de airco beneden direct uitgezet

  Scenario: Automatisch kiezen terwijl verwarmen nodig is laat de airco aan
    Gegeven afkoelen en ventileren zijn niet nodig
    En verwarmen is wel nodig
    En de airco woonkamer staat op "heat"
    En de automation "Airco Woonkamer" is actief
    Als geforceerd verwarmen wordt uitgezet
    Dan wordt de airco beneden niet uitgezet

  Scenario: De airco staat al uit
    Gegeven afkoelen, verwarmen en ventileren zijn niet nodig
    En de airco woonkamer staat op "off"
    En de automation "Airco Woonkamer" is actief
    Als geforceerd verwarmen wordt uitgezet
    Dan wordt de airco beneden niet uitgezet
