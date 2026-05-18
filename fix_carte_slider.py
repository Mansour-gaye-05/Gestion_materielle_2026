with open('templates/carte_materiels.html', 'r', encoding='utf-8') as f:
    content = f.read()

# Corriger la valeur initiale du slider
content = content.replace(
    'min="0" max="6" value="6" step="1"',
    'min="0" max="12" value="12" step="1"'
)

# Corriger filterByTime - valeur 12 = Tout voir
content = content.replace(
    "visiblePoints = v === 12 ? [...emplacements] : emplacements.filter(p => p.mois === v);",
    "visiblePoints = v === 12 ? [...emplacements] : emplacements.filter(p => p.mois == v);"
)

with open('templates/carte_materiels.html', 'w', encoding='utf-8') as f:
    f.write(content)
print('Carte corrigee!')
