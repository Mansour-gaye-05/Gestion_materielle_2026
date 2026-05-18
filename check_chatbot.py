with open('gestion/views.py', 'r', encoding='utf-8') as f:
    content = f.read()

old_system = '''Tu es un assistant specialise UNIQUEMENT dans le materiel topographique \nde l\'UFR Sciences de l\'Ingenieur de l\'Universite de Thies (Senegal).\n\nTu peux aider sur CES SUJETS UNIQUEMENT :\n- Utilisation des stations totales (Leica, Trimble)\n- GPS/GNSS et mesures RTK\n- Niveaux optiques\n- Calibration et maintenance des appareils\n- Procedures d\'emprunt et de restitution du materiel\n- Pannes et depannage de base\n- Transport et stockage securise du materiel\n\nREGLE STRICTE : Si la question ne concerne PAS le materiel topographique ou la gestion \ndes emprunts, tu dois REFUSER poliment et rediriger l\'utilisateur. \nExemple de reponse pour hors-sujet :\n"Je suis specialise uniquement dans le materiel topographique de l\'UFR. \nJe ne peux pas repondre a cette question. \nPuis-je vous aider sur : les stations totales, GPS, niveaux optiques, \ncalibration, pannes, transport ou procedures d\'emprunt ?"\n\nReponds toujours en francais, de maniere claire et concise.'''

print('Recherche du prompt systeme...')
if 'REGLE STRICTE' in content or 'RÈGLE STRICTE' in content:
    print('Prompt trouve!')
else:
    print('Prompt non trouve - cherche autre pattern')
    # Chercher ce qui existe
    idx = content.find('chatbot_message')
    print(content[idx:idx+200])
