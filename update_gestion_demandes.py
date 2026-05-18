with open('templates/gestion_demandes.html', 'w', encoding='utf-8') as f:
    f.write("""<!DOCTYPE html>
<html lang="fr">
<head>
    <meta charset="UTF-8">
    <title>Gestion des demandes - Admin</title>
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css" rel="stylesheet">
    <link href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0/css/all.min.css" rel="stylesheet">
    <style>
        .bg-custom { background-color: #2c3e50 !important; }
        .btn-custom { background-color: #2c3e50 !important; color: white !important; border: none; }
        body { background: #f0f2f5; }
        .card { border: none; border-radius: 12px; box-shadow: 0 2px 12px rgba(0,0,0,0.07); }
    </style>
</head>
<body>
<nav class="navbar navbar-dark bg-custom px-3">
    <span class="navbar-brand fw-bold"><i class="fas fa-clipboard-list"></i> Gestion des demandes</span>
    <a href="{% url 'dashboard' %}" class="btn btn-outline-light btn-sm"><i class="fas fa-arrow-left"></i> Dashboard</a>
</nav>

<div class="container-fluid p-4">
    {% if messages %}
        {% for message in messages %}
            <div class="alert alert-{{ message.tags }} alert-dismissible fade show py-2 small">
                {{ message }}<button type="button" class="btn-close btn-sm" data-bs-dismiss="alert"></button>
            </div>
        {% endfor %}
    {% endif %}

    <div class="card">
        <div class="card-body p-0">
            <div class="table-responsive">
                <table class="table table-hover mb-0">
                    <thead style="background:#2c3e50;color:white">
                        <tr>
                            <th class="ps-3">ID</th>
                            <th>Etudiant</th>
                            <th>Materiels</th>
                            <th>Dates</th>
                            <th>Statut</th>
                            <th>Actions</th>
                        </tr>
                    </thead>
                    <tbody>
                        {% for demande in demandes %}
                        <tr>
                            <td class="ps-3 fw-bold">#{{ demande.id }}</td>
                            <td>
                                <strong>{{ demande.utilisateur.username }}</strong><br>
                                <small class="text-muted">{{ demande.utilisateur.filiere|default:"-" }}</small>
                            </td>
                            <td>
                                {% for ligne in demande.lignes.all %}
                                    <span class="badge bg-secondary">{{ ligne.materiel.nom }} x{{ ligne.quantite }}</span><br>
                                {% endfor %}
                            </td>
                            <td class="small">
                                {{ demande.date_debut|date:"d/m/Y" }}<br>
                                <i class="fas fa-arrow-down text-muted" style="font-size:0.7rem"></i><br>
                                {{ demande.date_fin|date:"d/m/Y" }}
                            </td>
                            <td>
                                <span class="badge
                                    {% if demande.statut == 'en_attente' %}bg-warning
                                    {% elif demande.statut == 'approuvee' %}bg-success
                                    {% elif demande.statut == 'refusee' %}bg-danger
                                    {% elif demande.statut == 'en_cours' %}bg-info
                                    {% elif demande.statut == 'restituee' %}bg-secondary
                                    {% elif demande.statut == 'retard' %}bg-dark
                                    {% endif %}">
                                    {{ demande.get_statut_display }}
                                </span>
                            </td>
                            <td>
                                <div class="d-flex flex-column gap-1">
                                    {% if demande.statut == 'en_attente' %}
                                        <a href="{% url 'valider_demande' demande.id %}" class="btn btn-sm btn-custom" style="border-radius:20px">
                                            <i class="fas fa-check"></i> Traiter
                                        </a>
                                    {% elif demande.statut == 'approuvee' %}
                                        <a href="{% url 'valider_demande' demande.id %}" class="btn btn-sm btn-custom" style="border-radius:20px">
                                            <i class="fas fa-check"></i> Traiter
                                        </a>
                                        <a href="{% url 'recuperer_materiel' demande.id %}"
                                           class="btn btn-sm btn-warning" style="border-radius:20px"
                                           onclick="return confirm('Confirmer la remise du materiel a l etudiant ?')">
                                            <i class="fas fa-hand-holding"></i> Remettre
                                        </a>
                                    {% elif demande.statut == 'en_cours' %}
                                        <a href="{% url 'valider_demande' demande.id %}" class="btn btn-sm btn-custom" style="border-radius:20px">
                                            <i class="fas fa-eye"></i> Voir
                                        </a>
                                    {% elif demande.statut == 'restituee' %}
                                        <span class="text-success small"><i class="fas fa-check-circle"></i> Rendu</span>
                                    {% elif demande.statut == 'refusee' %}
                                        <span class="text-danger small"><i class="fas fa-times-circle"></i> Refuse</span>
                                    {% else %}
                                        <a href="{% url 'valider_demande' demande.id %}" class="btn btn-sm btn-custom" style="border-radius:20px">
                                            <i class="fas fa-eye"></i> Voir
                                        </a>
                                    {% endif %}
                                </div>
                            </td>
                        </tr>
                        {% empty %}
                        <tr><td colspan="6" class="text-center py-4 text-muted">Aucune demande</td></tr>
                        {% endfor %}
                    </tbody>
                </table>
            </div>
        </div>
    </div>
</div>
<script src="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/js/bootstrap.bundle.min.js"></script>
</body>
</html>""")
print('gestion_demandes.html mis a jour!')
