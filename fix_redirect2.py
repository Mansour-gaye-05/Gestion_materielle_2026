lines = open('gestion/views.py', 'r', encoding='utf-8').readlines()

# Trouver la ligne return redirect mes_demandes dans recuperer_materiel
for i, l in enumerate(lines):
    if 'def recuperer_materiel' in l:
        start = i
    if start and 'return redirect' in l and 'mes_demandes' in l and i > start:
        lines[i] = "    if request.user.is_staff or request.user.is_superuser:\n        return redirect('gestion_demandes')\n    return redirect('mes_demandes')\n"
        print(f'Ligne {i+1} corrigee!')
        break

open('gestion/views.py', 'w', encoding='utf-8').write(''.join(lines))
