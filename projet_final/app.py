"""L'interface du jeu dans le navigateur, avec Gradio. Ce fichier ne contient aucune règle."""
import gradio as gr

import donnees
import jeu

TITRE = "C'est Qui Qui ?"
REGLES = (
    "Un méfait a été commis dans la coloc. Questionne les trois colocs : "
    "deux disent la vérité, le troisième ment. "
    f"Tu as **{jeu.QUESTIONS_PAR_PARTIE} questions** en tout. "
    "Ensuite, désigne le coupable et présente la pièce à conviction qui le trahit."
)

AFFAIRES = donnees.lire_affaires()
TITRES = AFFAIRES["titre"].tolist()


# ===== Petites fonctions d'affichage =====
def texte_compteur(partie):
    """Renvoie le texte du compteur de questions."""
    if partie is None:
        return f"Questions restantes : {jeu.QUESTIONS_PAR_PARTIE} / {jeu.QUESTIONS_PAR_PARTIE}"
    return f"Questions restantes : **{partie.questions_restantes}** / {jeu.QUESTIONS_PAR_PARTIE}"


def texte_caractere(partie, nom):
    """Renvoie la fiche visible d'un coloc : son nom et son caractère."""
    suspect = jeu.trouver_suspect(partie, nom)
    return f"### {nom}\n*{suspect['caractere']}*"


def texte_verdict(verdict):
    """Met en forme le verdict de l'accusation."""
    lignes = ["## Verdict"]
    if verdict["bon_coupable"]:
        lignes.append(f"✅ **Bon coupable** : c'était bien {verdict['coupable']} !")
    else:
        lignes.append(f"❌ **Raté** : c'était {verdict['coupable']}.")
    if verdict["preuve_acceptee"]:
        lignes.append("✅ **Preuve acceptée.**")
    else:
        lignes.append(f"❌ **Preuve refusée.** Il fallait : {verdict['preuve_attendue']}.")
    lignes.append(f"\n**Ce qui s'est passé :** {verdict['solution']}")
    lignes.append(f"\nQuestions utilisées : {verdict['questions_utilisees']}")
    lignes.append(f"\n# Score : {verdict['score']} / 100")
    return "\n".join(lignes)


# ===== Les fonctions reliées aux événements =====
def demarrer(pseudo, titre):
    """Bouton « Nouvelle partie » : crée la partie et remet tout l'écran à zéro."""
    if titre is None:
        raise gr.Error("Choisis d'abord une affaire.")
    affaire_id = int(AFFAIRES[AFFAIRES["titre"] == titre]["affaire_id"].iloc[0])
    partie = jeu.nouvelle_partie(pseudo, affaire_id)

    noms = [s["nom"] for s in partie.suspects]
    description = f"## {partie.affaire['titre']}\n{partie.affaire['description']}"
    return (
        partie,                                       # l'état de la partie
        description,                                  # description de l'affaire
        gr.update(choices=noms, value=noms[0]),       # choix du coloc
        texte_caractere(partie, noms[0]),             # son caractère
        [],                                           # conversation vide
        "",                                           # zone de question vide
        texte_compteur(partie),                       # compteur à 12
        gr.update(choices=noms, value=None),          # choix du coupable
        "",                                           # pièce à conviction vide
        "",                                           # verdict vide
    )


def changer_suspect(partie, nom):
    """Choix d'un coloc : affiche son caractère et sa propre conversation."""
    if partie is None or nom is None:
        return "", []
    return texte_caractere(partie, nom), list(partie.historiques[nom])


def envoyer(partie, nom, question):
    """Bouton « Envoyer » ou touche Entrée : pose la question au coloc choisi."""
    if partie is None:
        raise gr.Error("Lance d'abord une nouvelle partie.")
    if nom is None:
        raise gr.Error("Choisis d'abord à qui tu parles.")
    try:
        replique = jeu.poser_question(partie, nom, question)
    except ValueError as erreur:
        raise gr.Error(str(erreur))

    if replique is None:  # question vide : rien ne change
        return list(partie.historiques[nom]), question, texte_compteur(partie)
    return list(partie.historiques[nom]), "", texte_compteur(partie)


def accuser(partie, nom_accuse, preuve):
    """Bouton « C'est lui ! C'est elle ! » : affiche le verdict."""
    if partie is None:
        raise gr.Error("Lance d'abord une nouvelle partie.")
    try:
        verdict = jeu.accuser(partie, nom_accuse, preuve)
    except ValueError as erreur:
        raise gr.Error(str(erreur))
    return texte_verdict(verdict)


def rafraichir_classement():
    """Ouverture de l'onglet « Classement » : relit les parties enregistrées."""
    return donnees.classement(), donnees.stats_par_affaire()


# ===== L'écran =====
with gr.Blocks(title=TITRE) as demo:
    partie = gr.State(None)

    gr.Markdown(f"# 🕵️ {TITRE}")
    gr.Markdown(REGLES)

    with gr.Tab("Jouer"):
        # Ligne de lancement
        with gr.Row():
            pseudo = gr.Textbox(label="Ton pseudo", placeholder="Anonyme", scale=2)
            choix_affaire = gr.Dropdown(TITRES, value=TITRES[0], label="L'affaire", scale=3)
            bouton_demarrer = gr.Button("Nouvelle partie", variant="primary", scale=1)

        description = gr.Markdown("*Choisis une affaire et lance une nouvelle partie.*")

        with gr.Row():
            # Colonne de gauche : le coloc et la question
            with gr.Column(scale=1):
                choix_coloc = gr.Radio([], label="À qui parles-tu ?")
                caractere = gr.Markdown()
                with gr.Group():
                    question = gr.Textbox(label="Ta question", placeholder="Tu faisais quoi hier soir ?")
                    bouton_envoyer = gr.Button("Envoyer")
                compteur = gr.Markdown(texte_compteur(None))
            # Colonne de droite : la conversation
            with gr.Column(scale=2):
                conversation = gr.Chatbot(label="La conversation", height=400)

        # Zone d'accusation
        gr.Markdown("## L'accusation")
        with gr.Row():
            choix_accuse = gr.Radio([], label="Qui est coupable ?", scale=1)
            preuve = gr.Textbox(label="La pièce à conviction",
                                placeholder="Décris l'objet qui trahit le coupable", scale=2)
        bouton_accuser = gr.Button("C'est lui ! C'est elle !", variant="stop")

        verdict = gr.Markdown()

    with gr.Tab("Classement") as onglet_classement:
        gr.Markdown("### Classement des joueurs")
        tableau_classement = gr.Dataframe(interactive=False)
        gr.Markdown("### Statistiques par affaire")
        tableau_stats = gr.Dataframe(interactive=False)

    # ===== Les événements =====
    bouton_demarrer.click(
        demarrer,
        inputs=[pseudo, choix_affaire],
        outputs=[partie, description, choix_coloc, caractere, conversation,
                 question, compteur, choix_accuse, preuve, verdict],
    )
    choix_coloc.change(changer_suspect, inputs=[partie, choix_coloc],
                       outputs=[caractere, conversation])

    entrees_question = [partie, choix_coloc, question]
    sorties_question = [conversation, question, compteur]
    bouton_envoyer.click(envoyer, inputs=entrees_question, outputs=sorties_question)
    question.submit(envoyer, inputs=entrees_question, outputs=sorties_question)

    bouton_accuser.click(accuser, inputs=[partie, choix_accuse, preuve], outputs=verdict)

    onglet_classement.select(rafraichir_classement, outputs=[tableau_classement, tableau_stats])


if __name__ == "__main__":
    demo.launch()