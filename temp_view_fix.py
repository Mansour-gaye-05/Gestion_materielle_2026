@staff_member_required
def carte_materiels(request):
    # Ne montrer que les demandes EN COURS AVEC emplacement VALIDE
    emplacements = Emplacement.objects.select_related('demande__utilisateur').filter(
        demande__statut='en_cours',  # Uniquement les emprunts actifs
        latitude__isnull=False,
        longitude__isnull=False,
        latitude__gt=0,  # Éviter les coordonnées par défaut
        longitude__gt=0
    ).exclude(
        adresse__icontains='lieu par défaut'
    ).distinct()
    
    # Debug
    print(f"\n=== POINTS SUR LA CARTE ADMIN ===")
    print(f"Total: {emplacements.count()}")
    for e in emplacements:
        print(f"  • Demande #{e.demande.id} - {e.demande.utilisateur.username}")
        print(f"    Lieu: {e.adresse}")
        print(f"    Coord: ({e.latitude}, {e.longitude})")
    print("================================\n")
    
    return render(request, 'carte_materiels.html', {'emplacements': emplacements})
