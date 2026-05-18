with open('templates/espace_etudiant.html', 'r', encoding='utf-8') as f:
    content = f.read()

import re
content = re.sub(
    r'<a href="\{%\s*url .recuperer_materiel.*?</a>',
    '',
    content,
    flags=re.DOTALL
)

with open('templates/espace_etudiant.html', 'w', encoding='utf-8') as f:
    f.write(content)
print('Bouton recuperer supprime de espace_etudiant!')
