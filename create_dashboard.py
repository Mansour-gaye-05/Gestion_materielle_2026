with open('templates/dashboard.html', 'w', encoding='utf-8') as f:
    f.write(r"""<!DOCTYPE html>
<html lang="fr">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Dashboard - UFR Sciences</title>
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css" rel="stylesheet">
    <link href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0/css/all.min.css" rel="stylesheet">
    <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
    <style>
        body { background: #f0f2f5; }
        .bg-custom { background-color: #2c3e50 !important; }
        .btn-custom { background-color: #2c3e50 !important; border-color: #2c3e50 !important; color:white !important; }
        .card { border: none; border-radius: 12px; box-shadow: 0 2px 12px rgba(0,0,0,0.08); }
        .card-header { border-radius: 12px 12px 0 0 !important; font-weight: 600; }
        .stat-card { border-radius: 12px; color: white; padding: 20px; position: relative; overflow: hidden; }
        .stat-card .icon { font-size: 2.5rem; opacity: 0.3; position: absolute; right: 15px; top: 15px; }
        .stat-card h2 { font-size: 2rem; font-weight: 700; margin: 0; }
        .stat-card p { margin: 0; opacity: 0.9; font-size: 0.9rem; }
        .chart-container { position: relative; }
        .section-title { font-size: 1.1rem; font-weight: 700; color: #2c3e50; border-left: 4px solid #2c3e50; padding-left: 10px; margin-bottom: 20px; }
    </style>
</head>
<body>
<nav class="navbar navbar-dark bg-custom px-3">
    <span class="navbar-brand fw-bold"><i class="fas fa-chart-line"></i> Dashboard Admin — UFR Sciences</span>
    <div class="d-flex gap-2">
        <span class="text-white align-self-center me-2"><i class="fas fa-user"></i> {{ user.username }}</span>
        <a href="{% url 'catalogue' %}" class="btn btn-outline-light btn-sm"><i class="fas fa-box"></i> Catalogue</a>
        <a href="/admin/" class="btn btn-outline-light btn-sm"><i class="fas fa-cog"></i> Admin</a>
        <a href="{% url 'journal_activite' %}" class="btn btn-outline-light btn-sm"><i class="fas fa-history"></i> Journal</a>
        <a href="{% url 'deconnexion' %}" class="btn btn-outline-light btn-sm"><i class="fas fa-sign-out-alt"></i></a>
    </div>
</nav>

<div class="container-fluid p-4">

    <!-- KPI ROW 1 -->
    <div class="row g-3 mb-4">
        <div class="col-md-2">
            <div class="stat-card" style="background:linear-gradient(135deg,#2c3e50,#4a6fa5)">
                <i class="fas fa-microchip icon"></i>
                <h2>{{ total_materiels }}</h2>
                <p>Total Materiels</p>
            </div>
        </div>
        <div class="col-md-2">
            <div class="stat-card" style="background:linear-gradient(135deg,#27ae60,#2ecc71)">
                <i class="fas fa-check-circle icon"></i>
                <h2>{{ materiels_disponibles }}</h2>
                <p>Disponibles</p>
            </div>
        </div>
        <div class="col-md-2">
            <div class="stat-card" style="background:linear-gradient(135deg,#e67e22,#f39c12)">
                <i class="fas fa-hand-holding icon"></i>
                <h2>{{ materiels_empruntes }}</h2>
                <p>Empruntes</p>
            </div>
        </div>
        <div class="col-md-2">
            <div class="stat-card" style="background:linear-gradient(135deg,#e74c3c,#c0392b)">
                <i class="fas fa-wrench icon"></i>
                <h2>{{ materiels_maintenance }}</h2>
                <p>Maintenance</p>
            </div>
        </div>
        <div class="col-md-2">
            <div class="stat-card" style="background:linear-gradient(135deg,#8e44ad,#9b59b6)">
                <i class="fas fa-clock icon"></i>
                <h2>{{ demandes_en_attente }}</h2>
                <p>En attente</p>
            </div>
        </div>
        <div class="col-md-2">
            <div class="stat-card" style="background:linear-gradient(135deg,#16a085,#1abc9c)">
                <i class="fas fa-users icon"></i>
                <h2>{{ total_utilisateurs }}</h2>
                <p>Utilisateurs</p>
            </div>
        </div>
    </div>

    <!-- KPI ROW 2 -->
    <div class="row g-3 mb-4">
        <div class="col-md-3">
            <div class="card p-3 text-center">
                <div class="text-muted small">Taux utilisation</div>
                <div style="font-size:1.8rem;font-weight:700;color:#e67e22">{{ taux_utilisation }}%</div>
                <div class="progress mt-1" style="height:6px">
                    <div class="progress-bar bg-warning" style="width:{{ taux_utilisation }}%"></div>
                </div>
            </div>
        </div>
        <div class="col-md-3">
            <div class="card p-3 text-center">
                <div class="text-muted small">Duree moyenne emprunt</div>
                <div style="font-size:1.8rem;font-weight:700;color:#2c3e50">{{ duree_moyenne }} j</div>
            </div>
        </div>
        <div class="col-md-3">
            <div class="card p-3 text-center">
                <div class="text-muted small">Emprunts (30 jours)</div>
                <div style="font-size:1.8rem;font-weight:700;color:#27ae60">{{ total_emprunts_jour }}</div>
            </div>
        </div>
        <div class="col-md-3">
            <div class="card p-3 text-center">
                <div class="text-muted small">Retards actifs</div>
                <div style="font-size:1.8rem;font-weight:700;color:#e74c3c">{{ demandes_retard }}</div>
            </div>
        </div>
    </div>

    <!-- GRAPHIQUES ROW 1 -->
    <div class="row g-3 mb-4">
        <!-- Evolution 30 jours -->
        <div class="col-md-8">
            <div class="card p-3">
                <div class="section-title">Evolution des emprunts (30 derniers jours)</div>
                <canvas id="evolutionChart" height="100"></canvas>
            </div>
        </div>
        <!-- Donut statuts -->
        <div class="col-md-4">
            <div class="card p-3">
                <div class="section-title">Statut des demandes</div>
                <canvas id="statutChart"></canvas>
            </div>
        </div>
    </div>

    <!-- GRAPHIQUES ROW 2 -->
    <div class="row g-3 mb-4">
        <!-- Top materiels empruntes -->
        <div class="col-md-4">
            <div class="card p-3">
                <div class="section-title">Top 5 materiels empruntes</div>
                <canvas id="topMaterielChart"></canvas>
            </div>
        </div>
        <!-- Stats par filiere -->
        <div class="col-md-4">
            <div class="card p-3">
                <div class="section-title">Demandes par filiere</div>
                <canvas id="filiereChart"></canvas>
            </div>
        </div>
        <!-- Materiels par categorie -->
        <div class="col-md-4">
            <div class="card p-3">
                <div class="section-title">Materiels par categorie</div>
                <canvas id="categorieChart"></canvas>
            </div>
        </div>
    </div>

    <!-- GRAPHIQUES ROW 3 -->
    <div class="row g-3 mb-4">
        <!-- Utilisateurs les plus actifs -->
        <div class="col-md-6">
            <div class="card p-3">
                <div class="section-title">Top 5 utilisateurs actifs</div>
                <canvas id="topUsersChart" height="120"></canvas>
            </div>
        </div>
        <!-- Evolution mensuelle -->
        <div class="col-md-6">
            <div class="card p-3">
                <div class="section-title">Evolution mensuelle (12 mois)</div>
                <canvas id="mensuelChart" height="120"></canvas>
            </div>
        </div>
    </div>

    <!-- GRAPHIQUES ROW 4 - Pannes -->
    <div class="row g-3 mb-4">
        <div class="col-md-6">
            <div class="card p-3">
                <div class="section-title">Taux de panne par materiel</div>
                <canvas id="pannesChart" height="120"></canvas>
            </div>
        </div>
        <div class="col-md-6">
            <div class="card p-3">
                <div class="section-title">Demandes recentes</div>
                <div class="table-responsive" style="max-height:250px;overflow-y:auto">
                    <table class="table table-sm table-hover">
                        <thead class="table-dark"><tr><th>#</th><th>Etudiant</th><th>Statut</th><th>Action</th></tr></thead>
                        <tbody>
                            {% for d in demandes_recentes %}
                            <tr>
                                <td>#{{ d.id }}</td>
                                <td>{{ d.utilisateur.username }}</td>
                                <td><span class="badge {% if d.statut == 'en_attente' %}bg-warning{% elif d.statut == 'approuvee' %}bg-success{% elif d.statut == 'refusee' %}bg-danger{% elif d.statut == 'en_cours' %}bg-info{% else %}bg-secondary{% endif %}">{{ d.get_statut_display }}</span></td>
                                <td><a href="{% url 'valider_demande' d.id %}" class="btn btn-xs btn-sm btn-custom">Traiter</a></td>
                            </tr>
                            {% endfor %}
                        </tbody>
                    </table>
                </div>
            </div>
        </div>
    </div>

    <!-- LIENS RAPIDES -->
    <div class="card p-3 mb-4">
        <div class="section-title">Administration rapide</div>
        <div class="row g-2">
            <div class="col-md-2"><a href="{% url 'gestion_catalogue' %}" class="btn btn-custom w-100"><i class="fas fa-boxes"></i> Catalogue</a></div>
            <div class="col-md-2"><a href="{% url 'gestion_demandes' %}" class="btn btn-warning w-100"><i class="fas fa-clipboard-list"></i> Demandes</a></div>
            <div class="col-md-2"><a href="{% url 'gestion_maintenance' %}" class="btn btn-danger w-100"><i class="fas fa-tools"></i> Maintenance</a></div>
            <div class="col-md-2"><a href="{% url 'gestion_utilisateurs' %}" class="btn btn-info w-100"><i class="fas fa-users"></i> Utilisateurs</a></div>
            <div class="col-md-2"><a href="{% url 'export_excel' %}" class="btn btn-success w-100"><i class="fas fa-file-excel"></i> Excel</a></div>
            <div class="col-md-2"><a href="{% url 'carte_materiels' %}" class="btn btn-secondary w-100"><i class="fas fa-map"></i> Carte</a></div>
        </div>
    </div>
</div>

<script>
const COLORS = ['#2c3e50','#3498db','#27ae60','#e67e22','#e74c3c','#9b59b6','#1abc9c','#f39c12','#16a085','#d35400'];

// 1. Evolution 30 jours
new Chart(document.getElementById('evolutionChart'), {
    type: 'line',
    data: {
        labels: {{ jours_labels|safe }},
        datasets: [
            { label: 'Valides', data: {{ emprunts_valides_jour|safe }}, borderColor: '#2c3e50', backgroundColor: 'rgba(44,62,80,0.1)', fill: true, tension: 0.3, pointRadius: 3 },
            { label: 'En cours', data: {{ emprunts_encours_jour|safe }}, borderColor: '#e67e22', backgroundColor: 'rgba(230,126,34,0.05)', fill: false, tension: 0.3, pointRadius: 3 }
        ]
    },
    options: { responsive: true, plugins: { legend: { position: 'top' } }, scales: { y: { beginAtZero: true } } }
});

// 2. Donut statuts demandes
new Chart(document.getElementById('statutChart'), {
    type: 'doughnut',
    data: {
        labels: ['En attente','Approuvee','En cours','Restituee','Refusee','Retard'],
        datasets: [{ data: {{ statuts_data|safe }}, backgroundColor: ['#f39c12','#27ae60','#3498db','#95a5a6','#e74c3c','#c0392b'] }]
    },
    options: { responsive: true, plugins: { legend: { position: 'bottom', labels: { font: { size: 11 } } } } }
});

// 3. Top materiels empruntes
new Chart(document.getElementById('topMaterielChart'), {
    type: 'bar',
    data: {
        labels: {{ top_mat_labels|safe }},
        datasets: [{ label: 'Emprunts', data: {{ top_mat_data|safe }}, backgroundColor: COLORS }]
    },
    options: { indexAxis: 'y', responsive: true, plugins: { legend: { display: false } }, scales: { x: { beginAtZero: true } } }
});

// 4. Stats par filiere
new Chart(document.getElementById('filiereChart'), {
    type: 'pie',
    data: {
        labels: {{ filiere_labels|safe }},
        datasets: [{ data: {{ filiere_data|safe }}, backgroundColor: COLORS }]
    },
    options: { responsive: true, plugins: { legend: { position: 'bottom', labels: { font: { size: 11 } } } } }
});

// 5. Materiels par categorie
new Chart(document.getElementById('categorieChart'), {
    type: 'doughnut',
    data: {
        labels: {{ cat_labels|safe }},
        datasets: [{ data: {{ cat_data|safe }}, backgroundColor: COLORS }]
    },
    options: { responsive: true, plugins: { legend: { position: 'bottom', labels: { font: { size: 11 } } } } }
});

// 6. Top utilisateurs actifs
new Chart(document.getElementById('topUsersChart'), {
    type: 'bar',
    data: {
        labels: {{ top_users_labels|safe }},
        datasets: [{ label: 'Demandes', data: {{ top_users_data|safe }}, backgroundColor: '#3498db' }]
    },
    options: { responsive: true, plugins: { legend: { display: false } }, scales: { y: { beginAtZero: true } } }
});

// 7. Evolution mensuelle
new Chart(document.getElementById('mensuelChart'), {
    type: 'bar',
    data: {
        labels: {{ mois_labels|safe }},
        datasets: [{ label: 'Demandes', data: {{ mois_data|safe }}, backgroundColor: 'rgba(44,62,80,0.7)', borderColor: '#2c3e50', borderWidth: 1 }]
    },
    options: { responsive: true, plugins: { legend: { display: false } }, scales: { y: { beginAtZero: true } } }
});

// 8. Taux de panne
new Chart(document.getElementById('pannesChart'), {
    type: 'bar',
    data: {
        labels: {{ pannes_labels|safe }},
        datasets: [{ label: 'Pannes', data: {{ pannes_data|safe }}, backgroundColor: '#e74c3c' }]
    },
    options: { responsive: true, plugins: { legend: { display: false } }, scales: { y: { beginAtZero: true } } }
});
</script>
<script src="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/js/bootstrap.bundle.min.js"></script>
</body>
</html>""")
print('dashboard.html cree!')
