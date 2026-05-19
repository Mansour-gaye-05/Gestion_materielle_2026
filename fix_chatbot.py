with open('gestion/views.py', 'r', encoding='utf-8') as f:
    content = f.read()

import re

old_func = re.search(r'def chatbot_message\(request\):.*?return JsonResponse\(\{.error.: .Methode non autorisee.\}, status=405\)', content, re.DOTALL)

if old_func:
    new_func = '''def chatbot_message(request):
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

        historique = conversation.messages[-20:]

        # Detecter automatiquement le mode selon le message
        msg_lower = user_message.lower()
        mots_panne = ["allume", "marche", "fonctionne", "bloque", "erreur", "probleme", "panne", "tombe", "casse", "ecran", "batterie", "signal", "freeze"]
        mots_suggestion = ["recommande", "conseil", "choisir", "quel materiel", "mission", "terrain", "leve", "cadastre", "implantation", "nivellement"]
        mots_procedure = ["emprunter", "restituer", "rendre", "recuperer", "demande", "reservation", "comment faire"]
        mots_ameliorer = ["ameliore", "ameliorer", "plus detail", "plus precis", "developpe", "approfondi", "explique mieux", "plus complet", "detaille", "autre facon", "reformule"]

        if any(m in msg_lower for m in mots_ameliorer):
            detected_mode = "amelioration"
        elif any(m in msg_lower for m in mots_panne):
            detected_mode = "diagnostic"
        elif any(m in msg_lower for m in mots_suggestion):
            detected_mode = "suggestion"
        elif any(m in msg_lower for m in mots_procedure):
            detected_mode = "procedure"
        else:
            detected_mode = mode

        system_prompt = """Tu es un assistant expert en materiel topographique de l\'UFR Sciences de l\'Ingenieur, Universite de Thies, Senegal.

Materiels disponibles : Stations totales Leica TS16, GPS GNSS differentiel i50/i73, Niveaux optiques electroniques, GPS Garmin de poche.

REGLES ABSOLUES :
- Reponds UNIQUEMENT sur le materiel topographique, les emprunts, les pannes, les procedures
- Si hors-sujet : decline poliment
- Toujours en francais, structure, concis
- Utilise des emojis pertinents
- TU AS UNE MEMOIRE : utilise TOUJOURS l\'historique de la conversation pour contextualiser tes reponses
- Si l\'utilisateur demande d\'ameliorer, developper ou preciser ta reponse precedente, fais-le vraiment differemment et avec plus de details
- Ne repete JAMAIS mot pour mot une reponse que tu as deja donnee dans cette conversation
- Si tu as deja repondu a une question, approfondis avec de nouveaux elements"""

        if detected_mode == "amelioration":
            system_prompt += """

MODE AMELIORATION :
L\'utilisateur veut que tu ameliores ou developpes ta DERNIERE reponse.
- Lis attentivement ta derniere reponse dans l\'historique
- Donne une version PLUS COMPLETE et DIFFERENTE
- Ajoute des details techniques que tu n\'avais pas mentionnes
- Utilise une structure differente (si tu avais des listes, ajoute des exemples concrets)
- Enrichis avec des cas pratiques specifiques au contexte UFR Thies"""

        elif detected_mode == "diagnostic":
            system_prompt += """

MODE DIAGNOSTIC :
🔍 DIAGNOSTIC : [appareil]
📋 Causes probables (de la plus simple a la plus complexe) :
   1. [cause 1]
   2. [cause 2]
🔧 Solutions etape par etape :
   Etape 1 : [action]
   Etape 2 : [action]
🚨 Si persiste : Signalez via l\'application"""

        elif detected_mode == "suggestion":
            system_prompt += """

MODE SUGGESTION :
📌 MISSION : [type detecte]
🎯 MATERIEL RECOMMANDE :
   • [principal] - [raison]
   • [complement] - [raison]
💡 CONSEILS TERRAIN :
   • [conseil pratique 1]
   • [conseil pratique 2]
⏱️ Duree recommandee : [X jours]"""

        elif detected_mode == "procedure":
            system_prompt += """

MODE PROCEDURE :
📋 PROCEDURE [action] :
1. [etape 1]
2. [etape 2]
3. [etape 3]"""

        # Construire les messages avec historique COMPLET
        groq_messages = [{"role": "system", "content": system_prompt}]

        # Ajouter tout l\'historique pour que l\'IA se souvienne
        for msg in historique:
            groq_messages.append({"role": "user", "content": msg["user"]})
            groq_messages.append({"role": "assistant", "content": msg["bot"]})

        # Message actuel
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
                    "max_tokens": 1000,
                    "temperature": 0.7,
                    "top_p": 0.9
                },
                timeout=20
            )
            if response.status_code == 200:
                bot_response = response.json()["choices"][0]["message"]["content"]
            else:
                bot_response = "Erreur de connexion a l\'IA. Veuillez reessayer."
        except Exception as e:
            bot_response = "Service IA temporairement indisponible. Veuillez reessayer."

        # Sauvegarder la conversation
        msgs = conversation.messages
        msgs.append({"user": user_message, "bot": bot_response, "date": str(timezone.now()), "mode": detected_mode})
        conversation.messages = msgs[-50:]
        conversation.save()

        return JsonResponse({"response": bot_response, "mode": detected_mode})

    return JsonResponse({"error": "Methode non autorisee"}, status=405)'''

    content = content[:old_func.start()] + new_func + content[old_func.end():]
    with open('gestion/views.py', 'w', encoding='utf-8') as f:
        f.write(content)
    print('chatbot_message mis a jour!')
else:
    print('Fonction non trouvee')
