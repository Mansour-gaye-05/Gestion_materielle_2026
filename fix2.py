with open('gestion/views.py', 'r', encoding='utf-8') as f:
    lines = f.readlines()

lines[286] = "        log_action(request, 'maintenance_resolue', f\"{request.user.username} a resolu la maintenance de '{maintenance.materiel.nom}'\", materiel=maintenance.materiel)\n"
lines[288] = "        messages.success(request, f'Maintenance resolue pour {maintenance.materiel.nom}')\n"

with open('gestion/views.py', 'w', encoding='utf-8') as f:
    f.writelines(lines)
print('Correction appliquee !')
