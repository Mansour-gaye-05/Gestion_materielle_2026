with open('Gestion_emprunt_materiels_SI/urls.py', 'r', encoding='utf-8') as f:
    content = f.read()

if 'changer_mot_de_passe' not in content:
    content = content.replace(
        "path('profil/', views.profil_etudiant, name='profil_etudiant'),",
        "path('profil/', views.profil_etudiant, name='profil_etudiant'),\n    path('profil/mdp/', views.changer_mot_de_passe, name='changer_mot_de_passe'),"
    )
    with open('Gestion_emprunt_materiels_SI/urls.py', 'w', encoding='utf-8') as f:
        f.write(content)
    print('URL ajoutee!')
