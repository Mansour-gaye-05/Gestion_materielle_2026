with open('gestion/views.py', 'r', encoding='utf-8') as f:
    lines = f.readlines()

lines[497] = "    log_action(request, 'deconnexion', f\"{request.user.username} s'est deconnecte\")\n"

with open('gestion/views.py', 'w', encoding='utf-8') as f:
    f.writelines(lines)
print('Correction appliquee !')
