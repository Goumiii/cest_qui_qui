"""Les règles du jeu : partie, questions, accusation, score."""
import unicodedata
from dataclasses import dataclass, field

import donnees
import ia

# ===== Réglages =====
MODELE = "lfm3-omni"
QUESTIONS_PAR_PARTIE = 12
POINTS_PREUVE = 50
POINTS_COUPABLE = 40
POINTS_RAPIDITE_MAX = 10
PSEUDO_PAR_DEFAUT = "Anonyme"


# ===== La fiche d'une partie =====
@dataclass
class Partie:
    """Tout ce qu'il faut savoir sur la partie en cours."""
    pseudo: str
    affaire: dict
    suspects: list
    modele: str = MODELE
    profil: str = "complet"
    questions_restantes: int = QUESTIONS_PAR_PARTIE
    terminee: bool = False
    historiques: dict = field(default_factory=dict)


def nouvelle_partie(pseudo, affaire_id, modele=MODELE, profil="complet"):
    """Crée une partie, avec un historique vide pour chaque coloc."""
    if pseudo is None or pseudo.strip() == "":
        pseudo = PSEUDO_PAR_DEFAUT
    affaire, suspects = donnees.charger_affaire(affaire_id)
    historiques = {s["nom"]: [] for s in suspects}
    return Partie(pseudo=pseudo.strip(), affaire=affaire, suspects=suspects,
                  modele=modele, profil=profil, historiques=historiques)


def trouver_suspect(partie, nom):
    """Renvoie la fiche du coloc qui porte ce nom."""
    for s in partie.suspects:
        if s["nom"] == nom:
            return s
    raise ValueError(f"Pas de coloc nommé {nom} dans cette affaire.")


# ===== Les consignes du modèle =====
def construire_prompt(affaire, suspect, tous_les_suspects):
    """Transforme la fiche CSV d'un coloc en consignes pour le modèle."""
    autres = [s["nom"] for s in tous_les_suspects if s["nom"] != suspect["nom"]]

    lignes = [
        f"Tu es {suspect['nom']}. Tu vis en colocation avec {autres[0]} et {autres[1]}.",
        "Quelqu'un mène l'enquête sur l'affaire ci-dessous et te pose des questions.",
        f"L'affaire : {affaire['description']}",
        f"Ton caractère : {suspect['caractere']}",
        "",
        f"A. Ce que tu faisais : « {suspect['alibi']} »",
    ]

    # Le modèle ne reçoit jamais la vérité : seul l'intitulé du bloc B change
    if suspect["coupable"]:
        lignes.append(f"B. Qui tu soupçonnes : « {suspect['indice']} »")
    else:
        lignes.append(f"B. Ce que tu as remarqué : « {suspect['indice']} »")

    lignes.append(f"C. Si on t'accuse : « {suspect['defense']} »")

    # Bloc D : seulement pour le coupable
    if suspect["coupable"]:
        lignes.append(f"D. Si on te dit que {suspect['faille']}, tu réponds : « {suspect['excuse']} »")

    if suspect["coupable"]:
        choix = "A, B, C ou D"
    else:
        choix = "A, B ou C"

    lignes += [
        "",
        "Règles :",
        f"- Choisis la phrase {choix} qui correspond le mieux à la question.",
        "- Réponds en 1 à 3 phrases, avec ta façon de parler.",
        "- N'invente rien qui ne soit pas écrit ci-dessus.",
        "- Réponds toujours en français.",
    ]
    return "\n".join(lignes)


# ===== Les questions =====
def poser_question(partie, nom, question):
    """Fait répondre un coloc, met à jour son historique et le compteur. Renvoie la réplique."""
    if partie.terminee:
        raise ValueError("Lance une nouvelle partie.")
    if question.strip() == "":
        return None  # question vide : rien ne se passe, le compteur ne bouge pas
    if partie.questions_restantes <= 0:
        raise ValueError("Il faut désigner le coupable.")

    suspect = trouver_suspect(partie, nom)
    prompt = construire_prompt(partie.affaire, suspect, partie.suspects)
    historique = partie.historiques[nom]

    replique = ia.repondre(partie.modele, prompt, historique, question)

    historique.append({"role": "user", "content": question})
    historique.append({"role": "assistant", "content": replique})
    partie.questions_restantes -= 1

    donnees.enregistrer_echange(partie.pseudo, partie.affaire["affaire_id"], nom, question, replique)
    return replique


# ===== La preuve =====
def sans_accents(texte):
    """Met le texte en minuscules et retire les accents."""
    texte = unicodedata.normalize("NFD", texte.lower())
    return "".join(c for c in texte if unicodedata.category(c) != "Mn")


def preuve_valable(affaire, description):
    """Vrai si la description contient un des mots-clés de l'affaire."""
    description = sans_accents(description)
    mots_cles = [m.strip() for m in affaire["mots_cles"].split(",")]
    return any(mot in description for mot in mots_cles)


# ===== Le score et l'accusation =====
def calculer_score(bon_coupable, preuve_acceptee, questions_restantes):
    """Applique le barème : 50 pour la preuve, 40 pour le coupable, jusqu'à 10 de rapidité."""
    score = 0
    if preuve_acceptee:
        score += POINTS_PREUVE
    if bon_coupable:
        score += POINTS_COUPABLE
        score += round(questions_restantes / QUESTIONS_PAR_PARTIE * POINTS_RAPIDITE_MAX)
    return score


def accuser(partie, nom_accuse, description=None, image=None):
    """Vérifie l'accusation, calcule le score et termine la partie. Renvoie le verdict."""
    if partie.terminee:
        raise ValueError("Lance une nouvelle partie.")
    if not nom_accuse:
        raise ValueError("Choisis d'abord qui tu accuses.")

    # Étape 7 : si une image est présentée, le modèle la décrit, puis Python décide
    vu_par_arbitre = None
    if image:
        vu_par_arbitre = ia.decrire_image(partie.modele, image)
        description = vu_par_arbitre

    coupable = [s["nom"] for s in partie.suspects if s["coupable"]][0]
    bon_coupable = nom_accuse == coupable
    preuve_acceptee = preuve_valable(partie.affaire, description or "")
    score = calculer_score(bon_coupable, preuve_acceptee, partie.questions_restantes)
    questions_utilisees = QUESTIONS_PAR_PARTIE - partie.questions_restantes
    partie.terminee = True

    donnees.enregistrer_partie(
        pseudo=partie.pseudo,
        affaire_id=partie.affaire["affaire_id"],
        affaire=partie.affaire["titre"],
        accuse=nom_accuse,
        bon_coupable=bon_coupable,
        preuve_acceptee=preuve_acceptee,
        questions_utilisees=questions_utilisees,
        score=score,
        profil=partie.profil,
    )

    return {
        "bon_coupable": bon_coupable,
        "preuve_acceptee": preuve_acceptee,
        "coupable": coupable,
        "preuve_attendue": partie.affaire["preuve_attendue"],
        "solution": partie.affaire["solution"],
        "questions_utilisees": questions_utilisees,
        "score": score,
        "vu_par_arbitre": vu_par_arbitre,
    }