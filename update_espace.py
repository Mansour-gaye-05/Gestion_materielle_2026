with open('templates/espace_etudiant.html', 'w', encoding='utf-8') as f:
    f.write("""<!DOCTYPE html>
<html lang="fr">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=1.0">
    <meta name="theme-color" content="#2c3e50">
    <title>Mon Espace - UFR Sciences</title>
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css" rel="stylesheet">
    <link href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0/css/all.min.css" rel="stylesheet">
    <style>
        :root { --primary: #2c3e50; --primary-light: #3498db; }
        body { background: #f0f2f5; padding-bottom: 80px; }

        /* NAVBAR MOBILE */
        .navbar-custom { background: var(--primary); position: sticky; top: 0; z-index: 1000; box-shadow: 0 2px 10px rgba(0,0,0,0.2); }
        .navbar-brand { font-size: 1rem; }

        /* BOTTOM NAV MOBILE */
        .bottom-nav { display: none; position: fixed; bottom: 0; left: 0; right: 0; background: var(--primary); z-index: 1000; padding: 8px 0; box-shadow: 0 -2px 10px rgba(0,0,0,0.2); }
        .bottom-nav a { flex: 1; text-align: center; color: rgba(255,255,255,0.7); text-decoration: none; font-size: 0.65rem; display: flex; flex-direction: column; align-items: center; gap: 2px; padding: 2px 0; }
        .bottom-nav a i { font-size: 1.2rem; }
        .bottom-nav a.active { color: white; }
        .bottom-nav a .badge-dot { width: 6px; height: 6px; background: #e74c3c; border-radius: 50%; position: absolute; top: 0; right: calc(50% - 10px); }
        @media (max-width: 768px) {
            .bottom-nav { display: flex; }
            .desktop-nav { display: none; }
            body { padding-bottom: 70px; }
        }

        /* WELCOME CARD */
        .welcome-card { background: linear-gradient(135deg, #2c3e50, #3498db); border: none; border-radius: 16px; }

        /* STAT CARDS */
        .stat-card { border: none; border-radius: 16px; transition: transform 0.2s; min-height: 90px; }
        .stat-card:active { transform: scale(0.97); }
        .stat-icon { font-size: 1.8rem; opacity: 0.25; position: absolute; right: 15px; top: 50%; transform: translateY(-50%); }
        .stat-card h2 { font-size: 1.8rem; font-weight: 700; margin: 0; }
        .stat-card p { font-size: 0.75rem; margin: 0; opacity: 0.9; }

        /* EMPRUNT CARDS MOBILE */
        .emprunt-card { border-radius: 12px; border: none; box-shadow: 0 2px 8px rgba(0,0,0,0.08); margin-bottom: 10px; }
        .emprunt-card .card-body { padding: 12px 15px; }

        /* ACTION BUTTONS */
        .btn-action { min-height: 48px; font-size: 0.85rem; border-radius: 25px; font-weight: 600; display: flex; align-items: center; justify-content: center; gap: 6px; }
        .btn-custom { background: var(--primary) !important; border-color: var(--primary) !important; color: white !important; }

        /* TABLE MOBILE */
        @media (max-width: 768px) {
            .table-to-cards thead { display: none; }
            .table-to-cards tbody tr { display: block; background: white; border-radius: 12px; margin-bottom: 10px; box-shadow: 0 2px 8px rgba(0,0,0,0.06); padding: 12px; border: none; }
            .table-to-cards tbody td { display: block; border: none; padding: 3px 0; font-size: 0.85rem; }
            .table-to-cards tbody td::before { content: attr(data-label); font-weight: 700; color: #666; font-size: 0.75rem; display: block; }
        }

        /* NOTIFICATION */
        .notif-item { border-left: 3px solid var(--primary); background: white; border-radius: 0 8px 8px 0; padding: 8px 12px; margin-bottom: 8px; font-size: 0.82rem; }

        /* SCROLLABLE */
        .scroll-section { max-height: 320px; overflow-y: auto; }
        .scroll-section::-webkit-scrollbar { width: 4px; }
        .scroll-section::-webkit-scrollbar-thumb { background: #ccc; border-radius: 4px; }

        /* SECTION TITLES */
        .section-title { font-size: 0.9rem; font-weight: 700; color: var(--primary); border-left: 3px solid var(--primary); padding-left: 8px; margin-bottom: 12px; }

        /* BADGE STATUT */
        .badge { font-size: 0.72rem; padding: 4px 8px; border-radius: 12px; }
    </style>
</head>
<body>
<!-- NAVBAR -->
<nav class="navbar navbar-dark navbar-custom px-3 py-2">
    <a class="navbar-brand" href="#"><i class="fas fa-graduation-cap"></i> UFR Sciences</a>
    <div class="desktop-nav d-flex gap-2">
        <span class="text-white align-self-center me-1 small"><i class="fas fa-user"></i> {{ user.username }}</span>
        <a href="{% url 'nouvelle_demande' %}" class="btn btn-outline-light btn-sm"><i class="fas fa-plus"></i> Demande</a>
        <a href="{% url 'catalogue' %}" class="btn btn-outline-light btn-sm"><i class="fas fa-box"></i> Catalogue</a>
        <a href="{% url 'chatbot' %}" class="btn btn-outline-light btn-sm"><i class="fas fa-robot"></i> IA</a>
        <a href="{% url 'deconnexion' %}" class="btn btn-outline-light btn-sm"><i class="fas fa-sign-out-alt"></i></a>
    </div>
</nav>

<!-- BOTTOM NAV MOBILE -->
<div class="bottom-nav">
    <a href="{% url 'espace_etudiant' %}" class="active">
        <i class="fas fa-home"></i><span>Accueil</span>
    </a>
    <a href="{% url 'catalogue' %}">
        <i class="fas fa-box"></i><span>Catalogue</span>
    </a>
    <a href="{% url 'nouvelle_demande' %}" style="color:white">
        <div style="background:#e74c3c;border-radius:50%;width:48px;height:48px;display:flex;align-items:center;justify-content:center;margin-top:-20px;box-shadow:0 4px 12px rgba(231,76,60,0.4)">
            <i class="fas fa-plus" style="font-size:1.4rem"></i>
        </div>
        <span>Demander</span>
    </a>
    <a href="{% url 'mes_demandes' %}">
        <i class="fas fa-history"></i><span>Historique</span>
    </a>
    <a href="{% url 'chatbot' %}">
        <i class="fas fa-robot"></i><span>IA</span>
    </a>
</div>

<div class="container-fluid px-3 mt-3">
    <!-- MESSAGES -->
    {% if messages %}
        {% for message in messages %}
            <div class="alert alert-{{ message.tags }} alert-dismissible fade show py-2 small">
                {{ message }}<button type="button" class="btn-close btn-sm" data-bs-dismiss="alert"></button>
            </div>
        {% endfor %}
    {% endif %}

    <!-- WELCOME -->
    <div class="card welcome-card text-white mb-3">
        <div class="card-body py-3">
            <div class="d-flex justify-content-between align-items-center">
                <div>
                    <h5 class="mb-1"><i class="fas fa-smile-wink"></i> Bonjour {{ user.username }} !</h5>
                    <small class="opacity-75"><i class="fas fa-graduation-cap"></i> {{ user.filiere|default:"Filiere non renseignee" }} — {{ user.niveau|default:"Niveau non renseigne" }}</small>
                </div>
                <a href="{% url 'profil_etudiant' %}" class="btn btn-outline-light btn-sm"><i class="fas fa-edit"></i></a>
            </div>
        </div>
    </div>

    <!-- STATS GRID -->
    <div class="row g-2 mb-3">
        <div class="col-4">
            <div class="card stat-card bg-primary text-white position-relative">
                <div class="card-body py-3 px-2">
                    <i class="fas fa-clipboard-list stat-icon"></i>
                    <h2>{{ stats.total }}</h2>
                    <p>Total</p>
                </div>
            </div>
        </div>
        <div class="col-4">
            <div class="card stat-card bg-warning text-white position-relative">
                <div class="card-body py-3 px-2">
                    <i class="fas fa-clock stat-icon"></i>
                    <h2>{{ stats.en_attente }}</h2>
                    <p>En attente</p>
                </div>
            </div>
        </div>
        <div class="col-4">
            <div class="card stat-card bg-success text-white position-relative">
                <div class="card-body py-3 px-2">
                    <i class="fas fa-check stat-icon"></i>
                    <h2>{{ stats.approuvees }}</h2>
                    <p>Approuvees</p>
                </div>
            </div>
        </div>
        <div class="col-4">
            <div class="card stat-card bg-info text-white position-relative">
                <div class="card-body py-3 px-2">
                    <i class="fas fa-hand-peace stat-icon"></i>
                    <h2>{{ stats.en_cours }}</h2>
                    <p>En cours</p>
                </div>
            </div>
        </div>
        <div class="col-4">
            <div class="card stat-card bg-secondary text-white position-relative">
                <div class="card-body py-3 px-2">
                    <i class="fas fa-undo stat-icon"></i>
                    <h2>{{ stats.restituees }}</h2>
                    <p>Rendus</p>
                </div>
            </div>
        </div>
        <div class="col-4">
            <div class="card stat-card bg-danger text-white position-relative">
                <div class="card-body py-3 px-2">
                    <i class="fas fa-exclamation stat-icon"></i>
                    <h2>{{ stats.retard }}</h2>
                    <p>Retards</p>
                </div>
            </div>
        </div>
    </div>

    <!-- EMPRUNTS EN COURS -->
    {% if emprunts_actifs %}
    <div class="mb-3">
        <div class="section-title"><i class="fas fa-hand-peace"></i> Emprunts en cours ({{ emprunts_actifs.count }})</div>
        {% for emprunt in emprunts_actifs %}
        <div class="emprunt-card card {% if emprunt.date_fin < today %}border-danger{% else %}border-0{% endif %}">
            <div class="card-body">
                <div class="d-flex justify-content-between align-items-start mb-2">
                    <div>
                        <strong class="d-block">{% for l in emprunt.lignes.all %}{{ l.materiel.nom }}{% endfor %}</strong>
                        <small class="{% if emprunt.date_fin < today %}text-danger fw-bold{% else %}text-muted{% endif %}">
                            {% if emprunt.date_fin < today %}
                                <i class="fas fa-exclamation-triangle"></i> En retard — retour le {{ emprunt.date_fin|date:"d/m/Y" }}
                            {% else %}
                                <i class="fas fa-calendar"></i> Retour le {{ emprunt.date_fin|date:"d/m/Y" }}
                            {% endif %}
                        </small>
                    </div>
                    <span class="badge bg-info">En cours</span>
                </div>
                <div class="d-flex gap-2">
                    <a href="{% url 'rendre_materiel' emprunt.id %}" class="btn btn-action btn-sm flex-fill" style="background:#27ae60;color:white;border:none" onclick="return confirm('Confirmer le retour ?')">
                        <i class="fas fa-undo"></i> Rendre
                    </a>
                    <a href="{% url 'mes_demandes' %}" class="btn btn-action btn-sm flex-fill btn-outline-secondary">
                        <i class="fas fa-eye"></i> Details
                    </a>
                </div>
            </div>
        </div>
        {% endfor %}
    </div>
    {% endif %}

    <!-- DERNIERES DEMANDES -->
    <div class="mb-3">
        <div class="d-flex justify-content-between align-items-center mb-2">
            <div class="section-title mb-0"><i class="fas fa-history"></i> Dernieres demandes</div>
            <a href="{% url 'mes_demandes' %}" class="btn btn-sm btn-outline-secondary" style="font-size:0.75rem">Tout voir</a>
        </div>
        <div class="table-responsive">
            <table class="table table-hover table-to-cards">
                <thead class="table-dark small">
                    <tr><th>Materiel</th><th>Periode</th><th>Statut</th></tr>
                </thead>
                <tbody>
                    {% for demande in demandes %}
                    <tr>
                        <td data-label="Materiel">{% for l in demande.lignes.all %}<strong>{{ l.materiel.nom|truncatechars:25 }}</strong>{% endfor %}</td>
                        <td data-label="Periode">{{ demande.date_debut|date:"d/m" }} → {{ demande.date_fin|date:"d/m/Y" }}</td>
                        <td data-label="Statut">
                            <span class="badge {% if demande.statut == 'en_attente' %}bg-warning{% elif demande.statut == 'approuvee' %}bg-success{% elif demande.statut == 'refusee' %}bg-danger{% elif demande.statut == 'en_cours' %}bg-info{% elif demande.statut == 'restituee' %}bg-secondary{% else %}bg-dark{% endif %}">
                                {{ demande.get_statut_display }}
                            </span>
                        </td>
                    </tr>
                    {% empty %}
                    <tr><td colspan="3" class="text-center text-muted py-3">Aucune demande</td></tr>
                    {% endfor %}
                </tbody>
            </table>
        </div>
    </div>

    <!-- NOTIFICATIONS -->
    {% if notifications %}
    <div class="mb-3">
        <div class="section-title"><i class="fas fa-bell"></i> Notifications</div>
        <div class="scroll-section">
            {% for notif in notifications %}
            <div class="notif-item">
                <small class="text-muted">{{ notif.date|date:"d/m H:i" }}</small>
                <p class="mb-0 small">{{ notif.message|truncatechars:90 }}</p>
            </div>
            {% endfor %}
        </div>
    </div>
    {% endif %}

    <!-- ACTIONS RAPIDES DESKTOP -->
    <div class="desktop-nav">
        <div class="card border-0 shadow-sm">
            <div class="card-body">
                <div class="section-title"><i class="fas fa-bolt"></i> Actions rapides</div>
                <div class="row g-2">
                    <div class="col-md-3"><a href="{% url 'nouvelle_demande' %}" class="btn btn-custom btn-action w-100"><i class="fas fa-plus-circle"></i> Nouvelle demande</a></div>
                    <div class="col-md-3"><a href="{% url 'catalogue' %}" class="btn btn-outline-primary btn-action w-100"><i class="fas fa-box"></i> Catalogue</a></div>
                    <div class="col-md-3"><a href="{% url 'mes_demandes' %}" class="btn btn-outline-info btn-action w-100"><i class="fas fa-history"></i> Historique</a></div>
                    <div class="col-md-3"><a href="{% url 'chatbot' %}" class="btn btn-outline-secondary btn-action w-100"><i class="fas fa-robot"></i> Assistant IA</a></div>
                </div>
            </div>
        </div>
    </div>
</div>
<script src="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/js/bootstrap.bundle.min.js"></script>
</body>
</html>""")
print('espace_etudiant.html mis a jour!')
