with open('templates/gestion_demandes.html', 'r', encoding='utf-8') as f:
    content = f.read()

# Ajouter bouton Rendre pour demandes en_cours
content = content.replace(
    "{% elif demande.statut == 'en_cours' %}\n                                        <a href=\"{% url 'valider_demande' demande.id %}\" class=\"btn btn-sm btn-custom\" style=\"border-radius:20px\">\n                                            <i class=\"fas fa-eye\"></i> Voir\n                                        </a>",
    """{% elif demande.statut == 'en_cours' %}
                                        <div class="d-flex flex-column gap-1">
                                            <a href="{% url 'valider_demande' demande.id %}" class="btn btn-sm btn-custom" style="border-radius:20px">
                                                <i class="fas fa-eye"></i> Voir
                                            </a>
                                            <a href="{% url 'rendre_materiel' demande.id %}"
                                               class="btn btn-sm" style="background:#27ae60;color:white;border:none;border-radius:20px"
                                               onclick="return confirm('Confirmer le retour du materiel par l etudiant ?')">
                                                <i class="fas fa-undo"></i> Retour materiel
                                            </a>
                                        </div>"""
)

with open('templates/gestion_demandes.html', 'w', encoding='utf-8') as f:
    f.write(content)
print('Bouton Rendre ajoute cote admin!')
