with open('templates/dashboard.html', 'r', encoding='utf-8') as f:
    content = f.read()

# Remplacer le canvas par un div conteneur avec hauteur fixe
content = content.replace(
    '<canvas id="evolutionChart" height="60"></canvas>',
    '<div style="height:300px;position:relative"><canvas id="evolutionChart"></canvas></div>'
)

# Fixer maintainAspectRatio a false
content = content.replace(
    'maintainAspectRatio: true,',
    'maintainAspectRatio: false,'
)

with open('templates/dashboard.html', 'w', encoding='utf-8') as f:
    f.write(content)
print('Done!')
