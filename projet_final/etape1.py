import ollama

MODELE = "lfm3-omni"

print("Pose ta question à Bastien (tape 'fin' pour arrêter).")

while True:
    question = input("\nToi : ")
    if question == "fin":
        break

    reponse = ollama.chat(
        model=MODELE,
        messages=[
            {"role": "system", "content": "Tu es Bastien, un sportif toujours affamé. Réponds en une phrase."},
            {"role": "user", "content": question},
        ],
    )
    print("Bastien :", reponse.message.content)
    