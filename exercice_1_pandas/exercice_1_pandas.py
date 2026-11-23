import pandas as pd

# ===== Partie A — Lire et explorer =====

# A1. Lire les deux fichiers
affaires = pd.read_csv("data/affaires.csv", sep=";", encoding="utf-8-sig")
suspects = pd.read_csv("data/suspects.csv", sep=";", encoding="utf-8-sig")

# A2. Taille des tableaux (lignes, colonnes)
print("A2 - Taille affaires :", affaires.shape)
print("A2 - Taille suspects :", suspects.shape)

# A3. Nom des colonnes
print("\nA3 - Colonnes affaires :", affaires.columns.tolist())
print("A3 - Colonnes suspects :", suspects.columns.tolist())
# Colonne commune : affaire_id

# A4. Trois premières lignes des colocs, 3 colonnes seulement
print("\nA4 -")
print(suspects[["affaire_id", "nom", "caractere"]].head(3))

# ===== Partie B — Sélectionner =====

# B1. La colonne des titres
print("\nB1 -")
print(affaires["titre"])

# B2. Nom et voix des cinq premiers colocs
print("\nB2 -")
print(suspects[["nom", "voix"]].head(5))

# B3. Noms des colocs de l'affaire 3, en liste
print("\nB3 -", suspects[suspects["affaire_id"] == 3]["nom"].tolist())

# B4. Numéro d'affaire et nom des coupables
coupables = suspects[suspects["coupable"] == "oui"]
print("\nB4 -")
print(coupables[["affaire_id", "nom"]])

# B5. Innocents ET voix féminine
innocentes = suspects[(suspects["coupable"] == "non") & (suspects["voix"] == "female-french")]
print("\nB5 -", innocentes["nom"].tolist())

# B6. Fiche de Jules en dictionnaire, puis son alibi
jules = suspects[suspects["nom"] == "Jules"].iloc[0].to_dict()
print("\nB6 -", jules["alibi"])

# ===== Partie C — Transformer =====

# C1. Colonne est_coupable (True/False), puis nombre de coupables
suspects["est_coupable"] = suspects["coupable"] == "oui"
print("\nC1 - Nombre de coupables :", suspects["est_coupable"].sum())

# C2. Nombre de colocs par voix
print("\nC2 -")
print(suspects["voix"].value_counts())

# C3. Longueur de l'alibi, puis les trois plus longs
suspects["longueur_alibi"] = suspects["alibi"].str.len()
print("\nC3 -")
print(suspects.sort_values("longueur_alibi", ascending=False)[["nom", "longueur_alibi"]].head(3))

# C4. Le coloc dont l'indice contient "20h"
print("\nC4 -")
print(suspects[suspects["indice"].str.contains("20h")][["affaire_id", "nom"]])

# C5. Cases vides de "faille", avant et après fillna
print("\nC5 - Cases vides avant :", suspects["faille"].isna().sum())
suspects = suspects.fillna("")
print("C5 - Cases vides après :", suspects["faille"].isna().sum())

# ===== Partie D — Croiser deux tableaux =====

# D1. Titre de chaque affaire + nom de son coupable
coupables = suspects[suspects["est_coupable"]]
affaires_coupables = pd.merge(affaires, coupables, on="affaire_id")
print("\nD1 -")
print(affaires_coupables[["titre", "nom"]])

# D2. Nombre de colocs par affaire
print("\nD2 -")
print(suspects.groupby("affaire_id")["nom"].count())

# ===== Partie E — Regrouper et classer =====

# E1. Lire les parties et compter
parties = pd.read_csv("data/parties_exemple.csv", sep=";", encoding="utf-8-sig")
print("\nE1 - Nombre de parties :", len(parties))

# E2. Score moyen (arrondi) et meilleur score
print("\nE2 - Moyenne :", round(parties["score"].mean(), 1))
print("E2 - Maximum :", parties["score"].max())

# E3. La meilleure partie
meilleure = parties.sort_values("score", ascending=False).iloc[0]
print("\nE3 -", meilleure["pseudo"], "|", meilleure["affaire"], "|", meilleure["score"])

# E4. Classement des joueurs
classement = (
    parties.groupby("pseudo")
    .agg(points=("score", "sum"), parties=("score", "count"), meilleur=("score", "max"))
    .sort_values("points", ascending=False)
)
print("\nE4 -")
print(classement)

# E5. Taux de réussite par affaire, en %
taux = (parties.groupby("affaire")["bon_coupable"].mean() * 100).round(0).sort_values()
print("\nE5 -")
print(taux)

# E6. Parties de Lina, de la plus récente à la plus ancienne
lina = parties[parties["pseudo"] == "Lina"].sort_values("date", ascending=False)
print("\nE6 -")
print(lina[["date", "affaire", "score"]])

# ===== Partie F — Enregistrer =====
from pathlib import Path

# F1. Enregistrer le classement
classement.reset_index().to_csv("data/classement.csv", sep=";", encoding="utf-8-sig", index=False)
print("\nF1 - Classement enregistré dans data/classement.csv")

# F2. Ajouter une partie sans effacer le fichier
fichier = Path("data/mes_parties.csv")
ma_partie = pd.DataFrame([{"pseudo": "Moi", "affaire_id": 1, "score": 95}])
ma_partie.to_csv(fichier, mode="a", header=not fichier.exists(),
                 index=False, sep=";", encoding="utf-8-sig")
print("\nF2 -")
print(pd.read_csv(fichier, sep=";", encoding="utf-8-sig"))

# ===== Défi =====
def classement_de(affaire_id):
    une_affaire = parties[parties["affaire_id"] == affaire_id]
    return une_affaire.groupby("pseudo")["score"].max().sort_values(ascending=False)

print("\nDéfi - classement_de(1) :")
print(classement_de(1))