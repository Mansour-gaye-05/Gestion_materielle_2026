with open('gestion/views.py', 'r', encoding='utf-8') as f:
    lines = f.readlines()

lines[320] = "        log_action(request, 'materiel_ajoute', f\"{request.user.username} a ajoute le materiel '{nom}'\", materiel=materiel_obj)\n"

with open('gestion/views.py', 'w', encoding='utf-8') as f:
    f.writelines(lines)
print('Correction appliquee !')
