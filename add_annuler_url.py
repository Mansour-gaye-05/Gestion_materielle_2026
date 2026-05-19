with open('Gestion_emprunt_materiels_SI/urls.py', 'r', encoding='utf-8') as f:
    content = f.read()

if 'annuler_demande' not in content:
    content = content.replace(
        "path('signaler-panne-emprunt/<int:demande_id>/', views.signaler_panne_emprunt, name='signaler_panne_emprunt'),",
        "path('signaler-panne-emprunt/<int:demande_id>/', views.signaler_panne_emprunt, name='signaler_panne_emprunt'),\n    path('annuler/<int:demande_id>/', views.annuler_demande, name='annuler_demande'),"
    )
    with open('Gestion_emprunt_materiels_SI/urls.py', 'w', encoding='utf-8') as f:
        f.write(content)
    print('URL annuler ajoutee!')
