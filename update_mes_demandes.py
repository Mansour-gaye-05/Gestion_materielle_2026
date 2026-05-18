with open('templates/mes_demandes.html', 'w', encoding='utf-8') as f:
    f.write("""<!DOCTYPE html>
<html lang="fr">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=1.0">
    <meta name="theme-color" content="#2c3e50">
    <title>Mes demandes - UFR Sciences</title>
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css" rel="stylesheet">
    <link href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0/css/all.min.css" rel="stylesheet">
    <style>
        :root { --primary: #2c3e50; }
        body { background: #f0f2f5; padding-bottom: 80px; }
        .navbar-custom { background: var(--primary); position: sticky; top: 0; z-index: 1000; box-shadow: 0 2px 10px rgba(0,0,0,0.2); }

        /* BOTTOM NAV */
        .bottom-nav { display: none; position: fixed; bottom: 0; left: 0; right: 0; background: var(--primary); z-index: 1000; padding: 8px 0; box-shadow: 0 -2px 10px rgba(0,0,0,0.2); }
        .bottom-nav a { flex: 1; text-align: center; color: rgba(255,255,255,0.7); text-decoration: none; font-size: 0.65rem; display: flex; flex-direction: column; align-items: center; gap: 2px; }
        .bottom-nav a i { font-size: 1.2rem; }
        .bottom-nav a.active { color: white; }
        @media (max-width: 768px) { .bottom-nav { display: flex; } .desktop-nav { display: none !important; } }

        /* DEMANDE CARD MOBILE */
        .demande-card { background: white; border-radius: 16px; box-shadow: 0 2px 12px rgba(0,0,0,0.07); margin-bottom: 12px; overflow: hidden; border: none; }
        .demande-card-header { padding: 12px 15px 8px; border-bottom: 1px solid #f0f0f0; }
        .demande-card-body { padding: 10px 15px; }
        .demande-card-footer { padding: 10px 15px; background: #fafafa; border-top: 1px solid #f0f0f0; }

        /* STATUT COLORS */
        .statut-en_attente { border-top: 4px solid #f39c12; }
        .statut-approuvee { border-top: 4px solid #27ae60; }
        .statut-refusee { border-top: 4px solid #e74c3c; }
        .statut-en_cours { border-top: 4px solid #3498db; }
        .statut-restituee { border-top: 4px solid #95a5a6; }
        .statut-retard { border-top: 4px solid #c0392b; }

        /* ACTION BUTTONS */
        .btn-action { min-height: 46px; border-radius: 23px; font-weight: 600; font-size: 0.85rem; display: flex; align-items: center; justify-content: center; gap: 6px; width: 100%; }
        .btn-rendre { background: #27ae60; border: none; color: white; }
        .btn-rendre:hover { background: #219a52; color: white; }
        .btn-recuperer { background: #f39c12; border: none; color: white; }
        .btn-recuperer:hover { background: #d68910; color: white; }
        .btn-panne { background: #e74c3c; border: none; color: white; }
        .btn-panne:hover { background: #c0392b; color: white; }
        .btn-custom { background: var(--primary) !important; color: white !important; border: none; }

        /* TABLE DESKTOP */
        @media (min-width: 769px) { .card-view { display: none; } }
        @media (max-width: 768px) { .table-view { display: none; } }

        /* ALERTS */
        .alert { border-radius: 12px; font-size: 0.85rem; }
        .badge { font-size: 0.72rem; border-radius: 12px; padding: 4px 9px; }

        /* EMPTY STATE */
        .empty-state { text-align: center; padding: 50px 20px; }
        .empty-state i { font-size: 4rem; color: #dee2e6; }
    </style>
</head>
<body>
<!-- NAVBAR -->
<nav class="navbar navbar-dark navbar-custom px-3 py-2">
    <a class="navbar-brand small" href="{% url 'accueil' %}"><i class="fas fa-graduation-cap"></i> UFR Sciences</a>
    <div class="desktop-nav d-flex gap-2">
        <span class="text-white align-self-center small me-1"><i class="fas fa-user"></i> {{ user.username }}</span>
        <a href="{% url 'catalogue' %}" class="btn btn-outline-light btn-sm"><i class="fas fa-box"></i> Catalogue</a>
        <a href="{% url 'espace_etudiant' %}" class="btn btn-outline-light btn-sm"><i class="fas fa-home"></i> Mon espace</a>
        <a href="{% url 'deconnexion' %}" class="btn btn-outline-light btn-sm"><i class="fas fa-sign-out-alt"></i></a>
    </div>
</nav>

<!-- BOTTOM NAV -->
<div class="bottom-nav">
    <a href="{% url 'espace_etudiant' %}"><i class="fas fa-home"></i><span>Accueil</span></a>
    <a href="{% url 'catalogue' %}"><i class="fas fa-box"></i><span>Catalogue</span></a>
    <a href="{% url 'nouvelle_demande' %}" style="color:white">
        <div style="background:#e74c3c;border-radius:50%;width:48px;height:48px;display:flex;align-items:center;justify-content:center;margin-top:-20px;box-shadow:0 4px 12px rgba(231,76,60,0.4)">
            <i class="fas fa-plus" style="font-size:1.4rem"></i>
        </div>
        <span>Demander</span>
    </a>
    <a href="{% url 'mes_demandes' %}" class="active"><i class="fas fa-history"></i><span>Historique</span></a>
    <a href="{% url 'chatbot' %}"><i class="fas fa-robot"></i><span>IA</span></a>
</div>

<div class="container-fluid px-3 mt-3">
    <div class="d-flex justify-content-between align-items-center mb-3">
        <h6 class="fw-bold text-dark mb-0"><i class="fas fa-history"></i> Mes demandes</h6>
        <a href="{% url 'nouvelle_demande' %}" class="btn btn-sm btn-custom px-3" style="border-radius:20px">
            <i class="fas fa-plus"></i> Nouvelle
        </a>
    </div>

    <!-- ALERTS -->
    {% if messages %}
        {% for message in messages %}
            <div class="alert alert-{{ message.tags }} alert-dismissible fade show py-2">
                {{ message }}<button type="button" class="btn-close btn-sm" data-bs-dismiss="alert"></button>
            </div>
        {% endfor %}
    {% endif %}

    {% for demande in demandes %}
        {% if demande.statut == 'retard' %}
            <div class="alert alert-danger alert-dismissible fade show py-2 small">
                <i class="fas fa-exclamation-triangle"></i> <strong>RETARD</strong> — Demande #{{ demande.id }} en retard depuis le {{ demande.date_fin|date:"d/m/Y" }}
                <button type="button" class="btn-close btn-sm" data-bs-dismiss="alert"></button>
            </div>
        {% elif demande.statut == 'approuvee' %}
            <div class="alert alert-success alert-dismissible fade show py-2 small">
                <i class="fas fa-check-circle"></i> <strong>APPROUVEE</strong> — Demande #{{ demande.id }} approuvee ! Recuperez le materiel.
                <button type="button" class="btn-close btn-sm" data-bs-dismiss="alert"></button>
            </div>
        {% endif %}
    {% endfor %}

    <!-- VUE CARTES (MOBILE) -->
    <div class="card-view">
        {% for demande in demandes %}
        <div class="demande-card statut-{{ demande.statut }}">
            <div class="demande-card-header">
                <div class="d-flex justify-content-between align-items-start">
                    <div>
                        <span class="text-muted small">#{{ demande.id }} — {{ demande.date_demande|date:"d/m/Y" }}</span>
                        <div class="fw-bold mt-1">
                            {% for ligne in demande.lignes.all %}{{ ligne.materiel.nom }}{% if not forloop.last %}, {% endif %}{% endfor %}
                        </div>
                    </div>
                    <span class="badge {% if demande.statut == 'en_attente' %}bg-warning{% elif demande.statut == 'approuvee' %}bg-success{% elif demande.statut == 'refusee' %}bg-danger{% elif demande.statut == 'en_cours' %}bg-info{% elif demande.statut == 'restituee' %}bg-secondary{% else %}bg-dark{% endif %}">
                        {{ demande.get_statut_display }}
                    </span>
                </div>
            </div>
            <div class="demande-card-body">
                <div class="row g-1 small text-muted">
                    <div class="col-6"><i class="fas fa-calendar-alt"></i> Du {{ demande.date_debut|date:"d/m/Y" }}</div>
                    <div class="col-6"><i class="fas fa-calendar-check"></i> Au {{ demande.date_fin|date:"d/m/Y" }}</div>
                    {% if demande.motif_refus %}
                    <div class="col-12 text-danger mt-1"><i class="fas fa-times-circle"></i> {{ demande.motif_refus|truncatechars:60 }}</div>
                    {% endif %}
                </div>
            </div>
            {% if demande.statut == 'en_cours' or demande.statut == 'approuvee' %}
            <div class="demande-card-footer">
                {% if demande.statut == 'approuvee' %}
                    <a href="{% url 'recuperer_materiel' demande.id %}" class="btn btn-action btn-recuperer" onclick="return confirm('Confirmer la reception du materiel ?')">
                        <i class="fas fa-hand-peace"></i> Je recupere le materiel
                    </a>
                {% elif demande.statut == 'en_cours' %}
                    <div class="row g-2">
                        <div class="col-6">
                            <a href="{% url 'rendre_materiel' demande.id %}" class="btn btn-action btn-rendre" onclick="return confirm('Confirmer le retour ?')">
                                <i class="fas fa-undo"></i> Rendre
                            </a>
                        </div>
                        <div class="col-6">
                            <button class="btn btn-action btn-panne" data-bs-toggle="modal" data-bs-target="#panneModal{{ demande.id }}">
                                <i class="fas fa-exclamation-triangle"></i> Panne
                            </button>
                        </div>
                    </div>
                {% endif %}
            </div>
            {% endif %}
        </div>

        <!-- MODAL PANNE -->
        {% if demande.statut == 'en_cours' %}
        <div class="modal fade" id="panneModal{{ demande.id }}" tabindex="-1">
            <div class="modal-dialog modal-dialog-centered">
                <div class="modal-content" style="border-radius:16px;overflow:hidden">
                    <form method="post" action="{% url 'signaler_panne_emprunt' demande.id %}">
                        {% csrf_token %}
                        <div class="modal-header bg-danger text-white">
                            <h6 class="modal-title"><i class="fas fa-exclamation-triangle"></i> Signaler une panne</h6>
                            <button type="button" class="btn-close btn-close-white" data-bs-dismiss="modal"></button>
                        </div>
                        <div class="modal-body">
                            <p class="small text-muted mb-2">Materiel : <strong>{% for l in demande.lignes.all %}{{ l.materiel.nom }}{% endfor %}</strong></p>
                            <label class="form-label small fw-bold">Description du probleme :</label>
                            <textarea name="description" class="form-control" rows="4" placeholder="Ex: ne s allume plus, ecran casse, mesures incorrectes..." required style="border-radius:10px"></textarea>
                            <small class="text-muted mt-1 d-block"><i class="fas fa-info-circle"></i> Un technicien sera informe immediatement.</small>
                        </div>
                        <div class="modal-footer border-0 pt-0">
                            <button type="button" class="btn btn-outline-secondary btn-sm" data-bs-dismiss="modal">Annuler</button>
                            <button type="submit" class="btn btn-danger btn-sm px-4" style="border-radius:20px">Signaler</button>
                        </div>
                    </form>
                </div>
            </div>
        </div>
        {% endif %}
        {% empty %}
        <div class="empty-state">
            <i class="fas fa-inbox d-block mb-3"></i>
            <h6 class="text-muted">Aucune demande pour le moment</h6>
            <a href="{% url 'nouvelle_demande' %}" class="btn btn-custom mt-3 px-4" style="border-radius:25px">
                <i class="fas fa-plus-circle"></i> Faire une demande
            </a>
        </div>
        {% endfor %}
    </div>

    <!-- VUE TABLE (DESKTOP) -->
    <div class="table-view">
        <div class="card border-0 shadow-sm" style="border-radius:16px;overflow:hidden">
            <div class="card-body p-0">
                <div class="table-responsive">
                    <table class="table table-hover mb-0">
                        <thead style="background:#2c3e50;color:white">
                            <tr>
                                <th class="ps-3">ID</th>
                                <th>Date</th>
                                <th>Materiel</th>
                                <th>Periode</th>
                                <th>Statut</th>
                                <th>Actions</th>
                            </tr>
                        </thead>
                        <tbody>
                            {% for demande in demandes %}
                            <tr>
                                <td class="ps-3 fw-bold">#{{ demande.id }}</td>
                                <td class="small">{{ demande.date_demande|date:"d/m/Y" }}</td>
                                <td>{% for l in demande.lignes.all %}<strong>{{ l.materiel.nom|truncatechars:25 }}</strong>{% endfor %}</td>
                                <td class="small">{{ demande.date_debut|date:"d/m" }} → {{ demande.date_fin|date:"d/m/Y" }}</td>
                                <td>
                                    <span class="badge {% if demande.statut == 'en_attente' %}bg-warning{% elif demande.statut == 'approuvee' %}bg-success{% elif demande.statut == 'refusee' %}bg-danger{% elif demande.statut == 'en_cours' %}bg-info{% elif demande.statut == 'restituee' %}bg-secondary{% else %}bg-dark{% endif %}">
                                        {{ demande.get_statut_display }}
                                    </span>
                                </td>
                                <td>
                                    {% if demande.statut == 'approuvee' %}
                                        <a href="{% url 'recuperer_materiel' demande.id %}" class="btn btn-sm btn-recuperer" onclick="return confirm('Confirmer ?')" style="border-radius:20px">
                                            <i class="fas fa-hand-peace"></i> Recuperer
                                        </a>
                                    {% elif demande.statut == 'en_cours' %}
                                        <div class="d-flex gap-1">
                                            <a href="{% url 'rendre_materiel' demande.id %}" class="btn btn-sm btn-rendre" onclick="return confirm('Confirmer le retour ?')" style="border-radius:20px">
                                                <i class="fas fa-undo"></i> Rendre
                                            </a>
                                            <button class="btn btn-sm btn-panne" data-bs-toggle="modal" data-bs-target="#panneModal{{ demande.id }}" style="border-radius:20px">
                                                <i class="fas fa-exclamation-triangle"></i>
                                            </button>
                                        </div>
                                    {% elif demande.statut == 'en_attente' %}
                                        <span class="text-muted small"><i class="fas fa-hourglass-half"></i> En attente</span>
                                    {% elif demande.statut == 'restituee' %}
                                        <span class="text-success small"><i class="fas fa-check-circle"></i> Rendu</span>
                                    {% else %}—{% endif %}
                                </td>
                            </tr>
                            {% empty %}
                            <tr><td colspan="6" class="text-center py-5 text-muted">
                                <i class="fas fa-inbox fa-3x d-block mb-2"></i>Aucune demande
                                <a href="{% url 'nouvelle_demande' %}" class="btn btn-custom btn-sm mt-2">Faire une demande</a>
                            </td></tr>
                            {% endfor %}
                        </tbody>
                    </table>
                </div>
            </div>
        </div>
    </div>
</div>
<script src="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/js/bootstrap.bundle.min.js"></script>
</body>
</html>""")
print('mes_demandes.html mis a jour!')
