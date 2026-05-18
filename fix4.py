with open('gestion/views.py', 'r', encoding='utf-8') as f:
    lines = f.readlines()

lines[468] = "            log_action(request, 'connexion', f\"{user.username} s'est connecte depuis {request.META.get('REMOTE_ADDR', 'IP inconnue')}\")\n"

with open('gestion/views.py', 'w', encoding='utf-8') as f:
    f.writelines(lines)
print('Correction appliquee !')
