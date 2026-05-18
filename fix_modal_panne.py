with open('templates/mes_demandes.html', 'r', encoding='utf-8') as f:
    content = f.read()

import re

# Extraire tous les modals panne
modals = re.findall(r'<!-- MODAL PANNE -->.*?{% endif %}\s*\n\s*{% empty %}', content, re.DOTALL)

if modals:
    # Extraire le contenu des modals sans le marqueur empty
    modal_content = re.findall(r'<!-- MODAL PANNE -->.*?</div>\s*\n\s*{% endif %}', content, re.DOTALL)
    modals_html = '\n'.join(modal_content)

    # Supprimer les modals de leur position actuelle
    content = re.sub(
        r'\s*<!-- MODAL PANNE -->.*?{% endif %}\s*\n(\s*{% empty %})',
        r'\n        \1',
        content,
        flags=re.DOTALL
    )

    # Ajouter les modals juste avant </body>
    content = content.replace(
        '<script src="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/js/bootstrap.bundle.min.js"></script>',
        modals_html + '\n<script src="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/js/bootstrap.bundle.min.js"></script>'
    )
    print('Modals deplaces!')
else:
    print('Modals non trouves')

with open('templates/mes_demandes.html', 'w', encoding='utf-8') as f:
    f.write(content)
