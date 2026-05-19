with open('templates/mes_demandes.html', 'r', encoding='utf-8') as f:
    content = f.read()

# Ajouter bouton annuler dans vue cartes mobile pour en_attente et approuvee
content = content.replace(
    "{% if demande.statut == 'approuvee' %}\n                    <div style=\"font-size:0.78rem;color:var(--success)\"><i class=\"fas fa-check-circle me-1\"></i> Approuvee — Presentez-vous au laboratoire pour recuperer le materiel.</div>",
    """{% if demande.statut == 'approuvee' %}
                    <div style="font-size:0.78rem;color:var(--success)" class="mb-2"><i class="fas fa-check-circle me-1"></i> Approuvee — Presentez-vous au laboratoire.</div>
                    <a href="{% url 'annuler_demande' demande.id %}"
                       class="btn btn-action" style="background:#e74c3c;color:white;font-size:0.78rem"
                       onclick="return confirm('Confirmer l annulation de cette demande ?')">
                        <i class="fas fa-times-circle"></i> Annuler la demande
                    </a>"""
)

# Ajouter bouton annuler pour en_attente dans vue cartes mobile
content = content.replace(
    "{% elif demande.statut == 'en_cours' %}\n                    <div class=\"row g-2\">\n                        <div class=\"col-12\">\n                            <button class=\"btn btn-action btn-signaler\"",
    """{% elif demande.statut == 'en_attente' %}
                    <a href="{% url 'annuler_demande' demande.id %}"
                       class="btn btn-action" style="background:#e74c3c;color:white;font-size:0.78rem"
                       onclick="return confirm('Confirmer l annulation ?')">
                        <i class="fas fa-times-circle"></i> Annuler la demande
                    </a>
                {% elif demande.statut == 'en_cours' %}
                    <div class="row g-2">
                        <div class="col-12">
                            <button class="btn btn-action btn-signaler\""""
)

# Ajouter dans vue table desktop
content = content.replace(
    "{% elif demande.statut == 'en_attente' %}\n                                <span class=\"small text-muted\"><i class=\"fas fa-hourglass-half\"></i> En attente</span>",
    """{% elif demande.statut == 'en_attente' %}
                                <a href="{% url 'annuler_demande' demande.id %}"
                                   class="btn btn-sm" style="background:#e74c3c;color:white;border-radius:20px;font-size:0.75rem;padding:4px 12px"
                                   onclick="return confirm('Annuler cette demande ?')">
                                    <i class="fas fa-times-circle"></i> Annuler
                                </a>"""
)

# Aussi pour approuvee dans vue table desktop
content = content.replace(
    "{% elif demande.statut == 'approuvee' %}\n                                <span class=\"small text-success\"><i class=\"fas fa-check-circle\"></i> Allez au labo</span>",
    """{% elif demande.statut == 'approuvee' %}
                                <div class="d-flex flex-column gap-1">
                                    <span class="small text-success"><i class="fas fa-check-circle"></i> Allez au labo</span>
                                    <a href="{% url 'annuler_demande' demande.id %}"
                                       class="btn btn-sm" style="background:#e74c3c;color:white;border-radius:20px;font-size:0.72rem;padding:3px 10px"
                                       onclick="return confirm('Annuler cette demande ?')">
                                        <i class="fas fa-times-circle"></i> Annuler
                                    </a>
                                </div>"""
)

with open('templates/mes_demandes.html', 'w', encoding='utf-8') as f:
    f.write(content)
print('Bouton annuler ajoute dans mes_demandes!')
