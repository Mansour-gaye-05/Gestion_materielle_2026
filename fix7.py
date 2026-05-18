with open('gestion/views.py', 'r', encoding='utf-8') as f:
    lines = f.readlines()

lines[764] = "            log_action(request, 'panne_signalee', f\"{request.user.username} a signale une panne sur '{ligne.materiel.nom}' : {description[:100]}\", materiel=ligne.materiel)\n"

with open('gestion/views.py', 'w', encoding='utf-8') as f:
    f.writelines(lines)
print('Correction appliquee !')
