lines = open('templates/dashboard.html', 'r', encoding='utf-8').readlines()
for i, l in enumerate(lines, 1):
    if 'deconnexion' in l and 'btn-outline-danger' in l:
        print(f'Ligne {i}: {repr(l)}')
