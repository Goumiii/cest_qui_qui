"""Lecture et écriture des données du jeu avec pandas (fichiers CSV)."""
from pathlib import Path

import pandas as pd

# Tous les chemins partent du dossier de ce fichier : ça marche sur toutes les machines
DOSSIER_DATA = Path(__file__).parent / "data"
FICHIER_AFFAIRES = DOSSIER_DATA / "affaires.csv"
FICHIER_SUSPECTS = DOSSIER_DATA / "suspects.csv"

SEP = ";"
ENCODAGE = "utf-8-sig"


def lire_affaires():
    """Renvoie le tableau de toutes les affaires."""
    return pd.read_csv(FICHIER_AFFAIRES, sep=SEP, encoding=ENCODAGE)


def lire_suspects(affaire_id):
    """Renvoie le tableau des trois colocs d'une affaire."""
    suspects = pd.read_csv(FICHIER_SUSPECTS, sep=SEP, encoding=ENCODAGE).fillna("")
    suspects["coupable"] = suspects["coupable"] == "oui"
    return suspects[suspects["affaire_id"] == affaire_id]


def charger_affaire(affaire_id):
    """Renvoie l'affaire (dictionnaire) et ses colocs (liste de dictionnaires)."""
    affaires = lire_affaires()
    affaire = affaires[affaires["affaire_id"] == affaire_id].iloc[0].to_dict()
    suspects = lire_suspects(affaire_id).to_dict("records")
    return affaire, suspects


# ===== Vérification de l'étape 2 =====
if __name__ == "__main__":
    affaire, suspects = charger_affaire(1)
    print(affaire["titre"])
    for s in suspects:
        print(s["nom"], "-", s["caractere"], "- coupable :", s["coupable"])
        