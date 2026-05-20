from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.admin.views.decorators import staff_member_required
from django.contrib.auth.decorators import login_required
from django.contrib.auth import login, logout, authenticate
from django.contrib import messages
from django.db.models import Count, Sum, Q
from django.db.models.functions import TruncDate
from django.utils import timezone
from django.http import HttpResponse, JsonResponse
from datetime import timedelta
from .models import Utilisateur, Categorie, Materiel, Demande, LigneDemande, Maintenance, Restitution, Emplacement, Notification, ConversationChat
import pandas as pd
from io import BytesIO
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
import re
import json


def log_action(request_or_user, action, description, demande=None, materiel=None):
    from .models import JournalActivite
    if hasattr(request_or_user, 'user'):
        user = request_or_user.user if request_or_user.user.is_authenticated else None
        ip = request_or_user.META.get('REMOTE_ADDR')
    else:
        user = request_or_user
        ip = None
    JournalActivite.objects.create(
        utilisateur=user,
        action=action,
        description=description,
        ip_address=ip,
        demande=demande,
        materiel=materiel
    )

# ==================== PAGE D'ACCUEIL ====================

def accueil(request):
    return render(request, 'index.html')


# ==================== PAGE D'ACCUEIL / CATALOGUE ====================

def catalogue(request):
    materiels = Materiel.objects.all()
    categories = Categorie.objects.all()

    cat_id = request.GET.get('categorie')
    if cat_id:
        materiels = materiels.filter(categorie_id=cat_id)
        categorie_selected = cat_id
    else:
        categorie_selected = None

    recherche = request.GET.get('recherche')
    if recherche:
        materiels = materiels.filter(nom__icontains=recherche)

    etat = request.GET.get('etat')
    if etat:
        materiels = materiels.filter(etat=etat)
        etat_selected = etat
    else:
        etat_selected = None

    context = {
        'materiels': materiels,
        'categories': categories,
        'categorie_selected': categorie_selected,
        'recherche': recherche,
        'etat_selected': etat_selected,
    }
    return render(request, 'catalogue.html', context)

@login_required
def ajouter_demande(request, materiel_id):
    materiel = get_object_or_404(Materiel, id=materiel_id)

    if request.method == 'POST' and materiel.etat == 'disponible':
        demande = Demande.objects.create(
            utilisateur=request.user,
            date_demande=timezone.now(),
            date_debut=timezone.now().date(),
            date_fin=timezone.now().date() + timedelta(days=7),
            statut='en_attente',
            motif=f"Demande pour {materiel.nom}"
        )

        LigneDemande.objects.create(
            demande=demande,
            materiel=materiel,
            quantite=1
        )

        messages.success(request, f'✅ Demande pour "{materiel.nom}" envoyée avec succès !')
    else:
        messages.error(request, f'❌ "{materiel.nom}" n\'est pas disponible')

    return redirect('catalogue')


# ==================== DASHBOARD ADMINISTRATEUR ====================

@staff_member_required
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


# ==================== GESTION DES DEMANDES ====================

@staff_member_required
def gestion_demandes(request):
    demandes = Demande.objects.all().order_by('-date_demande')
    return render(request, 'gestion_demandes.html', {'demandes': demandes})


@staff_member_required
def valider_demande(request, demande_id):
    demande = get_object_or_404(Demande, id=demande_id)

    if request.method == 'POST':
        action = request.POST.get('action')
        motif = request.POST.get('motif', '')

        if action == 'approuver':
            demande.statut = 'approuvee'
            demande.valide_par = request.user
            demande.date_validation = timezone.now()
            for ligne in demande.lignes.all():
                ligne.materiel.etat = 'emprunte'
                ligne.materiel.save()

            # ✅ Ne créer un emplacement que si l'étudiant en a fourni un
            # et qu'il n'existe pas déjà
            if not Emplacement.objects.filter(demande=demande).exists():
                lat = request.POST.get('latitude')
                lng = request.POST.get('longitude')
                adr = request.POST.get('adresse', '')
                if lat and lng:
                    Emplacement.objects.create(
                        demande=demande,
                        adresse=adr,
                        latitude=float(lat),
                        longitude=float(lng)
                    )

            log_action(request, 'demande_approuvee',
                       f'Admin {request.user.username} a approuve la demande #{demande.id}',
                       demande=demande)
            messages.success(request, f'Demande #{demande.id} approuvee')

        elif action == 'refuser':
            demande.statut = 'refusee'
            demande.motif_refus = motif
            log_action(request, 'demande_refusee',
                       f'Admin {request.user.username} a refuse la demande #{demande.id}. Motif: {motif}',
                       demande=demande)
            messages.warning(request, f'Demande #{demande.id} refusee')

        demande.save()
        return redirect('gestion_demandes')

    return render(request, 'valider_demande.html', {'demande': demande})
# ==================== GESTION DE LA MAINTENANCE ====================

@staff_member_required
def gestion_maintenance(request):
    maintenances = Maintenance.objects.all().order_by('-date_signalement')
    materiels = Materiel.objects.filter(etat__in=['disponible', 'emprunte'])
    return render(request, 'gestion_maintenance.html', {'maintenances': maintenances, 'materiels': materiels})


@staff_member_required
def ajouter_maintenance(request):
    if request.method == 'POST':
        materiel_id = request.POST.get('materiel')
        type_maintenance = request.POST.get('type')
        description = request.POST.get('description')

        materiel = get_object_or_404(Materiel, id=materiel_id)
        materiel.etat = 'maintenance'
        materiel.save()

        Maintenance.objects.create(
            materiel=materiel,
            type=type_maintenance,
            description=description,
            statut='signale'
        )

        messages.success(request, f'Maintenance signalée pour {materiel.nom}')
        return redirect('gestion_maintenance')

    return redirect('gestion_maintenance')


@staff_member_required
def resoudre_maintenance(request, maintenance_id):
    maintenance = get_object_or_404(Maintenance, id=maintenance_id)

    if request.method == 'POST':
        maintenance.statut = 'resolu'
        maintenance.date_resolution = timezone.now()
        maintenance.save()
        maintenance.materiel.etat = 'disponible'
        maintenance.materiel.save()
        log_action(request, 'maintenance_resolue', f"{request.user.username} a resolu la maintenance de '{maintenance.materiel.nom}'", materiel=maintenance.materiel)

        messages.success(request, f'Maintenance resolue pour {maintenance.materiel.nom}')

    return redirect('gestion_maintenance')


# ==================== GESTION DU CATALOGUE (CRUD) ====================

@staff_member_required
def gestion_catalogue(request):
    materiels = Materiel.objects.all().order_by('-id')
    categories = Categorie.objects.all()
    return render(request, 'gestion_catalogue.html', {'materiels': materiels, 'categories': categories})


@staff_member_required
def ajouter_materiel(request):
    if request.method == 'POST':
        nom = request.POST.get('nom')
        categorie_id = request.POST.get('categorie')
        numero_serie = request.POST.get('numero_serie')
        description = request.POST.get('description')
        etat = request.POST.get('etat')

        categorie = get_object_or_404(Categorie, id=categorie_id) if categorie_id else None

        Materiel.objects.create(
            nom=nom,
            categorie=categorie,
            numero_serie=numero_serie,
            description=description,
            etat=etat
        )
        log_action(request, 'materiel_ajoute', f"{request.user.username} a ajoute le materiel '{nom}'", materiel=materiel_obj)

        messages.success(request, f'Matériel "{nom}" ajouté avec succès')
        return redirect('gestion_catalogue')

    return redirect('gestion_catalogue')


@staff_member_required
def modifier_materiel(request, materiel_id):
    materiel = get_object_or_404(Materiel, id=materiel_id)

    if request.method == 'POST':
        materiel.nom = request.POST.get('nom')
        categorie_id = request.POST.get('categorie')
        materiel.categorie = get_object_or_404(Categorie, id=categorie_id) if categorie_id else None
        materiel.numero_serie = request.POST.get('numero_serie')
        materiel.description = request.POST.get('description')
        materiel.etat = request.POST.get('etat')
        materiel.save()
        log_action(request, 'materiel_modifie', f"{request.user.username} a modifié le matériel '{materiel.nom}'", materiel=materiel)

        messages.success(request, f'Matériel "{materiel.nom}" modifié')
        return redirect('gestion_catalogue')

    return redirect('gestion_catalogue')


@staff_member_required
def supprimer_materiel(request, materiel_id):
    materiel = get_object_or_404(Materiel, id=materiel_id)

    if request.method == 'POST':
        nom = materiel.nom
        materiel.delete()
        log_action(request, 'materiel_supprime', f"{request.user.username} a supprimé le matériel '{nom}' (ID: {materiel_id})")
        messages.success(request, f'Matériel "{nom}" supprimé')

    return redirect('gestion_catalogue')


# ==================== GESTION DES UTILISATEURS ====================

@staff_member_required
def gestion_utilisateurs(request):
    utilisateurs = Utilisateur.objects.all()
    return render(request, 'gestion_utilisateurs.html', {'utilisateurs': utilisateurs})


@staff_member_required
def modifier_role(request, user_id):
    utilisateur = get_object_or_404(Utilisateur, id=user_id)

    if request.method == 'POST':
        nouveau_role = request.POST.get('role')
        utilisateur.role = nouveau_role
        utilisateur.save()
        log_action(request, 'role_modifie', f"{request.user.username} a changé le rôle de {utilisateur.username} en '{nouveau_role}'")
        messages.success(request, f'Rôle de {utilisateur.username} modifié en {nouveau_role}')

    return redirect('gestion_utilisateurs')


# ==================== EXPORT PDF/EXCEL ====================

@staff_member_required
def export_statistiques_excel(request):
    output = BytesIO()
    with pd.ExcelWriter(output, engine='openpyxl') as writer:

        # Feuille 1 : Statistiques generales
        stats_data = {
            'Indicateur': [
                'Total materiels', 'Materiels disponibles', 'Materiels empruntes',
                'Materiels en maintenance', 'Total categories', 'Total utilisateurs',
                'Demandes total', 'Demandes en attente', 'Demandes en cours',
                'Demandes restituees', 'Demandes refusees', 'Demandes en retard'
            ],
            'Valeur': [
                Materiel.objects.count(),
                Materiel.objects.filter(etat='disponible').count(),
                Materiel.objects.filter(etat='emprunte').count(),
                Materiel.objects.filter(etat='maintenance').count(),
                Categorie.objects.count(),
                Utilisateur.objects.count(),
                Demande.objects.count(),
                Demande.objects.filter(statut='en_attente').count(),
                Demande.objects.filter(statut='en_cours').count(),
                Demande.objects.filter(statut='restituee').count(),
                Demande.objects.filter(statut='refusee').count(),
                Demande.objects.filter(statut='retard').count(),
            ]
        }
        pd.DataFrame(stats_data).to_excel(writer, sheet_name='Statistiques', index=False)

        # Feuille 2 : Liste complete des materiels
        materiels_data = []
        for m in Materiel.objects.select_related('categorie').all():
            materiels_data.append({
                'Nom': m.nom,
                'Categorie': m.categorie.libelle if m.categorie else '-',
                'Numero serie': m.numero_serie or '-',
                'Etat': m.get_etat_display(),
                'Quantite totale': m.quantite_totale,
                'Quantite disponible': m.quantite_disponible,
                'Description': m.description or '-',
                'Date acquisition': m.date_acquisition or '-',
            })
        pd.DataFrame(materiels_data).to_excel(writer, sheet_name='Materiels', index=False)

        # Feuille 3 : Liste des demandes
        demandes_data = []
        for d in Demande.objects.select_related('utilisateur', 'valide_par').prefetch_related('lignes__materiel').all():
            materiels_noms = ', '.join([l.materiel.nom for l in d.lignes.all()])
            demandes_data.append({
                'ID': d.id,
                'Etudiant': d.utilisateur.username,
                'Filiere': d.utilisateur.filiere or '-',
                'Materiel(s)': materiels_noms,
                'Date demande': d.date_demande.strftime('%d/%m/%Y %H:%M'),
                'Date debut': d.date_debut,
                'Date fin': d.date_fin,
                'Statut': d.get_statut_display(),
                'Valide par': d.valide_par.username if d.valide_par else '-',
                'Motif refus': d.motif_refus or '-',
            })
        pd.DataFrame(demandes_data).to_excel(writer, sheet_name='Demandes', index=False)

        # Feuille 4 : Maintenances
        maintenances_data = []
        for m in Maintenance.objects.select_related('materiel').all():
            maintenances_data.append({
                'Materiel': m.materiel.nom,
                'Type': m.get_type_display(),
                'Statut': m.get_statut_display(),
                'Date signalement': m.date_signalement.strftime('%d/%m/%Y %H:%M'),
                'Date resolution': m.date_resolution.strftime('%d/%m/%Y %H:%M') if m.date_resolution else '-',
                'Description': m.description or '-',
            })
        pd.DataFrame(maintenances_data).to_excel(writer, sheet_name='Maintenances', index=False)

        # Feuille 5 : Utilisateurs
        users_data = []
        for u in Utilisateur.objects.all():
            users_data.append({
                'Username': u.username,
                'Email': u.email,
                'Role': u.get_role_display(),
                'Filiere': u.filiere or '-',
                'Niveau': u.niveau or '-',
                'Telephone': u.telephone or '-',
                'Nombre demandes': u.demandes.count(),
            })
        pd.DataFrame(users_data).to_excel(writer, sheet_name='Utilisateurs', index=False)

    output.seek(0)
    response = HttpResponse(output, content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
    response['Content-Disposition'] = f'attachment; filename=rapport_complet_{timezone.now().strftime("%Y%m%d_%H%M")}.xlsx'
    return response


@staff_member_required
def export_rapport_pdf(request):
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename=rapport_{timezone.now().strftime("%Y%m%d_%H%M")}.pdf'

    p = canvas.Canvas(response, pagesize=A4)
    width, height = A4

    def draw_header(p, title):
        p.setFillColorRGB(0.17, 0.24, 0.31)
        p.rect(0, height - 80, width, 80, fill=1, stroke=0)
        p.setFillColorRGB(1, 1, 1)
        p.setFont("Helvetica-Bold", 16)
        p.drawString(40, height - 35, "UFR Sciences de l'Ingenieur - Universite de Thies")
        p.setFont("Helvetica", 11)
        p.drawString(40, height - 55, title)
        p.setFont("Helvetica", 9)
        p.drawString(40, height - 72, f"Genere le: {timezone.now().strftime('%d/%m/%Y a %H:%M')}")
        p.setFillColorRGB(0, 0, 0)

    def draw_section(p, y, title):
        p.setFillColorRGB(0.17, 0.24, 0.31)
        p.rect(40, y - 5, width - 80, 20, fill=1, stroke=0)
        p.setFillColorRGB(1, 1, 1)
        p.setFont("Helvetica-Bold", 11)
        p.drawString(45, y + 2, title)
        p.setFillColorRGB(0, 0, 0)
        return y - 25

    def check_page(p, y, height):
        if y < 80:
            p.showPage()
            draw_header(p, "Rapport complet (suite)")
            return height - 100
        return y

    # PAGE 1 - STATISTIQUES
    draw_header(p, "Rapport Complet - Gestion des Emprunts de Materiels")
    y = height - 100

    y = draw_section(p, y, "STATISTIQUES GENERALES")
    p.setFont("Helvetica", 10)

    stats = [
        ("Total materiels", Materiel.objects.count()),
        ("Materiels disponibles", Materiel.objects.filter(etat="disponible").count()),
        ("Materiels empruntes", Materiel.objects.filter(etat="emprunte").count()),
        ("Materiels en maintenance", Materiel.objects.filter(etat="maintenance").count()),
        ("Total categories", Categorie.objects.count()),
        ("Total utilisateurs", Utilisateur.objects.count()),
        ("Total demandes", Demande.objects.count()),
        ("Demandes en attente", Demande.objects.filter(statut="en_attente").count()),
        ("Demandes en cours", Demande.objects.filter(statut="en_cours").count()),
        ("Demandes restituees", Demande.objects.filter(statut="restituee").count()),
        ("Demandes refusees", Demande.objects.filter(statut="refusee").count()),
        ("Maintenances en cours", Maintenance.objects.filter(statut__in=["signale","en_cours"]).count()),
    ]

    for i, (label, val) in enumerate(stats):
        if i % 2 == 0:
            p.setFillColorRGB(0.96, 0.96, 0.96)
            p.rect(40, y - 4, width - 80, 16, fill=1, stroke=0)
        p.setFillColorRGB(0, 0, 0)
        p.drawString(50, y, label)
        p.setFont("Helvetica-Bold", 10)
        p.drawString(350, y, str(val))
        p.setFont("Helvetica", 10)
        y -= 18
        y = check_page(p, y, height)

    # LISTE DES MATERIELS
    y -= 10
    y = check_page(p, y, height)
    y = draw_section(p, y, "LISTE DES MATERIELS")

    p.setFont("Helvetica-Bold", 9)
    p.drawString(45, y, "Nom")
    p.drawString(200, y, "Categorie")
    p.drawString(320, y, "Etat")
    p.drawString(400, y, "Qte Dispo/Total")
    y -= 15

    p.setFont("Helvetica", 9)
    for i, m in enumerate(Materiel.objects.select_related("categorie").all()):
        if i % 2 == 0:
            p.setFillColorRGB(0.96, 0.96, 0.96)
            p.rect(40, y - 4, width - 80, 14, fill=1, stroke=0)
        p.setFillColorRGB(0, 0, 0)
        p.drawString(45, y, m.nom[:30])
        p.drawString(200, y, (m.categorie.libelle if m.categorie else "-")[:20])
        p.drawString(320, y, m.get_etat_display())
        p.drawString(400, y, f"{m.quantite_disponible}/{m.quantite_totale}")
        y -= 15
        y = check_page(p, y, height)

    # LISTE DES DEMANDES RECENTES
    y -= 10
    y = check_page(p, y, height)
    y = draw_section(p, y, "DEMANDES RECENTES (30 dernieres)")

    p.setFont("Helvetica-Bold", 9)
    p.drawString(45, y, "ID")
    p.drawString(75, y, "Etudiant")
    p.drawString(200, y, "Materiel")
    p.drawString(340, y, "Periode")
    p.drawString(450, y, "Statut")
    y -= 15

    p.setFont("Helvetica", 9)
    for i, d in enumerate(Demande.objects.select_related("utilisateur").prefetch_related("lignes__materiel").order_by("-date_demande")[:30]):
        if i % 2 == 0:
            p.setFillColorRGB(0.96, 0.96, 0.96)
            p.rect(40, y - 4, width - 80, 14, fill=1, stroke=0)
        p.setFillColorRGB(0, 0, 0)
        mat = ", ".join([l.materiel.nom[:15] for l in d.lignes.all()])
        p.drawString(45, y, f"#{d.id}")
        p.drawString(75, y, d.utilisateur.username[:18])
        p.drawString(200, y, mat[:20])
        p.drawString(340, y, f"{d.date_debut.strftime('%d/%m')} - {d.date_fin.strftime('%d/%m/%Y')}")
        p.drawString(450, y, d.get_statut_display())
        y -= 15
        y = check_page(p, y, height)

    p.save()
    return response


# ==================== CARTOGRAPHIE ====================

@staff_member_required
def carte_materiels(request):
    emplacements = Emplacement.objects.select_related('demande').filter(
        demande__statut='en_cours',
        latitude__isnull=False,
        longitude__isnull=False
    )
    print("=== CARTE ===")
    print("Count:", emplacements.count())
    for e in emplacements:
        print(f"  lat={e.latitude}, lng={e.longitude}, statut={e.demande.statut}")
    return render(request, 'carte_materiels.html', {'emplacements': emplacements})

# ==================== AUTHENTIFICATION ====================

def connexion(request):
    """Connexion pour les étudiants"""
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)
        if user:
            login(request, user)
            log_action(request, 'connexion', f"{user.username} s'est connecte depuis {request.META.get('REMOTE_ADDR', 'IP inconnue')}")
            if user.role == 'admin' or user.is_superuser:
                return redirect('dashboard')
            else:
                return redirect('espace_etudiant')
        else:
            messages.error(request, 'Identifiants incorrects')
    return render(request, 'connexion.html')


def connexion_admin(request):
    """Connexion pour les administrateurs"""
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)
        if user:
            if user.role == 'admin' or user.is_superuser:
                login(request, user)
                return redirect('dashboard')
            else:
                messages.error(request, 'Vous n\'avez pas les droits administrateur')
        else:
            messages.error(request, 'Identifiants incorrects')
    return render(request, 'connexion_admin.html')


def deconnexion(request):
    logout(request)
    log_action(request, 'deconnexion', f"{request.user.username} s'est deconnecte")
    messages.info(request, 'Vous êtes déconnecteé')
    return redirect('accueil')


# ==================== ESPACE ÉTUDIANT ====================

def inscription(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        email = request.POST.get('email')
        password = request.POST.get('password')
        password2 = request.POST.get('password2')
        filiere = request.POST.get('filiere')
        niveau = request.POST.get('niveau')
        telephone = request.POST.get('telephone')

        # Validation email universitaire (format: prenom.nom3@univ-thies.sn)
        if not re.match(r'^[a-z]+\.[a-z]+[0-9]@univ-thies\.sn$', email):
            messages.error(request,
                           'Format d\'email invalide. Utilisez: prenom.nom3@univ-thies.sn (ex: astou.gueye3@univ-thies.sn)')
            return render(request, 'inscription.html')
        if password == password2:
            if not Utilisateur.objects.filter(username=username).exists():
                utilisateur = Utilisateur.objects.create_user(
                    username=username,
                    email=email,
                    password=password,
                    role='etudiant',
                    filiere=filiere,
                    niveau=niveau,
                    telephone=telephone
                )
                login(request, utilisateur)
                log_action(request, 'inscription', f"Nouveau compte cree : {username} ({filiere} - {niveau})")
                messages.success(request, f'Bienvenue {username} ! Votre compte est créé.')
                return redirect('espace_etudiant')
            else:
                messages.error(request, 'Ce nom d\'utilisateur existe déjà')
        else:
            messages.error(request, 'Les mots de passe ne correspondent pas')

    return render(request, 'inscription.html')


@login_required
def espace_etudiant(request):
    demandes = Demande.objects.filter(utilisateur=request.user).order_by('-date_demande')

    # Statistiques
    stats = {
        'total': demandes.count(),
        'en_attente': demandes.filter(statut='en_attente').count(),
        'approuvees': demandes.filter(statut='approuvee').count(),
        'en_cours': demandes.filter(statut='en_cours').count(),
        'restituees': demandes.filter(statut='restituee').count(),
        'refusees': demandes.filter(statut='refusee').count(),
        'retard': demandes.filter(statut='retard').count(),
    }

    # Dernières demandes (5 dernières)
    dernieres_demandes = demandes[:5]

    # Emprunts actifs (en cours)
    emprunts_actifs = demandes.filter(statut='en_cours')

    # Notifications
    notifications = Notification.objects.filter(
        demande__utilisateur=request.user
    ).order_by('-date')[:10]

    context = {
        'utilisateur': request.user,
        'stats': stats,
        'demandes': dernieres_demandes,
        'emprunts_actifs': emprunts_actifs,
        'notifications': notifications,
        'today': timezone.now().date(),
    }
    return render(request, 'espace_etudiant.html', context)

@login_required
def nouvelle_demande(request):
    from datetime import date as date_type
    from .models import Reservation
    materiels = Materiel.objects.filter(etat='disponible')
    materiel_preselectionne = None
    materiel_id_get = request.GET.get('materiel_id')
    if materiel_id_get:
        materiel_preselectionne = Materiel.objects.filter(id=materiel_id_get).first()

    if request.method == 'POST':
        materiel_id = request.POST.get('materiel')
        date_debut_str = request.POST.get('date_debut')
        date_fin_str = request.POST.get('date_fin')
        adresse = request.POST.get('adresse')
        latitude = request.POST.get('latitude')
        longitude = request.POST.get('longitude')

        from datetime import datetime
        date_debut = datetime.strptime(date_debut_str, '%Y-%m-%d').date()
        date_fin = datetime.strptime(date_fin_str, '%Y-%m-%d').date()
        aujourd_hui = date_type.today()

        # Validation des dates
        if date_debut < aujourd_hui:
            messages.error(request, '❌ La date de début ne peut pas être dans le passé.')
            return render(request, 'nouvelle_demande.html', {'materiels': materiels, 'materiel_preselectionne': materiel_preselectionne})

        if date_fin <= date_debut:
            messages.error(request, '❌ La date de fin doit être après la date de début.')
            return render(request, 'nouvelle_demande.html', {'materiels': materiels, 'materiel_preselectionne': materiel_preselectionne})

        materiel = get_object_or_404(Materiel, id=materiel_id)

        # Vérification du stock
        if materiel.quantite_disponible < 1:
            messages.error(request, f'❌ "{materiel.nom}" n\'est plus disponible.')
            return render(request, 'nouvelle_demande.html', {'materiels': materiels, 'materiel_preselectionne': materiel_preselectionne})

        # Vérification des conflits de réservation
        conflit, qte_reservee = Reservation.verifier_conflit(materiel_id, date_debut, date_fin)
        if conflit:
            messages.error(request, f'❌ "{materiel.nom}" est déjà réservé sur cette période (quantité réservée: {qte_reservee}/{materiel.quantite_totale}). Choisissez d\'autres dates.')
            return render(request, 'nouvelle_demande.html', {'materiels': materiels, 'materiel_preselectionne': materiel_preselectionne})

        # Création de la demande
        demande = Demande.objects.create(
            utilisateur=request.user,
            date_debut=date_debut,
            date_fin=date_fin,
            statut='en_attente',
            motif=f"Demande pour {materiel.nom}"
        )

        LigneDemande.objects.create(demande=demande, materiel=materiel, quantite=1)

        # Création de la réservation
        Reservation.objects.create(
            materiel=materiel,
            utilisateur=request.user,
            demande=demande,
            date_debut=date_debut,
            date_fin=date_fin,
            quantite=1,
            statut='active'
        )
        log_action(request, 'demande_creee', f"{request.user.username} a créé une demande pour '{materiel.nom}' du {date_debut} au {date_fin}", demande=demande, materiel=materiel)

        if latitude and longitude:
            Emplacement.objects.create(
                demande=demande,
                adresse=adresse,
                latitude=float(latitude),
                longitude=float(longitude)
            )

        messages.success(request, f'✅ Demande pour "{materiel.nom}" du {date_debut.strftime("%d/%m/%Y")} au {date_fin.strftime("%d/%m/%Y")} envoyée !')
        return redirect('mes_demandes')

    context = {'materiels': materiels, 'materiel_preselectionne': materiel_preselectionne}
    return render(request, 'nouvelle_demande.html', context)


@login_required
def reservations_materiel(request, materiel_id):
    from .models import Reservation
    reservations = Reservation.objects.filter(
        materiel_id=materiel_id,
        statut='active',
        date_fin__gte=timezone.now().date()
    ).values('date_debut', 'date_fin', 'quantite')
    data = [
        {
            'debut': r['date_debut'].strftime('%Y-%m-%d'),
            'fin': r['date_fin'].strftime('%Y-%m-%d'),
            'quantite': r['quantite']
        }
        for r in reservations
    ]
    materiel = get_object_or_404(Materiel, id=materiel_id)
    return JsonResponse({
        'reservations': data,
        'quantite_totale': materiel.quantite_totale,
        'nom': materiel.nom
    })
@login_required
def mes_demandes(request):
    demandes = Demande.objects.filter(utilisateur=request.user).order_by('-date_demande')
    return render(request, 'mes_demandes.html', {'demandes': demandes})


@login_required
def rendre_materiel(request, demande_id):
    demande = get_object_or_404(Demande, id=demande_id, utilisateur=request.user)

    if demande.statut == 'en_cours':
        demande.statut = 'restituee'
        demande.save()

        for ligne in demande.lignes.all():
            ligne.materiel.etat = 'disponible'
            ligne.materiel.save()

            # ✅ log_action déplacé ici, après que 'ligne' est définie
            log_action(
                request,
                'materiel_rendu',
                f"{request.user.username} a rendu le matériel '{ligne.materiel.nom}' (demande #{demande.id})",
                demande=demande,
                materiel=ligne.materiel
            )

            # Notification
            Notification.objects.create(
                message=f"✅ {request.user.username} a rendu le matériel '{ligne.materiel.nom}'",
                type='retour',
                demande=demande
            )

        # ✅ Restitution créée une seule fois, après la boucle
        Restitution.objects.create(
            demande=demande,
            etat_materiel="Bon état",
            observations=f"Matériel rendu par {request.user.username} le {timezone.now().strftime('%d/%m/%Y à %H:%M')}"
        )

        messages.success(request, '✅ Matériel rendu avec succès !')
    else:
        messages.error(request, '❌ Cette demande ne peut pas être rendue')

    return redirect('mes_demandes')

@login_required
def recuperer_materiel(request, demande_id):
    demande = get_object_or_404(Demande, id=demande_id)

    if demande.statut == 'approuvee':
        demande.statut = 'en_cours'
        demande.save()

        for ligne in demande.lignes.all():
            ligne.materiel.etat = 'emprunte'
            ligne.materiel.save()
            log_action(request, 'materiel_recupere', f"{request.user.username} a remis '{ligne.materiel.nom}' a {demande.utilisateur.username}", materiel=ligne.materiel, demande=demande)
            Notification.objects.create(
                message=f"📦 Le materiel '{ligne.materiel.nom}' a ete remis a {demande.utilisateur.username}",
                type='recuperation',
                demande=demande
            )

        messages.success(request, f'✅ Materiel remis a {demande.utilisateur.username} avec succes !')
    else:
        messages.error(request, '❌ Action non autorisee')

    if request.user.is_staff or request.user.role == 'admin':
        return redirect('gestion_demandes')
    return redirect('mes_demandes')

@login_required
def signaler_panne_emprunt(request, demande_id):
    demande = get_object_or_404(Demande, id=demande_id, utilisateur=request.user)
    description = request.POST.get('description', '')

    if demande.statut == 'en_cours':
        for ligne in demande.lignes.all():
            Maintenance.objects.create(
                materiel=ligne.materiel,
                type='panne',
                description=f"{description} (signalé par {request.user.username} le {timezone.now().strftime('%d/%m/%Y')})",
                statut='signale'
            )
            ligne.materiel.etat = 'maintenance'
            ligne.materiel.save()
            log_action(request, 'panne_signalee', f"{request.user.username} a signale une panne sur '{ligne.materiel.nom}' : {description[:100]}", materiel=ligne.materiel)

            Notification.objects.create(
                message=f"⚠️ Panne sur le terrain - {request.user.username} signale: {description[:100]}",
                type='maintenance'
            )

        messages.warning(request, '⚠️ Panne signalée. Un technicien va prendre en charge le matériel.')
    else:
        messages.error(request, '❌ Action non autorisée')

    return redirect('mes_demandes')


@login_required
def profil_etudiant(request):
    if request.method == 'POST':
        request.user.email = request.POST.get('email')
        request.user.telephone = request.POST.get('telephone')
        request.user.filiere = request.POST.get('filiere')
        request.user.niveau = request.POST.get('niveau')
        request.user.save()
        messages.success(request, 'Profil mis à jour !')
        return redirect('profil_etudiant')

    return render(request, 'profil_etudiant.html')


# ==================== CHATBOT IA ====================

@login_required
def chatbot(request):
    return render(request, 'chatbot.html')


@login_required
def chatbot_message(request):
    if request.method == "POST":
        import requests as http_requests
        from django.conf import settings

        data = json.loads(request.body)
        user_message = data.get("message", "")
        mode = data.get("mode", "general")

        conversation, created = ConversationChat.objects.get_or_create(
            utilisateur=request.user,
            defaults={"messages": []}
        )

        historique = conversation.messages[-10:]

        # Detecter automatiquement le mode selon le message
        msg_lower = user_message.lower()
        mots_panne = ["allume", "marche", "fonctionne", "bloque", "erreur", "probleme", "panne", "tombe", "casse", "bug", "ecran", "batterie", "charge", "signal", "gps", "fixe", "plante", "freeze"]
        mots_suggestion = ["recommande", "conseil", "choisir", "quel materiel", "besoin", "leve", "topographique", "mission", "terrain", "projet", "cadastre", "implantation", "nivellement", "bathymetrie"]
        mots_procedure = ["emprunter", "restituer", "rendre", "recuperer", "demande", "reservation", "disponible", "reserver"]

        if any(m in msg_lower for m in mots_panne):
            detected_mode = "diagnostic"
        elif any(m in msg_lower for m in mots_suggestion):
            detected_mode = "suggestion"
        elif any(m in msg_lower for m in mots_procedure):
            detected_mode = "procedure"
        else:
            detected_mode = mode

        # Construire le prompt systeme selon le mode
        base_context = """Tu es un assistant expert en materiel topographique de l'UFR Sciences de l'Ingenieur, Universite de Thies, Senegal.
Le laboratoire dispose de : Stations totales Leica TS16, GPS GNSS differentiel i50/i73, Niveaux optiques electroniques, GPS Garmin de poche.

REGLES ABSOLUES :
- Reponds UNIQUEMENT sur le materiel topographique, les emprunts, les pannes, les procedures du laboratoire
- Si hors-sujet : decline poliment et propose des sujets disponibles
- Toujours en francais, structure et concis
- Utilise des emojis pour rendre la reponse claire"""

        if detected_mode == "diagnostic":
            system_prompt = base_context + """

MODE DIAGNOSTIC DE PANNE :
Quand l'utilisateur decrit un probleme, tu dois :
1. Identifier l'appareil concerne
2. Proposer les causes probables (du plus simple au plus complexe)
3. Donner les solutions etape par etape
4. Indiquer si une intervention technicien est necessaire

Structure ta reponse ainsi :
🔍 DIAGNOSTIC : [nom appareil]
⚠️ Causes probables :
  1. [cause la plus probable]
  2. [autre cause]
🛠️ Solutions a essayer :
  ✅ Etape 1 : [action simple]
  ✅ Etape 2 : [action suivante]
🚨 Si le probleme persiste : Signalez via l'application > "Signaler une panne"

Connaissances pannes specifiques :
- Station totale qui s'eteint : batterie faible, contactes sales, surchauffe
- GPS sans signal : masque ciel insuffisant, initialisation RTK manquante, antenne debranchee
- Niveau optique qui derive : mise en station incorrecte, bulle non centree, vis calantes
- Ecran noir : batterie decharge, reset necessaire (maintenir power 10s)
- Erreur de mesure anormale : prismes sales, calibration requise, refraction atmospherique"""

        elif detected_mode == "suggestion":
            system_prompt = base_context + """

MODE SUGGESTIONS INTELLIGENTES :
Quand l'utilisateur decrit sa mission ou son besoin, recommande le materiel optimal.

Structure ta reponse ainsi :
🎯 MISSION : [type de travail detecte]
📦 MATERIEL RECOMMANDE :
  ⭐ Principal : [materiel 1] - [pourquoi]
  ➕ Complementaire : [materiel 2] - [pourquoi]
  🔋 Accessoires : [liste]
💡 CONSEILS TERRAIN :
  - [conseil 1]
  - [conseil 2]
⏱️ Duree recommandee d'emprunt : [X jours]

Recommandations selon mission :
- Leve topographique general : Station totale + GPS GNSS
- Cadastre/foncier : Station totale Leica TS16 + trépied + prismes
- Implantation : Station totale + mire
- Nivellement : Niveau optique electronique + mire parlante
- Bathymetrie : GPS GNSS differentiel + accessoires
- Reconnaissance rapide : GPS Garmin de poche
- Grande precision : GPS GNSS RTK i50 ou i73"""

        elif detected_mode == "procedure":
            system_prompt = base_context + """

MODE PROCEDURE EMPRUNT :
Guide l'utilisateur sur les procedures du laboratoire.

Procedures disponibles :
- Emprunter : Catalogue > choisir materiel > Nouvelle demande > remplir dates + localisation > soumettre > attendre validation admin
- Recuperer : Espace etudiant > Mes demandes > bouton "Recuperer" (apres approbation admin)
- Rendre : Espace etudiant > Mes demandes > bouton "Rendre" > materiel restitue
- Signaler panne : Espace etudiant > Mes demandes > "Signaler panne" sur emprunt en cours
- Voir reservations : Nouvelle demande > selectionner materiel > calendrier affiche les dates prises

Structure ta reponse avec des etapes numerotees claires."""

        else:
            system_prompt = base_context + """

Reponds de facon claire et structuree. Utilise des emojis pertinents.
Si l'utilisateur semble avoir un probleme avec un appareil, propose le mode diagnostic.
Si l'utilisateur cherche du materiel pour une mission, propose des recommandations."""

        groq_messages = [{"role": "system", "content": system_prompt}]

        for msg in historique:
            groq_messages.append({"role": "user", "content": msg["user"]})
            groq_messages.append({"role": "assistant", "content": msg["bot"]})

        groq_messages.append({"role": "user", "content": user_message})

        try:
            response = http_requests.post(
                "https://api.groq.com/openai/v1/chat/completions",
                headers={
                    "Authorization": f"Bearer {settings.GROQ_API_KEY}",
                    "Content-Type": "application/json"
                },
                json={
                    "model": "llama-3.3-70b-versatile",
                    "messages": groq_messages,
                    "max_tokens": 800,
                    "temperature": 0.6
                },
                timeout=15
            )
            if response.status_code == 200:
                bot_response = response.json()["choices"][0]["message"]["content"]
            else:
                bot_response = "Erreur de connexion a l'IA. Veuillez reessayer."
        except Exception as e:
            bot_response = "Service IA temporairement indisponible. Veuillez reessayer."

        msgs = conversation.messages
        msgs.append({"user": user_message, "bot": bot_response, "date": str(timezone.now()), "mode": detected_mode})
        conversation.messages = msgs[-50:]
        conversation.save()

        return JsonResponse({"response": bot_response, "mode": detected_mode})

    return JsonResponse({"error": "Methode non autorisee"}, status=405)


# ==================== JOURNAL D'ACTIVITE ====================

@staff_member_required
def journal_activite(request):
    from .models import JournalActivite
    journaux = JournalActivite.objects.select_related('utilisateur', 'demande', 'materiel').all()

    # Filtres
    action_filter = request.GET.get('action')
    user_filter = request.GET.get('utilisateur')
    date_filter = request.GET.get('date')

    if action_filter:
        journaux = journaux.filter(action=action_filter)
    if user_filter:
        journaux = journaux.filter(utilisateur__username__icontains=user_filter)
    if date_filter:
        journaux = journaux.filter(date__date=date_filter)

    from .models import JournalActivite as JA
    context = {
        'journaux': journaux[:200],
        'action_choices': JA.ACTION_CHOICES,
        'total': journaux.count(),
    }
    return render(request, 'journal_activite.html', context)


# ─── À ajouter dans views.py ───────────────────────────────────────────────
#
# Importer en haut du fichier :
#   from django.http import HttpResponse
#   from .pdf_documents import generer_fiche_emprunt, generer_recu_restitution, generer_bon_sortie
#

from django.http import HttpResponse
from django.contrib.auth.decorators import login_required
from django.contrib.admin.views.decorators import staff_member_required
from django.shortcuts import get_object_or_404

# Placez pdf_documents.py dans le dossier de votre app (ex: gestion/)
from .pdf_documents import (
    generer_fiche_emprunt,
    generer_recu_restitution,
    generer_bon_sortie,
)


# ── 1. Fiche d'emprunt ──────────────────────────────────────────────────────

@login_required
def pdf_fiche_emprunt(request, demande_id):
    demande = get_object_or_404(Demande, id=demande_id)

    # Seul l'étudiant concerné ou un staff peut télécharger
    if request.user != demande.utilisateur and not request.user.is_staff:
        return HttpResponse('Accès refusé', status=403)

    buf = generer_fiche_emprunt(demande)

    response = HttpResponse(buf, content_type='application/pdf')
    response['Content-Disposition'] = (
        f'inline; filename="fiche_emprunt_{demande.id}.pdf"'
    )
    return response


# ── 2. Reçu de restitution ──────────────────────────────────────────────────

@login_required
def pdf_recu_restitution(request, demande_id):
    demande = get_object_or_404(Demande, id=demande_id)

    if request.user != demande.utilisateur and not request.user.is_staff:
        return HttpResponse('Accès refusé', status=403)

    # Récupérer la restitution si elle existe
    restitution = getattr(demande, 'restitution', None)

    buf = generer_recu_restitution(demande, restitution)

    response = HttpResponse(buf, content_type='application/pdf')
    response['Content-Disposition'] = (
        f'inline; filename="recu_restitution_{demande.id}.pdf"'
    )
    return response


# ── 3. Bon de sortie (staff seulement) ─────────────────────────────────────

@staff_member_required
def pdf_bon_sortie(request, demande_id):
    demande = get_object_or_404(Demande, id=demande_id)

    buf = generer_bon_sortie(demande)

    response = HttpResponse(buf, content_type='application/pdf')
    response['Content-Disposition'] = (
        f'inline; filename="bon_sortie_{demande.id}.pdf"'
    )
    return response

