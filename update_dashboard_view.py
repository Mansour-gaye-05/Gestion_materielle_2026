with open('gestion/views.py', 'r', encoding='utf-8') as f:
    content = f.read()

new_dashboard = '''@staff_member_required
def dashboard(request):
    from django.db.models import Avg, F, ExpressionWrapper, DurationField
    aujourdhui = timezone.now().date()
    date_debut_30 = aujourdhui - timedelta(days=29)

    # Evolution 30 jours
    emprunts_par_jour = (
        Demande.objects
        .filter(statut__in=["approuvee", "en_cours"], date_validation__isnull=False,
                date_validation__date__gte=date_debut_30)
        .annotate(jour=TruncDate("date_validation"))
        .values("jour").annotate(total=Count("id")).order_by("jour")
    )
    encours_par_jour = (
        Demande.objects
        .filter(statut="en_cours", date_demande__date__gte=date_debut_30)
        .annotate(jour=TruncDate("date_demande"))
        .values("jour").annotate(total=Count("id")).order_by("jour")
    )
    jours_labels = []
    emprunts_valides_jour = []
    emprunts_encours_jour = []
    for i in range(29, -1, -1):
        date_jour = aujourdhui - timedelta(days=i)
        jours_labels.append(date_jour.strftime("%d/%m"))
        valide = next((e["total"] for e in emprunts_par_jour if e["jour"] == date_jour), 0)
        encours = next((e["total"] for e in encours_par_jour if e["jour"] == date_jour), 0)
        emprunts_valides_jour.append(valide)
        emprunts_encours_jour.append(encours)

    total_emprunts_jour = sum(emprunts_valides_jour)
    moyenne_emprunts = round(total_emprunts_jour / 30, 1) if total_emprunts_jour > 0 else 0
    pic_emprunts = max(emprunts_valides_jour) if emprunts_valides_jour else 0

    # Stats materiels
    total_materiels = Materiel.objects.count()
    materiels_disponibles = Materiel.objects.filter(etat="disponible").count()
    materiels_empruntes = Materiel.objects.filter(etat="emprunte").count()
    materiels_maintenance = Materiel.objects.filter(etat="maintenance").count()
    taux_utilisation = round((materiels_empruntes / total_materiels * 100), 1) if total_materiels > 0 else 0

    # Stats demandes
    demandes_encours = Demande.objects.filter(statut="en_cours").count()
    demandes_retard = Demande.objects.filter(statut="retard").count()
    demandes_en_attente = Demande.objects.filter(statut="en_attente").count()
    demandes_total = Demande.objects.count()
    demandes_approuvees = Demande.objects.filter(statut="approuvee").count()
    demandes_refusees = Demande.objects.filter(statut="refusee").count()

    # Stats utilisateurs
    total_utilisateurs = Utilisateur.objects.count()
    total_etudiants = Utilisateur.objects.filter(role="etudiant").count()
    total_categories = Categorie.objects.count()

    # Materiels par categorie (pour graphique donut)
    materiels_par_categorie = Categorie.objects.annotate(total=Count("materiels"))
    cat_labels = [c.libelle for c in materiels_par_categorie]
    cat_data = [c.total for c in materiels_par_categorie]

    # Top 5 materiels les plus empruntes
    top_materiels = (
        LigneDemande.objects
        .values("materiel__nom")
        .annotate(total=Count("id"))
        .order_by("-total")[:5]
    )
    top_mat_labels = [t["materiel__nom"] for t in top_materiels]
    top_mat_data = [t["total"] for t in top_materiels]

    # Taux de panne par materiel (top 5)
    top_pannes = (
        Maintenance.objects
        .values("materiel__nom")
        .annotate(total=Count("id"))
        .order_by("-total")[:5]
    )
    pannes_labels = [p["materiel__nom"] for p in top_pannes]
    pannes_data = [p["total"] for p in top_pannes]

    # Utilisateurs les plus actifs (top 5)
    top_users = (
        Demande.objects
        .values("utilisateur__username", "utilisateur__filiere")
        .annotate(total=Count("id"))
        .order_by("-total")[:5]
    )
    top_users_labels = [u["utilisateur__username"] for u in top_users]
    top_users_data = [u["total"] for u in top_users]

    # Stats par filiere
    stats_filiere = (
        Demande.objects
        .values("utilisateur__filiere")
        .annotate(total=Count("id"))
        .order_by("-total")
    )
    filiere_labels = [f["utilisateur__filiere"] or "Non definie" for f in stats_filiere]
    filiere_data = [f["total"] for f in stats_filiere]

    # Evolution mensuelle (12 derniers mois)
    from django.db.models.functions import TruncMonth
    evolution_mensuelle = (
        Demande.objects
        .filter(date_demande__gte=timezone.now() - timedelta(days=365))
        .annotate(mois=TruncMonth("date_demande"))
        .values("mois")
        .annotate(total=Count("id"))
        .order_by("mois")
    )
    mois_labels = [e["mois"].strftime("%b %Y") for e in evolution_mensuelle]
    mois_data = [e["total"] for e in evolution_mensuelle]

    # Duree moyenne emprunt (en jours)
    demandes_terminees = Demande.objects.filter(statut__in=["restituee", "en_cours"])
    duree_totale = 0
    duree_count = 0
    for d in demandes_terminees:
        if d.date_debut and d.date_fin:
            duree = (d.date_fin - d.date_debut).days
            if duree >= 0:
                duree_totale += duree
                duree_count += 1
    duree_moyenne = round(duree_totale / duree_count, 1) if duree_count > 0 else 0

    # Statut des demandes (pour donut)
    statuts_data = [
        demandes_en_attente,
        demandes_approuvees,
        demandes_encours,
        Demande.objects.filter(statut="restituee").count(),
        demandes_refusees,
        demandes_retard,
    ]

    derniers_materiels = Materiel.objects.all().order_by("-id")[:10]
    demandes_recentes = Demande.objects.all().order_by("-date_demande")[:10]
    maintenances_cours = Maintenance.objects.filter(statut__in=["signale", "en_cours"]).count()

    import json
    context = {
        "total_materiels": total_materiels,
        "materiels_disponibles": materiels_disponibles,
        "materiels_empruntes": materiels_empruntes,
        "materiels_maintenance": materiels_maintenance,
        "taux_utilisation": taux_utilisation,
        "demandes_encours": demandes_encours,
        "demandes_retard": demandes_retard,
        "demandes_en_attente": demandes_en_attente,
        "demandes_total": demandes_total,
        "demandes_approuvees": demandes_approuvees,
        "demandes_refusees": demandes_refusees,
        "total_utilisateurs": total_utilisateurs,
        "total_etudiants": total_etudiants,
        "total_categories": total_categories,
        "materiels_par_categorie": materiels_par_categorie,
        "derniers_materiels": derniers_materiels,
        "demandes_recentes": demandes_recentes,
        "maintenances_cours": maintenances_cours,
        "jours_labels": json.dumps(jours_labels),
        "emprunts_valides_jour": json.dumps(emprunts_valides_jour),
        "emprunts_encours_jour": json.dumps(emprunts_encours_jour),
        "total_emprunts_jour": total_emprunts_jour,
        "moyenne_emprunts": moyenne_emprunts,
        "pic_emprunts": pic_emprunts,
        "duree_moyenne": duree_moyenne,
        "cat_labels": json.dumps(cat_labels),
        "cat_data": json.dumps(cat_data),
        "top_mat_labels": json.dumps(top_mat_labels),
        "top_mat_data": json.dumps(top_mat_data),
        "pannes_labels": json.dumps(pannes_labels),
        "pannes_data": json.dumps(pannes_data),
        "top_users_labels": json.dumps(top_users_labels),
        "top_users_data": json.dumps(top_users_data),
        "filiere_labels": json.dumps(filiere_labels),
        "filiere_data": json.dumps(filiere_data),
        "mois_labels": json.dumps(mois_labels),
        "mois_data": json.dumps(mois_data),
        "statuts_data": json.dumps(statuts_data),
    }
    return render(request, "dashboard.html", context)
'''

# Remplacer l'ancienne vue dashboard
import re
content = re.sub(
    r'@staff_member_required\ndef dashboard\(request\):.*?(?=\n# ==================== GESTION DES DEMANDES)',
    new_dashboard + '\n',
    content,
    flags=re.DOTALL
)

with open('gestion/views.py', 'w', encoding='utf-8') as f:
    f.write(content)
print('Vue dashboard mise a jour!')
