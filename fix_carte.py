with open('templates/carte_materiels.html', 'r', encoding='utf-8') as f:
    content = f.read()

content = content.replace(
    '<link rel="stylesheet" href="https://unpkg.com/leaflet@1.9.4/dist/leaflet.css" />',
    '<link rel="stylesheet" href="https://unpkg.com/leaflet@1.9.4/dist/leaflet.css" />\n    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css" rel="stylesheet">\n    <link href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0/css/all.min.css" rel="stylesheet">'
)

content = content.replace(
    '<div class="container">',
    '<div class="container">\n        <div class="d-flex justify-content-between align-items-center mb-3">\n            <h2 class="mb-0"><i class="fas fa-map-marker-alt"></i> Carte des materiels empruntes</h2>\n            <a href="{% url \'dashboard\' %}" class="btn btn-sm" style="background:#2c3e50;color:white;border-radius:20px"><i class="fas fa-arrow-left"></i> Retour Dashboard</a>\n        </div>'
)

content = content.replace('<h2>ðŸ—ºï¸ Carte des matÃ©riels empruntÃ©s</h2>', '')

with open('templates/carte_materiels.html', 'w', encoding='utf-8') as f:
    f.write(content)
print('Bouton retour ajoute!')
