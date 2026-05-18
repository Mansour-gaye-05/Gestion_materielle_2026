lines = open('gestion/views.py', 'r', encoding='utf-8').readlines()
new_lines = []
for i, line in enumerate(lines, 1):
    if i == 226:
        new_lines.append('            for ligne in demande.lignes.all():\n')
        new_lines.append("                ligne.materiel.etat = 'emprunte'\n")
        new_lines.append('                ligne.materiel.save()\n')
        new_lines.append('\n')
        new_lines.append("            log_action(request, 'demande_approuvee', f'Admin {request.user.username} a approuve la demande #{demande.id}', demande=demande)\n")
        new_lines.append("            messages.success(request, f'Demande #{demande.id} approuvee')\n")
    elif i in [228, 229, 230, 231, 232]:
        pass
    elif i == 240:
        new_lines.append("        elif action == 'refuser':\n")
        new_lines.append("            demande.statut = 'refusee'\n")
        new_lines.append('            demande.motif_refus = motif\n')
        new_lines.append("            log_action(request, 'demande_refusee', f'Admin {request.user.username} a refuse la demande #{demande.id}. Motif: {motif}', demande=demande)\n")
        new_lines.append("            messages.warning(request, f'Demande #{demande.id} refusee')\n")
    elif i in [234, 235, 236, 237]:
        pass
    else:
        new_lines.append(line)
open('gestion/views.py', 'w', encoding='utf-8').write(''.join(new_lines))
print('OK!')
