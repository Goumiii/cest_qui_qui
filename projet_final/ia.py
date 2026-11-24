"""Appels au modèle de langage avec Ollama. Ce fichier ne connaît pas les règles du jeu."""
import struct
import tempfile

import httpx
import ollama

REPLIQUE_DE_SECOURS = "Euh… tu peux répéter la question ?"


def repondre(modele, prompt_systeme, historique, question):
    """Renvoie la réplique du modèle à une question, en tenant compte de la conversation."""
    messages = [{"role": "system", "content": prompt_systeme}]
    messages = messages + historique
    messages.append({"role": "user", "content": question})

    reponse = ollama.chat(model=modele, messages=messages)
    texte = reponse.message.content.strip()
    if texte == "":
        return REPLIQUE_DE_SECOURS
    return texte


def decrire_image(modele, chemin_image):
    """Renvoie une phrase, en français, qui décrit l'objet principal d'une image."""
    message = {
        "role": "user",
        "content": "Décris en une seule phrase, en français, l'objet principal de cette image.",
        "images": [chemin_image],
    }
    reponse = ollama.chat(model=modele, messages=[message])
    return reponse.message.content.strip()


# ===== Étape 8 : l'écoute et la parole =====
# La bibliothèque ollama ne gère pas le son : on appelle directement le serveur avec httpx.
ADRESSE_OLLAMA = "http://localhost:11434"


def transcrire(modele, chemin_audio):
    """Renvoie le texte prononcé dans un enregistrement WAV."""
    with open(chemin_audio, "rb") as fichier:
        r = httpx.post(f"{ADRESSE_OLLAMA}/v1/audio/transcriptions",
                       data={"model": modele}, files={"file": fichier}, timeout=120)
    r.raise_for_status()
    return r.json()["text"].strip()


def corriger_wav(contenu):
    """Corrige les tailles écrites dans l'en-tête d'un WAV, pour que sa durée soit juste."""
    contenu = bytearray(contenu)
    # Taille totale du fichier, écrite à la position 4
    contenu[4:8] = struct.pack("<I", len(contenu) - 8)
    # Taille des données sonores, écrite juste après le mot « data »
    position = contenu.find(b"data")
    if position != -1:
        contenu[position + 4:position + 8] = struct.pack("<I", len(contenu) - position - 8)
    return bytes(contenu)


def parler(modele, texte, voix):
    """Fait dire un texte à voix haute et renvoie le chemin du fichier WAV créé."""
    r = httpx.post(f"{ADRESSE_OLLAMA}/v1/audio/speech",
                   json={"model": modele, "voice": voix, "input": texte,
                         "response_format": "wav"},
                   timeout=300)
    r.raise_for_status()
    fichier = tempfile.NamedTemporaryFile(suffix=".wav", delete=False)
    fichier.write(corriger_wav(r.content))
    fichier.close()
    return fichier.name
