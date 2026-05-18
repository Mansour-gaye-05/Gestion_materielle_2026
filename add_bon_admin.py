with open('templates/gestion_demandes.html', 'r', encoding='utf-8') as f:
    content = f.read()

content = content.replace(
    "{% elif demande.statut == 'restituee' %}\n                                        <span class=\"text-success small\"><i class=\"fas fa-check-circle\"></i> Rendu</span>",
    "{% elif demande.statut == 'restituee' %}\n                                        <div class=\"d-flex flex-column gap-1\">\n                                            <span class=\"text-success small\"><i class=\"fas fa-check-circle\"></i> Rendu</span>\n                                            <a href=\"{% url 'bon_sortie_pdf' demande.id %}\" target=\"_blank\" class=\"btn btn-sm btn-outline-primary\" style=\"border-radius:20px;font-size:0.75rem\">\n                                                <i class=\"fas fa-file-pdf\"></i> Bon de sortie\n                                            </a>\n                                        </div>"
)

with open('templates/gestion_demandes.html', 'w', encoding='utf-8') as f:
    f.write(content)
print('Bon de sortie ajoute cote admin!')
