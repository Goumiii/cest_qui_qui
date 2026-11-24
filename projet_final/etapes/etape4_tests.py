"""Étape 4 : tester le score et la preuve, sans le modèle."""
import sys
from pathlib import Path

sys.path.append(str(Path(__file__).parent.parent))

import donnees
import jeu

print("=== Score ===")
tests_score = [
    (True, True, 12, 100),
    (True, True, 0, 90),
    (True, False, 6, 45),
    (False, True, 6, 50),
    (False, False, 6, 0),
]
for coupable, preuve, restantes, attendu in tests_score:
    obtenu = jeu.calculer_score(coupable, preuve, restantes)
    etat = "OK" if obtenu == attendu else "ERREUR"
    print(f"{etat} : coupable={coupable}, preuve={preuve}, restantes={restantes} -> {obtenu} (attendu {attendu})")

print("\n=== Preuve, affaire 4 ===")
affaire, _ = donnees.charger_affaire(4)
tests_preuve = [
    ("des baskets toutes crottées", True),
    ("Des chaussures pleines de BOUE", True),
    ("un parapluie", False),
]
for description, attendu in tests_preuve:
    obtenu = jeu.preuve_valable(affaire, description)
    etat = "OK" if obtenu == attendu else "ERREUR"
    print(f"{etat} : « {description} » -> {'acceptée' if obtenu else 'refusée'}")