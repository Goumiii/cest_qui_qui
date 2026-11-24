"""Profils matériels et réglages : choisir ce que le jeu peut proposer sur cette machine."""
import ollama
import psutil

QUESTIONS_PAR_PARTIE = 12

# Pour chaque profil : le modèle Ollama, ce qu'il sait faire, et la mémoire libre conseillée (Go)
PROFILS = {
    "complet": {"modele": "lfm3-omni", "voix": True, "image": True, "ram_go": 3.0},
    "image": {"modele": "lfm3-vl", "voix": False, "image": True, "ram_go": 2.5},
    "voix": {"modele": "lfm3-audio", "voix": True, "image": False, "ram_go": 2.5},
    "leger": {"modele": "lfm2.5-thinking", "voix": False, "image": False, "ram_go": 1.0},
}

# Du plus complet au plus léger
ORDRE = ["complet", "image", "voix", "leger"]


def modeles_installes():
    """Renvoie la liste des modèles présents dans Ollama, sans le suffixe « :latest »."""
    try:
        liste = ollama.list()
    except Exception:
        raise ValueError("Ollama ne répond pas. Lance-le dans un autre terminal avec : ollama serve")
    return [m.model.replace(":latest", "") for m in liste.models]


def ram_libre_go():
    """Renvoie la mémoire vive disponible, en Go."""
    return psutil.virtual_memory().available / 1024 ** 3


def choisir_profil(force=None):
    """Renvoie (nom, profil) : le profil imposé, sinon le plus complet possible."""
    if force is not None:
        if force not in PROFILS:
            raise ValueError(f"Profil inconnu : {force}. Profils possibles : {', '.join(ORDRE)}")
        modele = PROFILS[force]["modele"]
        if modele not in modeles_installes():
            print(f"Attention : le modèle {modele} n'est pas installé. Tape : ollama pull {modele}")
        return force, PROFILS[force]

    installes = modeles_installes()
    possibles = [nom for nom in ORDRE if PROFILS[nom]["modele"] in installes]
    if not possibles:
        raise ValueError("Aucun modèle du jeu n'est installé. Tape : ollama pull lfm3-omni")

    # Le plus complet qui tient en mémoire
    ram = ram_libre_go()
    for nom in possibles:
        if ram >= PROFILS[nom]["ram_go"]:
            return nom, PROFILS[nom]

    # Mémoire trop juste : on prend quand même le plus complet installé
    print(f"Attention : seulement {ram:.1f} Go de mémoire libre, le jeu risque d'être lent.")
    return possibles[0], PROFILS[possibles[0]]


# ===== Vérification =====
if __name__ == "__main__":
    print("Modèles installés :", modeles_installes())
    print(f"Mémoire libre : {ram_libre_go():.1f} Go")
    nom, profil = choisir_profil()
    print("Profil choisi :", nom, profil)