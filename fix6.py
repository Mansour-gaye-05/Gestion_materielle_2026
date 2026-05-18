with open('gestion/views.py', 'r', encoding='utf-8') as f:
    lines = f.readlines()

lines[531] = "                log_action(request, 'inscription', f\"Nouveau compte cree : {username} ({filiere} - {niveau})\")\n"

with open('gestion/views.py', 'w', encoding='utf-8') as f:
    f.writelines(lines)
print('Correction appliquee !')
