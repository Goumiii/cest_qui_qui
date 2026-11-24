"""L'interface du jeu dans le navigateur, avec Gradio. Ce fichier ne contient aucune règle."""
import sys

import gradio as gr

import config
import donnees
import habillage
import ia
import jeu

# ===== Le profil de la machine (étape 9) =====
# python app.py          -> choix automatique
# python app.py leger    -> profil imposé
try:
    PROFIL_NOM, PROFIL = config.choisir_profil(sys.argv[1] if len(sys.argv) > 1 else None)
except ValueError as erreur:
    print(erreur)
    sys.exit(1)
print(f"Profil : {PROFIL_NOM} (modèle {PROFIL['modele']})")

TITRE = "C'est Qui Qui ?"
REGLES = (
    "Un méfait a été commis dans la coloc. Questionne les trois colocs : "
    "deux disent la vérité, le troisième ment. "
    f"Tu as **{jeu.QUESTIONS_PAR_PARTIE} questions** en tout. "
    "Ensuite, désigne le coupable et présente la pièce à conviction qui le trahit."
)

AFFAIRES = donnees.lire_affaires()
TITRES = AFFAIRES["titre"].tolist()

# Étape 8 : les deux modes de jeu, et la voix de celui qui lit l'affaire et le verdict
MODES = ["Écrit", "Voix"]
VOIX_NARRATEUR = "male-french"


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
    if verdict["vu_par_arbitre"]:
        lignes.append(f"\n🔍 *L'arbitre a vu : {verdict['vu_par_arbitre']}*")
    lignes.append(f"\n**Ce qui s'est passé :** {verdict['solution']}")
    lignes.append(f"\nQuestions utilisées : {verdict['questions_utilisees']}")
    lignes.append(f"\n# Score : {verdict['score']} / 100")
    return "\n\n".join(lignes)


def texte_verdict_oral(verdict):
    """Renvoie le verdict en phrases simples, pour être lu à voix haute."""
    if verdict["bon_coupable"]:
        phrases = [f"Bravo, c'était bien {verdict['coupable']} !"]
    else:
        phrases = [f"Raté, c'était {verdict['coupable']}."]
    if verdict["preuve_acceptee"]:
        phrases.append("Ta preuve est acceptée.")
    else:
        phrases.append(f"Ta preuve est refusée. Il fallait {verdict['preuve_attendue']}.")
    phrases.append(verdict["solution"])
    phrases.append(f"Ton score est de {verdict['score']} sur 100.")
    return " ".join(phrases)


def dire(texte, voix, mode):
    """En mode Voix, renvoie le fichier son du texte lu à voix haute. Sinon, rien."""
    if mode != "Voix" or not PROFIL["voix"]:
        return None
    try:
        return ia.parler(PROFIL["modele"], texte, voix)
    except Exception:
        gr.Warning("La voix n'a pas pu être générée. Le texte reste affiché.")
        return None


# ===== Les fonctions reliées aux événements =====
def demarrer(pseudo, titre, mode):
    """Bouton « Nouvelle partie » : crée la partie et remet tout l'écran à zéro."""
    if titre is None:
        raise gr.Error("Choisis d'abord une affaire.")
    affaire_id = int(AFFAIRES[AFFAIRES["titre"] == titre]["affaire_id"].iloc[0])
    partie = jeu.nouvelle_partie(pseudo, affaire_id, modele=PROFIL["modele"], profil=PROFIL_NOM)

    noms = [s["nom"] for s in partie.suspects]
    description = f"## {partie.affaire['titre']}\n{partie.affaire['description']}"
    lecture = f"{partie.affaire['titre']} {partie.affaire['description']}"
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
        None,                                         # image vide
        "",                                           # verdict vide
        None,                                         # micro vide
        dire(lecture, VOIX_NARRATEUR, mode),          # l'affaire lue à voix haute
    )


def changer_mode(mode):
    """Choix Écrit / Voix : affiche ou masque le micro et le haut-parleur."""
    voix = mode == "Voix"
    return gr.update(visible=voix), gr.update(visible=voix)


def dicter(enregistrement):
    """Fin d'un enregistrement au micro : écrit la question dans la zone de texte."""
    if enregistrement is None:
        return gr.update(), None
    try:
        texte = ia.transcrire(PROFIL["modele"], enregistrement)
    except Exception:
        raise gr.Error("Je n'ai pas réussi à comprendre l'enregistrement. Réessaie ou tape ta question.")
    return texte, None


def changer_suspect(partie, nom):
    """Choix d'un coloc : affiche son caractère et sa propre conversation."""
    if partie is None or nom is None:
        return "", []
    return texte_caractere(partie, nom), list(partie.historiques[nom])


def envoyer(partie, nom, question, mode):
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
        return list(partie.historiques[nom]), question, texte_compteur(partie), None

    voix = jeu.trouver_suspect(partie, nom)["voix"]
    son = dire(replique, voix, mode)
    return list(partie.historiques[nom]), "", texte_compteur(partie), son


def accuser(partie, nom_accuse, preuve, image, mode):
    """Bouton « C'est lui ! C'est elle ! » : affiche le verdict."""
    if partie is None:
        raise gr.Error("Lance d'abord une nouvelle partie.")
    if not image and (preuve is None or preuve.strip() == ""):
        raise gr.Error("Présente une pièce à conviction : une image ou une description.")
    try:
        verdict = jeu.accuser(partie, nom_accuse, description=preuve, image=image)
    except ValueError as erreur:
        raise gr.Error(str(erreur))
    return texte_verdict(verdict), dire(texte_verdict_oral(verdict), VOIX_NARRATEUR, mode)


def rafraichir_classement():
    """Ouverture de l'onglet « Classement » : relit les parties enregistrées."""
    return donnees.classement(), donnees.stats_par_affaire()


# ===== L'écran =====
with gr.Blocks(title=TITRE) as demo:
    partie = gr.State(None)

    gr.HTML(habillage.entete(1337 + len(donnees.lire_parties())))

    with gr.Row():
        # Les publicités de gauche
        with gr.Column(scale=1, min_width=170, elem_classes=["colonne-pub"]):
            gr.HTML(habillage.PUBS_GAUCHE)

        # Le jeu, au centre
        with gr.Column(scale=5, elem_id="page-centrale"):
            gr.Markdown(REGLES)
            gr.Markdown(f"*Profil : {PROFIL_NOM} — modèle {PROFIL['modele']}*")

            with gr.Tab("🔍 Jouer"):
                # Ligne de lancement
                with gr.Row():
                    pseudo = gr.Textbox(label="Ton pseudo", placeholder="Anonyme", scale=2)
                    choix_affaire = gr.Dropdown(TITRES, value=TITRES[0], label="L'affaire", scale=3)
                    choix_mode = gr.Radio(MODES, value="Écrit", label="Mode de jeu", scale=1,
                                          visible=PROFIL["voix"])
                    bouton_demarrer = gr.Button("Nouvelle partie", scale=1,
                                                elem_classes=["bouton-retro"])

                description = gr.Markdown("*Choisis une affaire et lance une nouvelle partie.*")

                with gr.Row():
                    # Colonne de gauche : le coloc et la question
                    with gr.Column(scale=1):
                        choix_coloc = gr.Radio([], label="À qui parles-tu ?")
                        caractere = gr.Markdown()
                        with gr.Group():
                            question = gr.Textbox(label="Ta question",
                                                  placeholder="Tu faisais quoi hier soir ?")
                            micro = gr.Audio(sources=["microphone"], type="filepath",
                                             label="🎤 Dicte ta question", visible=False)
                            bouton_envoyer = gr.Button("Envoyer", elem_classes=["bouton-retro"])
                        compteur = gr.Markdown(texte_compteur(None))
                    # Colonne de droite : la conversation
                    with gr.Column(scale=2):
                        conversation = gr.Chatbot(label="La conversation", height=400)
                        haut_parleur = gr.Audio(label="🔊 Haut-parleur", autoplay=True,
                                                interactive=False, visible=False)

                # Zone d'accusation
                gr.Markdown("## L'accusation")
                with gr.Row():
                    choix_accuse = gr.Radio([], label="Qui est coupable ?", scale=1)
                    with gr.Column(scale=2):
                        image = gr.Image(type="filepath", label="La pièce à conviction en image",
                                         height=200, visible=PROFIL["image"])
                        preuve = gr.Textbox(label="… ou décris-la par écrit" if PROFIL["image"]
                                            else "La pièce à conviction, décrite par écrit",
                                            placeholder="Décris l'objet qui trahit le coupable")
                bouton_accuser = gr.Button("C'est lui ! C'est elle !", elem_classes=["bouton-rouge"])

                verdict = gr.Markdown()

            with gr.Tab("🏆 Classement") as onglet_classement:
                gr.Markdown("### Classement des joueurs")
                tableau_classement = gr.Dataframe(interactive=False)
                gr.Markdown("### Statistiques par affaire")
                tableau_stats = gr.Dataframe(interactive=False)

        # Les publicités de droite
        with gr.Column(scale=1, min_width=170, elem_classes=["colonne-pub"]):
            gr.HTML(habillage.PUBS_DROITE)

    gr.HTML(habillage.PIED)

    # ===== Les événements =====
    bouton_demarrer.click(
        demarrer,
        inputs=[pseudo, choix_affaire, choix_mode],
        outputs=[partie, description, choix_coloc, caractere, conversation,
                 question, compteur, choix_accuse, preuve, image, verdict,
                 micro, haut_parleur],
    )
    choix_mode.change(changer_mode, inputs=choix_mode, outputs=[micro, haut_parleur])
    micro.stop_recording(dicter, inputs=micro, outputs=[question, micro])
    choix_coloc.change(changer_suspect, inputs=[partie, choix_coloc],
                       outputs=[caractere, conversation])

    entrees_question = [partie, choix_coloc, question, choix_mode]
    sorties_question = [conversation, question, compteur, haut_parleur]
    bouton_envoyer.click(envoyer, inputs=entrees_question, outputs=sorties_question)
    question.submit(envoyer, inputs=entrees_question, outputs=sorties_question)

    bouton_accuser.click(accuser, inputs=[partie, choix_accuse, preuve, image, choix_mode],
                         outputs=[verdict, haut_parleur])

    onglet_classement.select(rafraichir_classement, outputs=[tableau_classement, tableau_stats])


if __name__ == "__main__":
    demo.launch(css=habillage.CSS)
