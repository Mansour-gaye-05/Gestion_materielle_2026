import re

with open('gestion/views.py', 'r', encoding='utf-8') as f:
    content = f.read()

new_chatbot = '''@login_required
def chatbot_message(request):
    if request.method == "POST":
        import requests as http_requests
        from django.conf import settings

        data = json.loads(request.body)
        user_message = data.get("message", "")
        mode = data.get("mode", "general")

        conversation, created = ConversationChat.objects.get_or_create(
            utilisateur=request.user,
            defaults={"messages": []}
        )

        historique = conversation.messages[-10:]

        # Detecter automatiquement le mode selon le message
        msg_lower = user_message.lower()
        mots_panne = ["allume", "marche", "fonctionne", "bloque", "erreur", "probleme", "panne", "tombe", "casse", "bug", "ecran", "batterie", "charge", "signal", "gps", "fixe", "plante", "freeze"]
        mots_suggestion = ["recommande", "conseil", "choisir", "quel materiel", "besoin", "leve", "topographique", "mission", "terrain", "projet", "cadastre", "implantation", "nivellement", "bathymetrie"]
        mots_procedure = ["emprunter", "restituer", "rendre", "recuperer", "demande", "reservation", "disponible", "reserver"]

        if any(m in msg_lower for m in mots_panne):
            detected_mode = "diagnostic"
        elif any(m in msg_lower for m in mots_suggestion):
            detected_mode = "suggestion"
        elif any(m in msg_lower for m in mots_procedure):
            detected_mode = "procedure"
        else:
            detected_mode = mode

        # Construire le prompt systeme selon le mode
        base_context = """Tu es un assistant expert en materiel topographique de l\'UFR Sciences de l\'Ingenieur, Universite de Thies, Senegal.
Le laboratoire dispose de : Stations totales Leica TS16, GPS GNSS differentiel i50/i73, Niveaux optiques electroniques, GPS Garmin de poche.

REGLES ABSOLUES :
- Reponds UNIQUEMENT sur le materiel topographique, les emprunts, les pannes, les procedures du laboratoire
- Si hors-sujet : decline poliment et propose des sujets disponibles
- Toujours en francais, structure et concis
- Utilise des emojis pour rendre la reponse claire"""

        if detected_mode == "diagnostic":
            system_prompt = base_context + """

MODE DIAGNOSTIC DE PANNE :
Quand l\'utilisateur decrit un probleme, tu dois :
1. Identifier l\'appareil concerne
2. Proposer les causes probables (du plus simple au plus complexe)
3. Donner les solutions etape par etape
4. Indiquer si une intervention technicien est necessaire

Structure ta reponse ainsi :
🔍 DIAGNOSTIC : [nom appareil]
⚠️ Causes probables :
  1. [cause la plus probable]
  2. [autre cause]
🛠️ Solutions a essayer :
  ✅ Etape 1 : [action simple]
  ✅ Etape 2 : [action suivante]
🚨 Si le probleme persiste : Signalez via l\'application > "Signaler une panne"

Connaissances pannes specifiques :
- Station totale qui s\'eteint : batterie faible, contactes sales, surchauffe
- GPS sans signal : masque ciel insuffisant, initialisation RTK manquante, antenne debranchee
- Niveau optique qui derive : mise en station incorrecte, bulle non centree, vis calantes
- Ecran noir : batterie decharge, reset necessaire (maintenir power 10s)
- Erreur de mesure anormale : prismes sales, calibration requise, refraction atmospherique"""

        elif detected_mode == "suggestion":
            system_prompt = base_context + """

MODE SUGGESTIONS INTELLIGENTES :
Quand l\'utilisateur decrit sa mission ou son besoin, recommande le materiel optimal.

Structure ta reponse ainsi :
🎯 MISSION : [type de travail detecte]
📦 MATERIEL RECOMMANDE :
  ⭐ Principal : [materiel 1] - [pourquoi]
  ➕ Complementaire : [materiel 2] - [pourquoi]
  🔋 Accessoires : [liste]
💡 CONSEILS TERRAIN :
  - [conseil 1]
  - [conseil 2]
⏱️ Duree recommandee d\'emprunt : [X jours]

Recommandations selon mission :
- Leve topographique general : Station totale + GPS GNSS
- Cadastre/foncier : Station totale Leica TS16 + trépied + prismes
- Implantation : Station totale + mire
- Nivellement : Niveau optique electronique + mire parlante
- Bathymetrie : GPS GNSS differentiel + accessoires
- Reconnaissance rapide : GPS Garmin de poche
- Grande precision : GPS GNSS RTK i50 ou i73"""

        elif detected_mode == "procedure":
            system_prompt = base_context + """

MODE PROCEDURE EMPRUNT :
Guide l\'utilisateur sur les procedures du laboratoire.

Procedures disponibles :
- Emprunter : Catalogue > choisir materiel > Nouvelle demande > remplir dates + localisation > soumettre > attendre validation admin
- Recuperer : Espace etudiant > Mes demandes > bouton "Recuperer" (apres approbation admin)
- Rendre : Espace etudiant > Mes demandes > bouton "Rendre" > materiel restitue
- Signaler panne : Espace etudiant > Mes demandes > "Signaler panne" sur emprunt en cours
- Voir reservations : Nouvelle demande > selectionner materiel > calendrier affiche les dates prises

Structure ta reponse avec des etapes numerotees claires."""

        else:
            system_prompt = base_context + """

Reponds de facon claire et structuree. Utilise des emojis pertinents.
Si l\'utilisateur semble avoir un probleme avec un appareil, propose le mode diagnostic.
Si l\'utilisateur cherche du materiel pour une mission, propose des recommandations."""

        groq_messages = [{"role": "system", "content": system_prompt}]

        for msg in historique:
            groq_messages.append({"role": "user", "content": msg["user"]})
            groq_messages.append({"role": "assistant", "content": msg["bot"]})

        groq_messages.append({"role": "user", "content": user_message})

        try:
            response = http_requests.post(
                "https://api.groq.com/openai/v1/chat/completions",
                headers={
                    "Authorization": f"Bearer {settings.GROQ_API_KEY}",
                    "Content-Type": "application/json"
                },
                json={
                    "model": "llama-3.3-70b-versatile",
                    "messages": groq_messages,
                    "max_tokens": 800,
                    "temperature": 0.6
                },
                timeout=15
            )
            if response.status_code == 200:
                bot_response = response.json()["choices"][0]["message"]["content"]
            else:
                bot_response = "Erreur de connexion a l\'IA. Veuillez reessayer."
        except Exception as e:
            bot_response = "Service IA temporairement indisponible. Veuillez reessayer."

        msgs = conversation.messages
        msgs.append({"user": user_message, "bot": bot_response, "date": str(timezone.now()), "mode": detected_mode})
        conversation.messages = msgs[-50:]
        conversation.save()

        return JsonResponse({"response": bot_response, "mode": detected_mode})

    return JsonResponse({"error": "Methode non autorisee"}, status=405)
'''

# Remplacer la fonction chatbot_message
content = re.sub(
    r'@login_required\ndef chatbot_message\(request\):.*?(?=\n@|\ndef |\n# =====)',
    new_chatbot + "\n",
    content,
    flags=re.DOTALL
)

with open('gestion/views.py', 'w', encoding='utf-8') as f:
    f.write(content)
print('chatbot_message mis a jour!')
