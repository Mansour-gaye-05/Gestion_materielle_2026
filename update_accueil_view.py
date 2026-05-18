with open('gestion/views.py', 'r', encoding='utf-8') as f:
    content = f.read()

old = """def accueil(request):
    return render(request, 'accueil.html')"""

new = """def accueil(request):
    context = {
        'total_materiels': Materiel.objects.count(),
        'materiels_disponibles': Materiel.objects.filter(etat='disponible').count(),
        'total_utilisateurs': Utilisateur.objects.count(),
        'total_demandes': Demande.objects.count(),
    }
    return render(request, 'accueil.html', context)"""

content = content.replace(old, new)
with open('gestion/views.py', 'w', encoding='utf-8') as f:
    f.write(content)
print('Vue accueil mise a jour!')
