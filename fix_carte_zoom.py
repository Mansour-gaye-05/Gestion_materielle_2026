with open('templates/carte_materiels.html', 'r', encoding='utf-8') as f:
    content = f.read()

old = """        // Ajuster la vue
        if (emplacements.length > 0) {
            var bounds = [];
            for (var i = 0; i < emplacements.length; i++) {
                bounds.push([emplacements[i].lat, emplacements[i].lng]);
            }
            map.fitBounds(bounds);
        }"""

new = """        // Ajuster la vue
        if (emplacements.length > 0) {
            var bounds = [];
            for (var i = 0; i < emplacements.length; i++) {
                bounds.push([emplacements[i].lat, emplacements[i].lng]);
            }
            if (emplacements.length === 1) {
                map.setView([emplacements[0].lat, emplacements[0].lng], 15);
            } else {
                map.fitBounds(bounds, {padding: [50, 50], maxZoom: 16});
            }
        }

        // Afficher coordonnees dans le panneau info
        var info = '<strong>Materiels en cours (' + emplacements.length + ')</strong><br>';
        for (var i = 0; i < emplacements.length; i++) {
            var e = emplacements[i];
            info += '<hr><b>' + e.materiel + '</b> — ' + e.etudiant + '<br>';
            info += '<small>📍 ' + e.adresse + ' (lat:' + e.lat.toFixed(4) + ', lng:' + e.lng.toFixed(4) + ')</small><br>';
            info += '<small>📅 Du ' + e.date_debut + ' au ' + e.date_fin + '</small><br>';
        }
        document.getElementById('info').innerHTML = info;"""

content = content.replace(old, new)

with open('templates/carte_materiels.html', 'w', encoding='utf-8') as f:
    f.write(content)
print('Carte mise a jour!')
