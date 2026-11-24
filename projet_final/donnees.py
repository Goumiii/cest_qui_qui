"""Lecture et écriture des données du jeu avec pandas (fichiers CSV)."""
from datetime import datetime
from pathlib import Path

import pandas as pd

# Tous les chemins partent du dossier de ce fichier : ça marche sur toutes les machines
DOSSIER_DATA = Path(__file__).parent / "data"
FICHIER_AFFAIRES = DOSSIER_DATA / "affaires.csv"
FICHIER_SUSPECTS = DOSSIER_DATA / "suspects.csv"
FICHIER_PARTIES = DOSSIER_DATA / "parties.csv"
FICHIER_ECHANGES = DOSSIER_DATA / "echanges.csv"

COLONNES_PARTIES = ["date", "pseudo", "affaire_id", "affaire", "accuse", "bon_coupable",
                    "preuve_acceptee", "questions_utilisees", "score", "profil"]

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


def maintenant():
    """Renvoie la date et l'heure actuelles, au format 2026-11-24T16:30:00."""
    return datetime.now().isoformat(timespec="seconds")


def ajouter_ligne(fichier, ligne):
    """Ajoute une ligne (dictionnaire) à la fin d'un CSV, en-tête compris la première fois."""
    tableau = pd.DataFrame([ligne])
    tableau.to_csv(fichier, mode="a", header=not fichier.exists(),
                   index=False, sep=SEP, encoding=ENCODAGE)


def enregistrer_echange(pseudo, affaire_id, suspect, question, replique):
    """Ajoute une question posée et sa réponse à echanges.csv."""
    ajouter_ligne(FICHIER_ECHANGES, {
        "date": maintenant(),
        "pseudo": pseudo,
        "affaire_id": affaire_id,
        "suspect": suspect,
        "question": question,
        "replique": replique,
    })


def enregistrer_partie(pseudo, affaire_id, affaire, accuse, bon_coupable,
                       preuve_acceptee, questions_utilisees, score, profil):
    """Ajoute une partie terminée à parties.csv."""
    ajouter_ligne(FICHIER_PARTIES, {
        "date": maintenant(),
        "pseudo": pseudo,
        "affaire_id": affaire_id,
        "affaire": affaire,
        "accuse": accuse,
        "bon_coupable": bon_coupable,
        "preuve_acceptee": preuve_acceptee,
        "questions_utilisees": questions_utilisees,
        "score": score,
        "profil": profil,
    })


def lire_parties():
    """Renvoie le tableau des parties, ou un tableau vide si aucune partie n'a été jouée."""
    if not FICHIER_PARTIES.exists():
        return pd.DataFrame(columns=COLONNES_PARTIES)
    return pd.read_csv(FICHIER_PARTIES, sep=SEP, encoding=ENCODAGE)


def classement():
    """Points, nombre de parties et meilleur score par joueur, du meilleur au moins bon."""
    parties = lire_parties()
    if parties.empty:
        return pd.DataFrame(columns=["pseudo", "points", "parties", "meilleur"])
    return (
        parties.groupby("pseudo")
        .agg(points=("score", "sum"), parties=("score", "count"), meilleur=("score", "max"))
        .sort_values("points", ascending=False)
        .reset_index()
    )


def stats_par_affaire():
    """Pour chaque affaire : parties jouées, taux de réussite en % et questions moyennes."""
    parties = lire_parties()
    if parties.empty:
        return pd.DataFrame(columns=["affaire", "parties", "reussite_%", "questions_moyennes"])
    parties["bon_coupable"] = parties["bon_coupable"].astype(bool)
    stats = parties.groupby("affaire").agg(
        parties=("score", "count"),
        reussite=("bon_coupable", "mean"),
        questions_moyennes=("questions_utilisees", "mean"),
    )
    stats["reussite"] = (stats["reussite"] * 100).round(0)
    stats["questions_moyennes"] = stats["questions_moyennes"].round(1)
    stats = stats.rename(columns={"reussite": "reussite_%"})
    return stats.sort_values("parties", ascending=False).reset_index()


# ===== Vérification =====
if __name__ == "__main__":
    affaire, suspects = charger_affaire(1)
    print(affaire["titre"])
    for s in suspects:
        print(s["nom"], "-", s["caractere"], "- coupable :", s["coupable"])
    print("\nClassement :")
    print(classement())
    print("\nStatistiques par affaire :")
    print(stats_par_affaire())