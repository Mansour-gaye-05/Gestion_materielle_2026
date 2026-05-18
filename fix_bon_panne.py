with open('templates/mes_demandes.html', 'r', encoding='utf-8') as f:
    content = f.read()

# 1. Corriger l'URL du bon de sortie (unifier vers bon_sortie_pdf)
content = content.replace(
    "{% url 'pdf_bon_sortie' demande.id %}",
    "{% url 'bon_sortie_pdf' demande.id %}"
)

# 2. Supprimer le bon de sortie de la vue etudiant (vue cartes mobile - ligne ~171)
import re

# Supprimer dans vue mobile (card-view)
content = re.sub(
    r'<a href="\{%\s*url .bon_sortie_pdf. demande\.id %\}"[^>]*target="_blank"[^>]*>.*?</a>',
    '',
    content,
    flags=re.DOTALL
)

# 3. Garder le bon de sortie uniquement pour admin dans vue desktop
# Remplacer le bouton bon de sortie dans vue desktop par verification is_staff
content = content.replace(
    '<a href="{% url \'bon_sortie_pdf\' demande.id %}" class="btn btn-sm btn-outline-secondary" style="border-radius:20px;font-size:0.75rem">\n                                            <i class="fas fa-file-pdf"></i> Bon de sortie\n                                        </a>',
    ''
)

with open('templates/mes_demandes.html', 'w', encoding='utf-8') as f:
    f.write(content)
print('Done!')
