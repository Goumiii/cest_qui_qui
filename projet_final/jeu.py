"""Les règles du jeu : partie, questions, accusation, score."""


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