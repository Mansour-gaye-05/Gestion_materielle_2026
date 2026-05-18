with open('templates/dashboard.html', 'r', encoding='utf-8') as f:
    content = f.read()

import re

# Supprimer le bloc Materiels par categorie
content = re.sub(
    r'<div class="col-md-4">\s*<div class="card p-3">\s*<div class="section-title">Materiels par categorie</div>\s*<canvas id="categorieChart"></canvas>\s*</div>\s*</div>',
    '',
    content,
    flags=re.DOTALL
)

# Supprimer le bloc Taux de panne
content = re.sub(
    r'<div class="col-md-6">\s*<div class="card p-3">\s*<div class="section-title">Taux de panne par materiel</div>\s*<canvas id="pannesChart".*?</div>\s*</div>',
    '',
    content,
    flags=re.DOTALL
)

# Supprimer le JS categorieChart
content = re.sub(
    r'new Chart\(document\.getElementById\(.categorieChart.\).*?\}\);',
    '',
    content,
    flags=re.DOTALL
)

# Supprimer le JS pannesChart
content = re.sub(
    r'new Chart\(document\.getElementById\(.pannesChart.\).*?\}\);',
    '',
    content,
    flags=re.DOTALL
)

# Mettre demandes recentes en pleine largeur maintenant
content = content.replace(
    '<div class="col-md-6">\n            <div class="card p-3">\n                <div class="section-title">Demandes recentes</div>',
    '<div class="col-md-12">\n            <div class="card p-3">\n                <div class="section-title">Demandes recentes</div>'
)

with open('templates/dashboard.html', 'w', encoding='utf-8') as f:
    f.write(content)
print('Graphiques supprimes!')
