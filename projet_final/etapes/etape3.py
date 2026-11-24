"""Étape 3 : discuter avec un coloc qui répond d'après sa fiche et se souvient."""
import sys
from pathlib import Path

# Permet d'importer donnees, ia et jeu, qui sont dans le dossier au-dessus
sys.path.append(str(Path(__file__).parent.parent))

import donnees
import ia
import jeu

MODELE = "lfm3-omni"

affaire, suspects = donnees.charger_affaire(1)
print(affaire["titre"])
print(affaire["description"])

noms = [s["nom"] for s in suspects]
nom = input(f"\nÀ qui veux-tu parler ? ({', '.join(noms)}) : ")
suspect = [s for s in suspects if s["nom"] == nom][0]

prompt = jeu.construire_prompt(affaire, suspect, suspects)
historique = []

print(f"\nTu parles à {nom} (tape 'fin' pour arrêter).")
while True:
    question = input("\nToi : ")
    if question == "fin":
        break
    replique = ia.repondre(MODELE, prompt, historique, question)
    print(f"{nom} :", replique)

    historique.append({"role": "user", "content": question})
    historique.append({"role": "assistant", "content": replique})