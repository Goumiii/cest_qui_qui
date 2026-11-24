"""Appels au modèle de langage avec Ollama. Ce fichier ne connaît pas les règles du jeu."""
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