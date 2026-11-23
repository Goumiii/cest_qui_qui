import gradio as gr
import pandas as pd

# ===== Les données =====
AFFAIRES = pd.read_csv("data/affaires.csv", sep=";", encoding="utf-8-sig")              # étape 2
SUSPECTS = pd.read_csv("data/suspects.csv", sep=";", encoding="utf-8-sig").fillna("")   # étape 4
PARTIES = pd.read_csv("data/parties_exemple.csv", sep=";", encoding="utf-8-sig")        # étape 7

NB_QUESTIONS = 5


# ===== Les fonctions =====

# Étape 1 — Accueil
def saluer(prenom):
    if prenom.strip() == "":
        return "Dis-moi d'abord comment tu t'appelles."
    return f"Bienvenue dans la coloc, **{prenom}** !"


# Étapes 2 et 4 — Choisir une affaire : description + liste de ses colocs
def choisir_affaire(titre):
    if titre is None:
        return "", gr.update(choices=[], value=None)
    affaire = AFFAIRES[AFFAIRES["titre"] == titre].iloc[0]
    noms = SUSPECTS[SUSPECTS["affaire_id"] == affaire["affaire_id"]]["nom"].tolist()
    return affaire["description"], gr.update(choices=noms, value=noms[0])


def texte_compteur(restantes):
    return f"Questions restantes : {restantes}"


# Étapes 4 et 6 — Choisir un coloc : sa fiche, et on repart de zéro
def choisir_coloc(nom):
    if nom is None:
        return "", [], [], NB_QUESTIONS, texte_compteur(NB_QUESTIONS)
    coloc = SUSPECTS[SUSPECTS["nom"] == nom].iloc[0]
    # Défi 2 : voix féminine ou masculine
    if coloc["voix"] == "female-french":
        voix = "Voix féminine"
    else:
        voix = "Voix masculine"
    fiche = f"### {nom}\n{coloc['caractere']}\n\n*{voix}*"
    # fiche, conversation, historique, restantes, compteur
    return fiche, [], [], NB_QUESTIONS, texte_compteur(NB_QUESTIONS)


# Étape 6 — Choisir une phrase de la fiche d'après les mots de la question
def trouver_reponse(fiche, question):
    q = question.lower()
    if "soir" in q or "faisais" in q or "étais" in q:
        return fiche["alibi"]
    if "vu" in q or "entendu" in q or "remarqué" in q:
        return fiche["indice"]
    return fiche["defense"]


# Étapes 5 et 6 — Envoyer une question
def envoyer(nom, question, historique, restantes):
    if nom is None:
        raise gr.Error("Choisis d'abord un coloc.")
    if question.strip() == "":
        # On ne change rien
        return historique, historique, question, restantes, texte_compteur(restantes)
    if restantes <= 0:
        raise gr.Error("Tu n'as plus de questions.")

    fiche = SUSPECTS[SUSPECTS["nom"] == nom].iloc[0]
    reponse = trouver_reponse(fiche, question)
    historique = historique + [
        {"role": "user", "content": question},
        {"role": "assistant", "content": reponse},
    ]
    restantes = restantes - 1
    # conversation, historique, question vide, restantes, compteur
    return historique, historique, "", restantes, texte_compteur(restantes)


# Défi 1 — Recommencer
def recommencer():
    return [], [], NB_QUESTIONS, texte_compteur(NB_QUESTIONS)


# Étape 7 — Classement (exercice 1, question E4)
def classement():
    return (
        PARTIES.groupby("pseudo")
        .agg(points=("score", "sum"), parties=("score", "count"), meilleur=("score", "max"))
        .sort_values("points", ascending=False)
        .reset_index()
    )


# Défi 3 — Les parties d'une affaire
def parties_de(titre):
    if titre is None or titre == "Toutes les affaires":
        choix = PARTIES
    else:
        choix = PARTIES[PARTIES["affaire"] == titre]
    return choix[["date", "pseudo", "affaire", "score"]].sort_values("date", ascending=False)


# ===== L'écran =====
with gr.Blocks(title="L'annuaire de la coloc") as demo:
    restantes = gr.State(NB_QUESTIONS)   # étape 5
    historique = gr.State([])            # étape 6

    gr.Markdown("# L'annuaire de la coloc")

    with gr.Tab("Les colocs"):
        # Étape 3 — prénom et bouton sur la même ligne
        with gr.Row():
            prenom = gr.Textbox(label="Ton prénom", scale=3)
            bouton_saluer = gr.Button("Entrer", scale=1)
        accueil = gr.Markdown()

        # Étape 2
        choix_affaire = gr.Dropdown(AFFAIRES["titre"].tolist(), value=None, label="L'affaire")
        description = gr.Markdown()

        # Étape 3 — deux colonnes
        with gr.Row():
            with gr.Column(scale=1):
                choix_coloc = gr.Radio([], label="Le coloc")          # étape 4
                fiche = gr.Markdown()
                question = gr.Textbox(label="Ta question")             # étape 5
                bouton_envoyer = gr.Button("Envoyer")
                compteur = gr.Markdown(texte_compteur(NB_QUESTIONS))
                bouton_recommencer = gr.Button("Recommencer")          # défi 1
            with gr.Column(scale=2):
                conversation = gr.Chatbot(label="La conversation")     # étape 6

    # Étape 7 — second onglet
    with gr.Tab("Classement") as onglet_classement:
        tableau = gr.Dataframe(label="Classement des joueurs", interactive=False)
        # Défi 3
        filtre_affaire = gr.Dropdown(["Toutes les affaires"] + AFFAIRES["titre"].tolist(),
                                     value="Toutes les affaires", label="Parties d'une affaire")
        tableau_parties = gr.Dataframe(label="Parties", interactive=False)

    # ===== Les événements =====
    bouton_saluer.click(saluer, inputs=prenom, outputs=accueil)
    choix_affaire.change(choisir_affaire, inputs=choix_affaire, outputs=[description, choix_coloc])
    choix_coloc.change(choisir_coloc, inputs=choix_coloc,
                       outputs=[fiche, conversation, historique, restantes, compteur])

    entrees = [choix_coloc, question, historique, restantes]
    sorties = [conversation, historique, question, restantes, compteur]
    bouton_envoyer.click(envoyer, inputs=entrees, outputs=sorties)
    question.submit(envoyer, inputs=entrees, outputs=sorties)

    bouton_recommencer.click(recommencer, outputs=[conversation, historique, restantes, compteur])

    onglet_classement.select(classement, outputs=tableau)
    onglet_classement.select(parties_de, inputs=filtre_affaire, outputs=tableau_parties)
    filtre_affaire.change(parties_de, inputs=filtre_affaire, outputs=tableau_parties)

demo.launch()