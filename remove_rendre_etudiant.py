with open('templates/mes_demandes.html', 'r', encoding='utf-8') as f:
    content = f.read()

import re

# Remplacer le bloc rendre dans vue cartes mobile par message informatif
content = re.sub(
    r'<div class="col-6">\s*<a href="\{%\s*url .rendre_materiel. demande\.id %\}".*?</a>\s*</div>',
    '',
    content,
    flags=re.DOTALL
)

# Remplacer dans vue desktop table
content = re.sub(
    r'<a href="\{%\s*url .rendre_materiel. demande\.id %\}".*?Rendre\s*</a>',
    '',
    content,
    flags=re.DOTALL
)

# Remplacer le message apres suppression du bouton rendre dans mobile
content = content.replace(
    "{% elif demande.statut == 'en_cours' %}\n                        <div class=\"row g-2\">\n                            <div class=\"col-6\">\n                                \n                            </div>",
    "{% elif demande.statut == 'en_cours' %}\n                        <div class=\"text-info small p-2\"><i class=\"fas fa-info-circle\"></i> Presentez-vous au laboratoire pour restituer le materiel.</div>"
)

with open('templates/mes_demandes.html', 'w', encoding='utf-8') as f:
    f.write(content)
print('Bouton Rendre retire de mes_demandes!')
