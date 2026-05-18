lines = open('gestion/views.py', 'r', encoding='utf-8').readlines()
# Supprimer la ligne 1009 qui est un reste
del lines[1008]  # index 0-based = ligne 1009
open('gestion/views.py', 'w', encoding='utf-8').write(''.join(lines))
print('Ligne supprimee!')
