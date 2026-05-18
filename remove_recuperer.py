with open('templates/mes_demandes.html', 'r', encoding='utf-8') as f:
    content = f.read()

# Supprimer bouton recuperer dans vue cartes mobile
import re
content = re.sub(
    r'\{%\s*elif demande\.statut == .approuvee. %\}.*?<a href="\{%\s*url .recuperer_materiel.*?</a>',
    "{% elif demande.statut == 'approuvee' %}\n                        <div class=\"text-success small p-2\"><i class=\"fas fa-check-circle\"></i> Approuvee — Presentez-vous au laboratoire pour recuperer le materiel.</div>",
    content,
    flags=re.DOTALL
)

with open('templates/mes_demandes.html', 'w', encoding='utf-8') as f:
    f.write(content)
print('Bouton recuperer supprime de mes_demandes!')
