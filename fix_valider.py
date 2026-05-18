lines = open('gestion/views.py', 'r', encoding='utf-8').readlines()
new_lines = []
for i, line in enumerate(lines, 1):
    if i == 232:
        # Supprimer le demande.save() mal place dans le bloc approuver
        pass
    elif i == 239:
        # Ajouter demande.save() avant le redirect, pour les deux cas
        new_lines.append('        demande.save()\n')
        new_lines.append(line)
    else:
        new_lines.append(line)
open('gestion/views.py', 'w', encoding='utf-8').write(''.join(new_lines))
print('Correction appliquee!')
