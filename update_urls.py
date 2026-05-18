with open('Gestion_emprunt_materiels_SI/urls.py', 'r', encoding='utf-8') as f:
    content = f.read()
if 'journal_activite' not in content:
    content = content.replace(
        "path('export/excel/', views.export_statistiques_excel, name='export_excel'),",
        "path('journal/', views.journal_activite, name='journal_activite'),\n    path('export/excel/', views.export_statistiques_excel, name='export_excel'),"
    )
    with open('Gestion_emprunt_materiels_SI/urls.py', 'w', encoding='utf-8') as f:
        f.write(content)
    print('URL journal ajoutee!')
else:
    print('URL deja presente')
