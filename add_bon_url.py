with open('Gestion_emprunt_materiels_SI/urls.py', 'r', encoding='utf-8') as f:
    content = f.read()

if 'bon_sortie_pdf' not in content:
    content = content.replace(
        "path('rendre/<int:demande_id>/', views.rendre_materiel, name='rendre_materiel'),",
        "path('rendre/<int:demande_id>/', views.rendre_materiel, name='rendre_materiel'),\n    path('bon-sortie/<int:demande_id>/', views.bon_sortie_pdf, name='bon_sortie_pdf'),"
    )
    with open('Gestion_emprunt_materiels_SI/urls.py', 'w', encoding='utf-8') as f:
        f.write(content)
    print('URL bon de sortie ajoutee!')
