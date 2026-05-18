with open('templates/dashboard.html', 'r', encoding='utf-8') as f:
    content = f.read()

import re

# Remplacer ou ajouter bg-custom dans le style
if '.bg-custom' not in content:
    content = content.replace('<style>', '<style>\n        .bg-custom { background-color: #2c3e50 !important; }')
    print('bg-custom ajoute')
else:
    # Corriger la valeur existante
    content = re.sub(r'\.bg-custom\s*\{[^}]*\}', '.bg-custom { background-color: #2c3e50 !important; }', content)
    print('bg-custom corrige')

with open('templates/dashboard.html', 'w', encoding='utf-8') as f:
    f.write(content)
print('Done!')
