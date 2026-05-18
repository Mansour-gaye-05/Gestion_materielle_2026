with open('templates/carte_materiels.html', 'w', encoding='utf-8') as f:
    f.write("""<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <title>Carte des materiels empruntes</title>
    <link rel="stylesheet" href="https://unpkg.com/leaflet@1.9.4/dist/leaflet.css"/>
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css" rel="stylesheet">
    <link href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0/css/all.min.css" rel="stylesheet">
    <script src="https://unpkg.com/leaflet@1.9.4/dist/leaflet.js"></script>
    <style>
        body { background: #f0f2f5; }
        #map { height: 550px; width: 100%; border-radius: 12px; border: 1px solid #dee2e6; }
        .navbar-custom { background: #2c3e50; }
    </style>
</head>
<body>
<nav class="navbar navbar-dark navbar-custom px-3 py-2">
    <span class="navbar-brand fw-bold"><i class="fas fa-map-marker-alt"></i> Carte des materiels empruntes</span>
    <a href="{% url 'dashboard' %}" class="btn btn-outline-light btn-sm">
        <i class="fas fa-arrow-left"></i> Retour Dashboard
    </a>
</nav>

<div class="container-fluid p-4">
    <div class="row mb-3">
        <div class="col-12">
            <div class="card border-0 shadow-sm p-3">
                <strong><i class="fas fa-info-circle text-primary"></i> {{ emplacements|length }} materiel(s) en cours d'utilisation</strong>
            </div>
        </div>
    </div>

    <div class="row">
        <div class="col-md-8">
            <div class="card border-0 shadow-sm p-2">
                <div id="map"></div>
            </div>
        </div>
        <div class="col-md-4">
            <div class="card border-0 shadow-sm p-3">
                <h6 class="fw-bold mb-3"><i class="fas fa-list"></i> Details</h6>
                {% for e in emplacements %}
                <div class="border-bottom pb-2 mb-2">
                    <strong>{{ e.demande.utilisateur.username }}</strong><br>
                    <small class="text-muted">
                        {% for ligne in e.demande.lignes.all %}
                            <i class="fas fa-box"></i> {{ ligne.materiel.nom }}<br>
                        {% endfor %}
                        <i class="fas fa-map-marker-alt"></i> {{ e.adresse }}<br>
                        <i class="fas fa-calendar"></i> {{ e.demande.date_debut|date:"d/m/Y" }} au {{ e.demande.date_fin|date:"d/m/Y" }}
                    </small>
                </div>
                {% empty %}
                <p class="text-muted">Aucun materiel en cours.</p>
                {% endfor %}
            </div>
        </div>
    </div>
</div>

<script>
var map = L.map('map').setView([14.791, -16.935], 13);

L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
    attribution: '© OpenStreetMap',
    maxZoom: 19
}).addTo(map);

var points = [];

{% for e in emplacements %}
{% if e.latitude and e.longitude %}
var marker = L.marker([{{ e.latitude }}, {{ e.longitude }}]);
marker.bindPopup(
    '<b>{{ e.demande.utilisateur.username|escapejs }}</b><br>' +
    '{% for ligne in e.demande.lignes.all %}{{ ligne.materiel.nom|escapejs }}{% endfor %}<br>' +
    '{{ e.adresse|escapejs }}<br>' +
    '{{ e.demande.date_debut|date:"d/m/Y" }} au {{ e.demande.date_fin|date:"d/m/Y" }}'
).addTo(map);
points.push([{{ e.latitude }}, {{ e.longitude }}]);
{% endif %}
{% endfor %}

if (points.length === 1) {
    map.setView(points[0], 15);
} else if (points.length > 1) {
    map.fitBounds(points, {padding: [40, 40], maxZoom: 15});
}
</script>
<script src="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/js/bootstrap.bundle.min.js"></script>
</body>
</html>""")
print('carte_materiels.html reecrit!')
