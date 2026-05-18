with open('gestion/views.py', 'r', encoding='utf-8') as f:
    content = f.read()

old = """def carte_materiels(request):
    emplacements = Emplacement.objects.select_related('demande').filter(
        demande__statut='en_cours',
        latitude__isnull=False,
        longitude__isnull=False
    )
    print("=== CARTE ===")
    print("Count:", emplacements.count())
    for e in emplacements:
        print(f"  lat={e.latitude}, lng={e.longitude}, statut={e.demande.statut}")
    return render(request, 'carte_materiels.html', {'emplacements': emplacements})"""

new = """def carte_materiels(request):
    import json
    emplacements = Emplacement.objects.select_related('demande__utilisateur').filter(
        demande__statut='en_cours',
        latitude__isnull=False,
        longitude__isnull=False
    ).prefetch_related('demande__lignes__materiel')

    points = []
    for e in emplacements:
        materiels = ', '.join([l.materiel.nom for l in e.demande.lignes.all()])
        points.append({
            'lat': float(e.latitude),
            'lng': float(e.longitude),
            'etudiant': e.demande.utilisateur.username,
            'materiel': materiels,
            'adresse': e.adresse or '',
            'date_debut': e.demande.date_debut.strftime('%d/%m/%Y'),
            'date_fin': e.demande.date_fin.strftime('%d/%m/%Y'),
        })

    return render(request, 'carte_materiels.html', {
        'emplacements': emplacements,
        'points_json': json.dumps(points)
    })"""

import re
content = re.sub(
    r'def carte_materiels\(request\):.*?return render\(request, .carte_materiels\.html., \{.emplacements.: emplacements\}\)',
    new,
    content,
    flags=re.DOTALL
)

with open('gestion/views.py', 'w', encoding='utf-8') as f:
    f.write(content)
print('Vue carte mise a jour!')
