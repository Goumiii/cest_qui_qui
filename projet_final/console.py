"""Jouer une partie complète dans le terminal, sans interface graphique."""
import donnees
import jeu


def choisir_affaire():
    """Affiche les affaires et renvoie le numéro choisi."""
    affaires = donnees.lire_affaires()
    for _, a in affaires.iterrows():
        print(f"  {a['affaire_id']}. {a['titre']}")
    while True:
        choix = input("Numéro de l'affaire : ")
        if choix.isdigit() and int(choix) in affaires["affaire_id"].tolist():
            return int(choix)
        print("Numéro inconnu.")


def afficher_verdict(verdict):
    """Affiche le résultat de l'accusation."""
    print("\n===== VERDICT =====")
    if verdict["bon_coupable"]:
        print("Bon coupable !")
    else:
        print(f"Raté ! C'était {verdict['coupable']}.")
    if verdict["preuve_acceptee"]:
        print("Preuve acceptée !")
    else:
        print(f"Preuve refusée. Il fallait : {verdict['preuve_attendue']}.")
    print("Ce qui s'est passé :", verdict["solution"])
    print(f"Questions utilisées : {verdict['questions_utilisees']}")
    print(f"SCORE : {verdict['score']} / 100")


def jouer():
    """La boucle d'une partie : questions, puis accusation et verdict."""
    print("===== C'EST QUI QUI ? =====\n")
    pseudo = input("Ton pseudo : ")
    affaire_id = choisir_affaire()
    partie = jeu.nouvelle_partie(pseudo, affaire_id)

    print(f"\n{partie.affaire['titre']}")
    print(partie.affaire["description"])
    noms = [s["nom"] for s in partie.suspects]
    print("\nLes colocs :")
    for s in partie.suspects:
        print(f"  - {s['nom']} : {s['caractere']}")
    print("\nTape 'accuser' quand tu as trouvé.")

    while partie.questions_restantes > 0:
        nom = input(f"\nÀ qui parles-tu ? ({', '.join(noms)}, ou accuser) : ")
        if nom == "accuser":
            break
        if nom not in noms:
            print("Ce coloc n'existe pas.")
            continue
        question = input("Ta question : ")
        replique = jeu.poser_question(partie, nom, question)
        if replique is None:
            continue
        print(f"{nom} : {replique}")
        print(f"(Questions restantes : {partie.questions_restantes})")

    if partie.questions_restantes == 0:
        print("\nPlus de questions ! Il faut accuser.")

    nom_accuse = ""
    while nom_accuse not in noms:
        nom_accuse = input(f"\nQui accuses-tu ? ({', '.join(noms)}) : ")
    description = input("Quelle pièce à conviction présentes-tu ? ")

    verdict = jeu.accuser(partie, nom_accuse, description)
    afficher_verdict(verdict)


if __name__ == "__main__":
    jouer()