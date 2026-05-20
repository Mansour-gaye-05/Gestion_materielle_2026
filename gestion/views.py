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


def verifier_retards():
    """
    Met à jour le statut des demandes en retard
    Retourne le nombre de demandes marquées en retard
    """
    aujourdhui = timezone.now().date()

    # Demandes en cours dont la date de fin est dépassée
    demandes_en_retard = Demande.objects.filter(
        statut='en_cours',
        date_fin__lt=aujourdhui
    )

    count = demandes_en_retard.count()

    for demande in demandes_en_retard:
        demande.statut = 'retard'
        demande.save()
        # Ajouter une notification
        Notification.objects.create(
            message=f"⚠️ Demande #{demande.id} en retard depuis le {demande.date_fin.strftime('%d/%m/%Y')}",
            type='retard',
            demande=demande
        )
        log_action(None, 'retard_detecte', f"Demande #{demande.id} marquee en retard", demande=demande)

    return count

# ==================== PAGE D'ACCUEIL ====================

def accueil(request):
    total_types = Materiel.objects.count()
    quantite_totale = sum(m.quantite_totale for m in Materiel.objects.all())
    quantite_disponible = sum(m.quantite_disponible for m in Materiel.objects.all())

    context = {
        'total_types': total_types,
        'quantite_totale': quantite_totale,
        'quantite_disponible': quantite_disponible,
        'total_utilisateurs': Utilisateur.objects.count(),
    }
    return render(request, 'index.html', context)

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
    if etat == 'disponible':
        materiels = materiels.filter(quantite_disponible__gt=0)
        etat_selected = etat
    elif etat:
        materiels = materiels.filter(etat=etat)
        etat_selected = etat
    else:
        etat_selected = None
    # Synchroniser etat avec quantite_disponible
    for m in Materiel.objects.all():
        if m.quantite_disponible > 0 and m.etat == 'emprunte':
            m.etat = 'disponible'
            m.save()
        elif m.quantite_disponible == 0 and m.etat not in ['maintenance', 'hors_service']:
            m.etat = 'emprunte'
            m.save()
    context = {
        'materiels': materiels,
        'categories': categories,
        'categorie_selected': categorie_selected,
        'recherche': recherche,
        'etat_selected': etat_selected,
    }
    return render(request, 'catalogue.html', context)
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

        messages.success(request, f'  Demande pour "{materiel.nom}" envoyee avec succes !')
    else:
        messages.error(request, f'  "{materiel.nom}" n\'est pas disponible')

    return redirect('catalogue')


# ==================== DASHBOARD ADMINISTRATEUR ====================

@staff_member_required
def dashboard(request):
    # Vérifier les retards avant tout
    verifier_retards()

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

    # ========== NOUVEAU : STATISTIQUES DE QUANTITE ==========
    quantite_totale = sum(m.quantite_totale for m in Materiel.objects.all())
    quantite_disponible = sum(m.quantite_disponible for m in Materiel.objects.all())
    quantite_empruntee = quantite_totale - quantite_disponible

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
        # NOUVELLES VARIABLES QUANTITE
        "quantite_totale": quantite_totale,
        "quantite_disponible": quantite_disponible,
        "quantite_empruntee": quantite_empruntee,
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
    # Vérifier les retards avant tout
    verifier_retards()

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

            #   Ne cr er un emplacement que si l' tudiant en a fourni un
            # et qu'il n'existe pas d j 
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

        messages.success(request, f'Maintenance signalee pour {materiel.nom}')
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

        messages.success(request, f'Mat riel "{nom}" ajout  avec succ s')
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
        log_action(request, 'materiel_modifie', f"{request.user.username} a modifie le materiel '{materiel.nom}'", materiel=materiel)

        messages.success(request, f'Materiel "{materiel.nom}" modifie')
        return redirect('gestion_catalogue')

    return redirect('gestion_catalogue')


@staff_member_required
def supprimer_materiel(request, materiel_id):
    materiel = get_object_or_404(Materiel, id=materiel_id)

    if request.method == 'POST':
        nom = materiel.nom
        materiel.delete()
        log_action(request, 'materiel_supprime', f"{request.user.username} a supprime le materiel '{nom}' (ID: {materiel_id})")
        messages.success(request, f'Materiel "{nom}" supprime')

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
        log_action(request, 'role_modifie', f"{request.user.username} a change le role de {utilisateur.username} en '{nouveau_role}'")
        messages.success(request, f'Role de {utilisateur.username} modifie en {nouveau_role}')

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
    })

# ==================== AUTHENTIFICATION ====================


def mot_de_passe_oublie(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        email = request.POST.get('email')
        new_password = request.POST.get('new_password')
        confirm_password = request.POST.get('confirm_password')

        if new_password != confirm_password:
            messages.error(request, 'Les mots de passe ne correspondent pas.')
            return render(request, 'mot_de_passe_oublie.html')

        if len(new_password) < 6:
            messages.error(request, 'Le mot de passe doit contenir au moins 6 caracteres.')
            return render(request, 'mot_de_passe_oublie.html')

        from django.contrib.auth import get_user_model
        User = get_user_model()
        try:
            user = User.objects.get(username=username, email=email)
            user.set_password(new_password)
            user.save()
            messages.success(request, 'Mot de passe reinitialise avec succes. Vous pouvez vous connecter.')
            return redirect('connexion')
        except User.DoesNotExist:
            messages.error(request, "Nom d'utilisateur ou email incorrect.")
    return render(request, 'mot_de_passe_oublie.html')

def connexion(request):
    """Connexion pour les  tudiants"""
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
    messages.info(request, 'Vous etes deconnecte avec succes.')
    return redirect('accueil')


# ==================== ESPACE  TUDIANT ====================

def inscription(request):
    if request.method == 'POST':
        first_name = request.POST.get('first_name')
        last_name = request.POST.get('last_name')
        username = request.POST.get('username')
        email = request.POST.get('email')
        password = request.POST.get('password')
        password2 = request.POST.get('password2')
        filiere = request.POST.get('filiere')
        niveau = request.POST.get('niveau')
        telephone = request.POST.get('telephone')

        # Validation email universitaire
        if not re.match(r'^[a-z]+\.[a-z]+[0-9]@univ-thies\.sn$', email):
            messages.error(request,
                           'Format d\'email invalide. Utilisez: prenom.nom3@univ-thies.sn (ex: astou.gueye3@univ-thies.sn)')
            return render(request, 'inscription.html')

        # Validation prénom et nom
        if not first_name or not last_name:
            messages.error(request, 'Veuillez renseigner votre prénom et votre nom.')
            return render(request, 'inscription.html')

        if password == password2:
            if not Utilisateur.objects.filter(username=username).exists():
                utilisateur = Utilisateur.objects.create_user(
                    username=username,
                    email=email,
                    password=password,
                    first_name=first_name,
                    last_name=last_name,
                    role='etudiant',
                    filiere=filiere,
                    niveau=niveau,
                    telephone=telephone
                )
                login(request, utilisateur)
                log_action(request, 'inscription',
                           f"Nouveau compte créé : {first_name} {last_name} ({username}) - {filiere} - {niveau}")
                messages.success(request, f'Bienvenue {first_name} {last_name} ! Votre compte a été créé avec succès.')
                return redirect('espace_etudiant')
            else:
                messages.error(request, 'Ce nom d\'utilisateur existe déjà.')
        else:
            messages.error(request, 'Les mots de passe ne correspondent pas.')

    return render(request, 'inscription.html')

@login_required

@login_required

@login_required
@login_required
def profil_enseignant(request):
    if request.user.role not in ['enseignant', 'admin'] and not request.user.is_superuser:
        messages.error(request, 'Accès non autorisé.')
        return redirect('accueil')

    if request.method == 'POST':
        user = request.user
        user.first_name = request.POST.get('first_name', '')
        user.last_name = request.POST.get('last_name', '')
        user.email = request.POST.get('email', '')
        user.telephone = request.POST.get('telephone', '')
        user.filiere = request.POST.get('filiere', '')
        new_password = request.POST.get('new_password', '')

        if new_password:
            if len(new_password) >= 6:
                user.set_password(new_password)
                from django.contrib.auth import update_session_auth_hash
                update_session_auth_hash(request, user)
                messages.success(request, 'Mot de passe mis à jour.')
            else:
                messages.error(request, 'Le mot de passe doit contenir au moins 6 caractères.')

        user.save()
        messages.success(request, 'Profil mis à jour avec succès.')
        return redirect('profil_enseignant')

    return render(request, 'profil_enseignant.html')

@login_required
def profil_technicien(request):
    if request.user.role not in ['technicien', 'admin']:
        return redirect('accueil')
    if request.method == 'POST':
        user = request.user
        user.first_name = request.POST.get('first_name', '')
        user.last_name = request.POST.get('last_name', '')
        user.email = request.POST.get('email', '')
        user.telephone = request.POST.get('telephone', '')
        new_password = request.POST.get('new_password', '')
        if new_password:
            user.set_password(new_password)
            messages.success(request, 'Mot de passe mis a jour.')
        user.save()
        messages.success(request, 'Profil mis a jour avec succes.')
        return redirect('profil_technicien')
    return render(request, 'profil_technicien.html')

def espace_technicien(request):
    if request.user.role not in ['technicien', 'admin'] and not request.user.is_superuser:
        messages.error(request, 'Acces non autorise.')
        return redirect('accueil')
    from gestion.models import Maintenance, Materiel
    maintenances = Maintenance.objects.select_related('materiel').order_by('-date_signalement')
    stats = {
        'signalees': maintenances.filter(statut='signale').count(),
        'en_cours': maintenances.filter(statut='en_cours').count(),
        'resolues': maintenances.filter(statut='resolu').count(),
        'total': maintenances.count(),
    }
    return render(request, 'espace_technicien.html', {
        'maintenances': maintenances,
        'stats': stats,
    })


def espace_enseignant(request):
    if request.user.role not in ['enseignant', 'admin'] and not request.user.is_superuser:
        messages.error(request, 'Accès non autorisé.')
        return redirect('accueil')

    demandes = Demande.objects.filter(utilisateur=request.user).order_by('-date_demande')

    stats = {
        'total': demandes.count(),
        'en_attente': demandes.filter(statut='en_attente').count(),
        'approuvees': demandes.filter(statut='approuvee').count(),
        'en_cours': demandes.filter(statut='en_cours').count(),
        'restituees': demandes.filter(statut='restituee').count(),
        'retard': demandes.filter(statut='retard').count(),
    }

    emprunts_actifs = demandes.filter(statut='en_cours')
    notifications = Notification.objects.filter(demande__utilisateur=request.user).order_by('-date')[:10]

    return render(request, 'espace_enseignant.html', {
        'demandes': demandes,
        'stats': stats,
        'emprunts_actifs': emprunts_actifs,
        'notifications': notifications,
        'today': timezone.now().date(),
    })

@login_required
def enseignant_valider_demande(request, demande_id):
    if request.user.role not in ['enseignant', 'admin'] and not request.user.is_superuser:
        messages.error(request, 'Accès non autorisé.')
        return redirect('accueil')

    demande = get_object_or_404(Demande, id=demande_id)
    action = request.POST.get('action')
    motif_refus = request.POST.get('motif_refus', '')

    if action == 'approuver' and demande.statut == 'en_attente':
        demande.statut = 'approuvee'
        demande.valide_par = request.user
        demande.date_validation = timezone.now()
        demande.save()
        Notification.objects.create(
            message=f"Votre demande #{demande.id} a été approuvée par {request.user.username}.",
            type='validation',
            demande=demande
        )
        messages.success(request, f'Demande #{demande.id} approuvée !')

    elif action == 'refuser' and demande.statut == 'en_attente':
        demande.statut = 'refusee'
        demande.motif_refus = motif_refus
        demande.valide_par = request.user
        demande.save()
        Notification.objects.create(
            message=f"Votre demande #{demande.id} a été refusée. Motif: {motif_refus}",
            type='refus',
            demande=demande
        )
        messages.warning(request, f'Demande #{demande.id} refusée.')

    return redirect('espace_enseignant')

def espace_etudiant(request):
    # Vérifier les retards avant tout
    verifier_retards()

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

    # Dernieres demandes (5 dernieres)
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
            messages.error(request, '  La date de debut ne peut pas etre dans le passe.')
            return render(request, 'nouvelle_demande.html', {'materiels': materiels, 'materiel_preselectionne': materiel_preselectionne})

        materiel = get_object_or_404(Materiel, id=materiel_id)

        # V rification du stock
        if materiel.quantite_disponible < 1:
            messages.error(request, f'  "{materiel.nom}" n\'est plus disponible.')
            return render(request, 'nouvelle_demande.html', {'materiels': materiels, 'materiel_preselectionne': materiel_preselectionne})

        # V rification des conflits de r servation
        conflit, qte_reservee = Reservation.verifier_conflit(materiel_id, date_debut, date_fin)
        if conflit:
            messages.error(request, f'  "{materiel.nom}" est d j  r serv  sur cette p riode (quantit  r serv e: {qte_reservee}/{materiel.quantite_totale}). Choisissez d\'autres dates.')
            return render(request, 'nouvelle_demande.html', {'materiels': materiels, 'materiel_preselectionne': materiel_preselectionne})

        # Cr ation de la demande
        demande = Demande.objects.create(
            utilisateur=request.user,
            date_debut=date_debut,
            date_fin=date_fin,
            statut='en_attente',
            motif=f"Demande pour {materiel.nom}"
        )

        LigneDemande.objects.create(demande=demande, materiel=materiel, quantite=1)

        # Cr ation de la r servation
        Reservation.objects.create(
            materiel=materiel,
            utilisateur=request.user,
            demande=demande,
            date_debut=date_debut,
            date_fin=date_fin,
            quantite=1,
            statut='active'
        )
        log_action(request, 'demande_creee', f"{request.user.username} a cr  une demande pour '{materiel.nom}' du {date_debut} au {date_fin}", demande=demande, materiel=materiel)

        if latitude and longitude:
            Emplacement.objects.create(
                demande=demande,
                adresse=adresse,
                latitude=float(latitude),
                longitude=float(longitude)
            )

        messages.success(request, f'  Demande pour "{materiel.nom}" du {date_debut.strftime("%d/%m/%Y")} au {date_fin.strftime("%d/%m/%Y")} envoy e !')
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

@login_required
def annuler_demande(request, demande_id):
    demande = get_object_or_404(Demande, id=demande_id, utilisateur=request.user)
    if demande.statut == 'en_attente':
        demande.statut = 'annulee'
        demande.save()
        for ligne in demande.lignes.all():
            ligne.materiel.quantite_disponible = min(ligne.materiel.quantite_totale, ligne.materiel.quantite_disponible + ligne.quantite)
            if ligne.materiel.quantite_disponible > 0:
                ligne.materiel.etat = 'disponible'
            ligne.materiel.save()
        log_action(request, 'demande_annulee',
            f"{request.user.username} a annule la demande #{demande.id}",
            demande=demande)
        messages.success(request, f'Demande #{demande.id} annulee avec succes.')
    else:
        messages.error(request, 'Cette demande ne peut pas etre annulee.')
    return redirect('mes_demandes')


@login_required
def annuler_demande(request, demande_id):
    demande = get_object_or_404(Demande, id=demande_id, utilisateur=request.user)
    if demande.statut == 'en_attente':
        demande.statut = 'annulee'
        demande.save()
        for ligne in demande.lignes.all():
            ligne.materiel.quantite_disponible = min(ligne.materiel.quantite_totale, ligne.materiel.quantite_disponible + ligne.quantite)
            if ligne.materiel.quantite_disponible > 0:
                ligne.materiel.etat = 'disponible'
            ligne.materiel.save()
        log_action(request, 'demande_annulee',
            f"{request.user.username} a annule la demande #{demande.id}",
            demande=demande)
        messages.success(request, f'Demande #{demande.id} annulee avec succes.')
    else:
        messages.error(request, 'Cette demande ne peut pas etre annulee.')
    return redirect('mes_demandes')


@login_required
def detail_demande(request, demande_id):
    demande = get_object_or_404(Demande, id=demande_id, utilisateur=request.user)
    lignes = demande.lignes.select_related('materiel').all()
    return render(request, 'detail_demande.html', {
        'demande': demande,
        'lignes': lignes,
    })


def mes_demandes(request):
    # Vérifier les retards avant tout
    verifier_retards()

    demandes = Demande.objects.filter(utilisateur=request.user).order_by('-date_demande')
    statut_filter = request.GET.get('statut', '')
    search = request.GET.get('search', '')

    if statut_filter:
        demandes = demandes.filter(statut=statut_filter)
    if search:
        demandes = demandes.filter(lignes__materiel__nom__icontains=search).distinct()

    return render(request, 'mes_demandes.html', {
        'demandes': demandes,
        'statut_filter': statut_filter,
        'search': search,
    })


@login_required
def rendre_materiel(request, demande_id):
    demande = get_object_or_404(Demande, id=demande_id)

    if demande.statut == 'en_cours':
        demande.statut = 'restituee'
        demande.save()

        for ligne in demande.lignes.all():
            ligne.materiel.quantite_disponible = min(ligne.materiel.quantite_totale, ligne.materiel.quantite_disponible + ligne.quantite)
            if ligne.materiel.quantite_disponible > 0:
                ligne.materiel.etat = 'disponible'
            ligne.materiel.save()

            #   log_action d plac  ici, apr s que 'ligne' est d finie
            log_action(
                request,
                'materiel_rendu',
                f"{request.user.username} a rendu le materiel '{ligne.materiel.nom}' (demande #{demande.id})",
                demande=demande,
                materiel=ligne.materiel
            )

            # Notification
            Notification.objects.create(
                message=f"  {request.user.username} a rendu le materiel '{ligne.materiel.nom}'",
                type='retour',
                demande=demande
            )

        #   Restitution cr e une seule fois, apr s la boucle
        Restitution.objects.get_or_create(
            demande=demande,
            defaults={
                'etat_materiel': 'Bon etat',
                'observations': f'Materiel rendu par {request.user.username}'
            }
        )

        messages.success(request, '  Materiel rendu avec succes !')
    else:
        messages.error(request, '  Cette demande ne peut pas  etre rendue')

    return redirect('mes_demandes')

@login_required
def recuperer_materiel(request, demande_id):
    demande = get_object_or_404(Demande, id=demande_id)

    if demande.statut == 'approuvee':
        demande.statut = 'en_cours'
        demande.save()

        for ligne in demande.lignes.all():
            ligne.materiel.etat = 'emprunte'
            ligne.materiel.quantite_disponible = max(0, ligne.materiel.quantite_disponible - ligne.quantite)
            if ligne.materiel.quantite_disponible == 0:
                ligne.materiel.etat = 'emprunte'
            ligne.materiel.save()
            log_action(request, 'materiel_recupere', f"{request.user.username} a remis '{ligne.materiel.nom}' a {demande.utilisateur.username}", materiel=ligne.materiel, demande=demande)
            Notification.objects.create(
                message=f"  Le materiel '{ligne.materiel.nom}' a ete remis a {demande.utilisateur.username}",
                type='recuperation',
                demande=demande
            )

        messages.success(request, f'  Materiel remis a {demande.utilisateur.username} avec succes !')
    else:
        messages.error(request, '  Action non autorisee')

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
                description=f"{description} (signale par {request.user.username} le {timezone.now().strftime('%d/%m/%Y')})",
                statut='signale'
            )
            ligne.materiel.etat = 'maintenance'
            ligne.materiel.save()
            log_action(request, 'panne_signalee', f"{request.user.username} a signale une panne sur '{ligne.materiel.nom}' : {description[:100]}", materiel=ligne.materiel)

            Notification.objects.create(
                message=f"  Panne sur le terrain - {request.user.username} signale: {description[:100]}",
                type='maintenance'
            )

        messages.warning(request, '  Panne signalee. Un technicien va prendre en charge le materiel.')
    else:
        messages.error(request, '  Action non autorisee')

    return redirect('mes_demandes')


@login_required
def signaler_panne_page(request, demande_id):
    """Page dédiée pour signaler une panne (contourne le modal)"""
    from .models import Demande, Maintenance
    from django.contrib import messages
    from django.shortcuts import redirect, render, get_object_or_404

    demande = get_object_or_404(Demande, id=demande_id, utilisateur=request.user)

    if demande.statut != 'en_cours':
        messages.error(request, 'Seules les demandes en cours peuvent signaler une panne.')
        return redirect('mes_demandes')

    if request.method == 'POST':
        description = request.POST.get('description', '')

        if not description:
            messages.error(request, 'Veuillez décrire la panne.')
            return render(request, 'signaler_panne.html', {'demande': demande})

        for ligne in demande.lignes.all():
            Maintenance.objects.create(
                materiel=ligne.materiel,
                type='panne',
                description=f"{description} (signalé par {request.user.username} le {timezone.now().strftime('%d/%m/%Y')})",
                statut='signale'
            )
            ligne.materiel.etat = 'maintenance'
            ligne.materiel.save()

            log_action(request, 'panne_signalee',
                       f"{request.user.username} a signalé une panne sur '{ligne.materiel.nom}' : {description[:100]}",
                       materiel=ligne.materiel)

            Notification.objects.create(
                message=f"🚨 Panne sur le terrain - {request.user.username} signale: {description[:100]}",
                type='maintenance'
            )

        messages.warning(request, '✅ Panne signalée avec succès ! Un technicien va prendre en charge le matériel.')
        return redirect('mes_demandes')

    return render(request, 'signaler_panne.html', {'demande': demande})


@login_required
def profil_etudiant(request):
    if request.method == 'POST':
        request.user.email = request.POST.get('email')
        request.user.telephone = request.POST.get('telephone')
        request.user.filiere = request.POST.get('filiere')
        request.user.niveau = request.POST.get('niveau')
        if 'photo_profil' in request.FILES:
            request.user.photo_profil = request.FILES['photo_profil']
        request.user.save()
        messages.success(request, 'Profil mis a jour !')
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
        from django.core.paginator import Paginator

        data = json.loads(request.body)
        user_message = data.get("message", "")
        mode = data.get("mode", "general")
        action = data.get("action", "send")  # send, clear_history, get_history

        conversation, created = ConversationChat.objects.get_or_create(
            utilisateur=request.user,
            defaults={"messages": []}
        )

        # Action : Effacer l'historique
        if action == "clear_history":
            conversation.messages = []
            conversation.save()
            return JsonResponse({"status": "success", "message": "Historique effacé"})

        # Action : Récupérer l'historique
        if action == "get_history":
            page = int(data.get("page", 1))
            per_page = 20
            messages_list = conversation.messages[-100:]  # Derniers 100 messages max
            paginator = Paginator(messages_list, per_page)
            current_page = paginator.page(page)
            return JsonResponse({
                "status": "success",
                "history": list(current_page.object_list),
                "total_pages": paginator.num_pages,
                "current_page": page,
                "has_next": current_page.has_next(),
                "has_previous": current_page.has_previous()
            })

        historique = conversation.messages[-30:]  # Garder les 30 derniers messages

        # Détection améliorée des intentions
        msg_lower = user_message.lower()

        mots_panne = ["allume", "marche", "fonctionne", "bloque", "erreur", "probleme", "panne", "tombe", "casse",
                      "ecran", "batterie", "signal", "freeze", "plante", "redemarre", "eteint", "chauffe", "bruit",
                      "affichage", "ne s'allume", "ne fonctionne"]
        mots_suggestion = ["recommande", "conseil", "choisir", "quel materiel", "mission", "terrain", "leve",
                           "cadastre", "implantation", "nivellement", "topographie", "projet", "besoin", "pour faire",
                           "comment mesurer", "quel appareil"]
        mots_procedure = ["emprunter", "restituer", "rendre", "recuperer", "demande", "reservation", "comment faire",
                          "procedure", "etapes", "marches a suivre", "comment obtenir", "delai", "combien de temps"]
        mots_ameliorer = ["ameliore", "ameliorer", "plus detail", "plus precis", "developpe", "approfondi",
                          "explique mieux", "plus complet", "detaille", "autre facon", "reformule", "precisement",
                          "peux tu developper", "ajoute des details", "plus d infos", "plus technique"]
        mots_historique = ["historique", "conversation précédente", "ce qu'on a dit", "messages précédents",
                           "rappelle moi", "c'était quoi"]
        mots_remerciement = ["merci", "thanks", "super", "parfait", "top", "genial", "cool", "merci beaucoup", "bravo",
                             "excellent"]

        # Récupérer la dernière réponse
        derniere_reponse_assistant = ""
        for msg in reversed(historique):
            if "bot" in msg:
                derniere_reponse_assistant = msg.get("bot", "")
                break

        # Détection du mode
        if any(m in msg_lower for m in mots_ameliorer):
            detected_mode = "amelioration"
        elif any(m in msg_lower for m in mots_historique):
            detected_mode = "historique"
        elif any(m in msg_lower for m in mots_panne):
            detected_mode = "diagnostic"
        elif any(m in msg_lower for m in mots_suggestion):
            detected_mode = "suggestion"
        elif any(m in msg_lower for m in mots_procedure):
            detected_mode = "procedure"
        elif any(m in msg_lower for m in mots_remerciement):
            detected_mode = "remerciement"
        else:
            detected_mode = mode

        # ==================== CONSTRUCTION DU PROMPT ====================

        system_prompt = """Tu es un assistant expert et convivial en matériel topographique pour l'UFR Sciences de l'Ingénieur, Université de Thiès, Sénégal.

**Matériels disponibles :**
- Stations totales Leica TS16 / TS13 (précision 1 seconde)
- GPS GNSS différentiel i50 / i73 (précision RTK 1-2 cm)
- Niveaux optiques et électroniques (précision ±0.5mm/30m)
- GPS Garmin de poche (navigation, précision 3-5m)

**TON STYLE :**
- Sois naturel, amical et professionnel
- Utilise des emojis avec parcimonie
- Structure tes réponses avec des listes claires
- Adopte un ton qui inspire confiance
- Termine parfois par une question ouverte

**RÈGLES :**
- Réponds UNIQUEMENT sur le matériel topographique, les emprunts, les pannes et les procédures
- Si hors-sujet, décline poliment
- Utilise l'historique de la conversation que tu reçois pour contextualiser tes réponses
"""

        # Mode HISTORIQUE
        if detected_mode == "historique":
            # Construire un résumé de l'historique
            historique_resume = "\n".join([
                f"Utilisateur : {msg['user']}\nAssistant : {msg['bot'][:200]}..."
                for msg in historique[-5:] if "user" in msg and "bot" in msg
            ])
            system_prompt += f"""

MODE HISTORIQUE - RAPPEL DE CONVERSATION

L'utilisateur demande à voir ou à se souvenir de la conversation précédente.

Voici l'historique récent de votre conversation :
---
{historique_resume}
---

Réponds à l'utilisateur en lui résumant ce qui a été dit précédemment, en répondant à sa question spécifique sur l'historique.
"""

        # Mode AMELIORATION
        elif detected_mode == "amelioration":
            system_prompt += f"""

MODE AMÉLIORATION - DÉVELOPPEMENT DE LA RÉPONSE

L'utilisateur trouve que ta réponse manque de détails.

Ta DERNIÈRE RÉPONSE à améliorer :
---
{derniere_reponse_assistant}
---

**À faire :**
1. Améliore UNIQUEMENT la réponse ci-dessus
2. Ajoute des détails techniques (chiffres, protocoles)
3. Donne des conseils pratiques
4. Sois plus complet (+50% de contenu)
"""

        # Mode DIAGNOSTIC
        elif detected_mode == "diagnostic":
            system_prompt += """

MODE DIAGNOSTIC - STRUCTURE À SUIVRE :

🔍 **Diagnostic :** [appareil concerné]

📋 **Causes probables (du simple au complexe) :**
1. [cause 1]
2. [cause 2]

🔧 **Solutions étape par étape :**
• Étape 1 : [action simple]
• Étape 2 : [action suivante]

💡 **Astuce terrain :** [conseil pratique]

🚨 **Si persiste :** Signalez via "Mes demandes" > "Signaler une panne"
"""

        # Mode SUGGESTION
        elif detected_mode == "suggestion":
            system_prompt += """

MODE SUGGESTION - STRUCTURE À SUIVRE :

📌 **Mission identifiée :** [type de mission]

🎯 **Matériel recommandé :**
• **Principal :** [nom] — [raison]
• **Complémentaire :** [nom] — [utilité]

💡 **Conseils terrain :**
• [conseil 1]
• [conseil 2]

⏱️ **Durée recommandée :** [X jours]
"""

        # Mode PROCEDURE
        elif detected_mode == "procedure":
            system_prompt += """

MODE PROCÉDURE - STRUCTURE À SUIVRE :

📋 **Procédure [action] :**

1. **Étape 1 :** [action précise]
2. **Étape 2 :** [action suivante]
3. **Étape 3 :** [action finale]

ℹ️ **À savoir :** [info complémentaire]
"""

        # Mode REMERCIEMENT
        elif detected_mode == "remerciement":
            system_prompt += """

MODE REMERCIEMENT - RÉPONSE CHALEUREUSE

L'utilisateur vous remercie. Répondez avec enthousiasme et proposez votre aide pour la suite.

Exemple : "Avec plaisir ! N'hésitez pas si vous avez d'autres questions. Bon terrain ! 🚀"
"""

        # Construction des messages pour l'API
        groq_messages = [{"role": "system", "content": system_prompt}]

        # Ajouter l'historique (sauf pour mode amélioration)
        if detected_mode not in ["amelioration", "historique"]:
            for msg in historique[-8:]:
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
                    "max_tokens": 1000,
                    "temperature": 0.7,
                },
                timeout=25
            )
            if response.status_code == 200:
                bot_response = response.json()["choices"][0]["message"]["content"]
            else:
                bot_response = "🔌 Désolé, l'assistant rencontre une difficulté. Veuillez réessayer."
        except http_requests.exceptions.Timeout:
            bot_response = "⏰ L'assistant met trop de temps à répondre. Réessayez."
        except Exception as e:
            bot_response = "🌐 Service momentanément indisponible. Réessayez plus tard."

        # Sauvegarde dans l'historique
        msgs = conversation.messages
        msgs.append({
            "user": user_message,
            "bot": bot_response,
            "date": str(timezone.now()),
            "mode": detected_mode
        })
        conversation.messages = msgs[-100:]  # Garder les 100 derniers messages
        conversation.save()

        return JsonResponse({
            "response": bot_response,
            "mode": detected_mode,
            "history_count": len(msgs)
        })

    return JsonResponse({"error": "Méthode non autorisée"}, status=405)

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


#     ajouter dans views.py  
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


#   1. Fiche d'emprunt  

@login_required
def pdf_fiche_emprunt(request, demande_id):
    demande = get_object_or_404(Demande, id=demande_id)

    # Seul l' tudiant concern  ou un staff peut t l charger
    if request.user != demande.utilisateur and not request.user.is_staff:
        return HttpResponse('Acc s refus ', status=403)

    buf = generer_fiche_emprunt(demande)

    response = HttpResponse(buf, content_type='application/pdf')
    response['Content-Disposition'] = (
        f'inline; filename="fiche_emprunt_{demande.id}.pdf"'
    )
    return response


#   2. Re u de restitution  

@login_required
def pdf_recu_restitution(request, demande_id):
    demande = get_object_or_404(Demande, id=demande_id)

    if request.user != demande.utilisateur and not request.user.is_staff:
        return HttpResponse('Acc s refus ', status=403)

    # R cup rer la restitution si elle existe
    restitution = getattr(demande, 'restitution', None)

    buf = generer_recu_restitution(demande, restitution)

    response = HttpResponse(buf, content_type='application/pdf')
    response['Content-Disposition'] = (
        f'inline; filename="recu_restitution_{demande.id}.pdf"'
    )
    return response


#   3. Bon de sortie (staff seulement)  

@staff_member_required
def pdf_bon_sortie(request, demande_id):
    demande = get_object_or_404(Demande, id=demande_id)

    buf = generer_bon_sortie(demande)

    response = HttpResponse(buf, content_type='application/pdf')
    response['Content-Disposition'] = (
        f'inline; filename="bon_sortie_{demande.id}.pdf"'
    )
    return response




# ==================== BON DE SORTIE PDF ====================

@login_required
def bon_sortie_pdf(request, demande_id):
    demande = get_object_or_404(Demande, id=demande_id)
    if not request.user.is_staff and demande.utilisateur != request.user:
        return redirect("espace_etudiant")

    response = HttpResponse(content_type="application/pdf")
    response["Content-Disposition"] = f"attachment; filename=bon_sortie_{demande.id}.pdf"

    p = canvas.Canvas(response, pagesize=A4)
    width, height = A4

    # En-tete
    p.setFillColorRGB(0.17, 0.24, 0.31)
    p.rect(0, height - 100, width, 100, fill=1, stroke=0)
    p.setFillColorRGB(1, 1, 1)
    p.setFont("Helvetica-Bold", 16)
    p.drawString(40, height - 40, "UFR Sciences de l'Ingenieur")
    p.setFont("Helvetica", 12)
    p.drawString(40, height - 62, "Universite de Thies - Laboratoire de Topographie")
    p.setFont("Helvetica-Bold", 14)
    p.drawCentredString(width / 2, height - 88, "BON DE SORTIE MATERIEL")
    p.setFillColorRGB(0, 0, 0)

    # Numero et date
    y = height - 130
    p.setFont("Helvetica-Bold", 11)
    p.drawString(40, y, f"Bon N : {demande.id:04d}")
    p.drawRightString(width - 40, y, f"Date : {timezone.now().strftime('%d/%m/%Y')}")
    y -= 30

    # Separateur
    p.setStrokeColorRGB(0.17, 0.24, 0.31)
    p.setLineWidth(2)
    p.line(40, y, width - 40, y)
    y -= 25

    # Infos etudiant
    p.setFont("Helvetica-Bold", 12)
    p.drawString(40, y, "INFORMATIONS EMPRUNTEUR")
    y -= 20
    p.setFont("Helvetica", 11)
    p.drawString(40, y, f"Nom d'utilisateur : {demande.utilisateur.username}")
    y -= 18
    p.drawString(40, y, f"Email : {demande.utilisateur.email or 'Non renseigne'}")
    y -= 18
    p.drawString(40, y, f"Filiere : {demande.utilisateur.filiere or 'Non renseignee'}")
    y -= 18
    p.drawString(40, y, f"Niveau : {demande.utilisateur.niveau or 'Non renseigne'}")
    y -= 30

    # Separateur
    p.setLineWidth(1)
    p.line(40, y, width - 40, y)
    y -= 25

    # Infos demande
    p.setFont("Helvetica-Bold", 12)
    p.drawString(40, y, "DETAILS DE L'EMPRUNT")
    y -= 20
    p.setFont("Helvetica", 11)
    p.drawString(40, y, f"Date de debut : {demande.date_debut.strftime('%d/%m/%Y')}")
    y -= 18
    p.drawString(40, y, f"Date de fin : {demande.date_fin.strftime('%d/%m/%Y')}")
    y -= 18
    p.drawString(40, y, f"Statut : {demande.get_statut_display()}")
    if demande.valide_par:
        y -= 18
        p.drawString(40, y, f"Valide par : {demande.valide_par.username}")
    y -= 30

    # Separateur
    p.line(40, y, width - 40, y)
    y -= 25

    # Materiels
    p.setFont("Helvetica-Bold", 12)
    p.drawString(40, y, "MATERIELS EMPRUNTES")
    y -= 20

    # Tableau materiels
    p.setFillColorRGB(0.17, 0.24, 0.31)
    p.rect(40, y - 5, width - 80, 20, fill=1, stroke=0)
    p.setFillColorRGB(1, 1, 1)
    p.setFont("Helvetica-Bold", 10)
    p.drawString(50, y + 2, "Materiel")
    p.drawString(300, y + 2, "Categorie")
    p.drawString(430, y + 2, "Quantite")
    p.setFillColorRGB(0, 0, 0)
    y -= 20

    p.setFont("Helvetica", 10)
    for i, ligne in enumerate(demande.lignes.all()):
        if i % 2 == 0:
            p.setFillColorRGB(0.95, 0.95, 0.95)
            p.rect(40, y - 4, width - 80, 16, fill=1, stroke=0)
        p.setFillColorRGB(0, 0, 0)
        p.drawString(50, y, ligne.materiel.nom[:35])
        p.drawString(300, y, (ligne.materiel.categorie.libelle if ligne.materiel.categorie else "-")[:20])
        p.drawString(430, y, str(ligne.quantite))
        y -= 18

    y -= 20
    p.line(40, y, width - 40, y)
    y -= 30

    # Emplacement si disponible
    emplacement = demande.emplacements.first()
    if emplacement and emplacement.adresse:
        p.setFont("Helvetica-Bold", 11)
        p.drawString(40, y, f"Lieu d'utilisation : {emplacement.adresse}")
        y -= 30

    # Signatures
    y -= 20
    p.setFont("Helvetica-Bold", 11)
    p.drawString(60, y, "Signature Emprunteur")
    p.drawString(350, y, "Signature Responsable")
    y -= 60
    p.line(60, y, 220, y)
    p.line(350, y, 510, y)

    # Pied de page
    p.setFont("Helvetica", 8)
    p.setFillColorRGB(0.5, 0.5, 0.5)
    p.drawCentredString(width / 2, 30, f"Document genere le {timezone.now().strftime('%d/%m/%Y a %H:%M')} - UFR Sciences de l'Ingenieur, Universite de Thies")

    p.save()
    return response


# ==================== NOTIFICATIONS TEMPS REEL ====================

@login_required
def notifications_count(request):
    count = Notification.objects.filter(
        demande__utilisateur=request.user,
        lu=False
    ).count()
    notifications = Notification.objects.filter(
        demande__utilisateur=request.user
    ).order_by('-date')[:5]
    data = {
        'count': count,
        'notifications': [
            {
                'message': n.message,
                'type': n.type,
                'date': n.date.strftime('%d/%m %H:%M'),
                'lu': n.lu
            }
            for n in notifications
        ]
    }
    return JsonResponse(data)

@login_required
def marquer_notifications_lues(request):
    if request.method == 'POST':
        Notification.objects.filter(
            demande__utilisateur=request.user,
            lu=False
        ).update(lu=True)
        return JsonResponse({'status': 'ok'})
    return JsonResponse({'error': 'methode non autorisee'}, status=405)


@staff_member_required
def notifications_admin_count(request):
    notifs = Notification.objects.all().order_by('-date')[:10]
    count = Notification.objects.filter(lu=False).count()
    data = {
        'count': count,
        'notifications': [
            {
                'message': n.message,
                'type': n.type,
                'date': n.date.strftime('%d/%m %H:%M'),
                'lu': n.lu
            }
            for n in notifs
        ]
    }
    return JsonResponse(data)

@staff_member_required
def marquer_notifications_admin_lues(request):
    if request.method == 'POST':
        Notification.objects.filter(lu=False).update(lu=True)
        return JsonResponse({'status': 'ok'})
    return JsonResponse({'error': 'methode non autorisee'}, status=405)


# ==================== CHANGER MOT DE PASSE ====================

@login_required
def changer_mot_de_passe(request):
    if request.method == 'POST':
        ancien = request.POST.get('ancien_mdp')
        nouveau = request.POST.get('nouveau_mdp')
        confirmer = request.POST.get('confirmer_mdp')

        if not request.user.check_password(ancien):
            messages.error(request, 'Ancien mot de passe incorrect.')
        elif nouveau != confirmer:
            messages.error(request, 'Les nouveaux mots de passe ne correspondent pas.')
        elif len(nouveau) < 6:
            messages.error(request, 'Le mot de passe doit contenir au moins 6 caracteres.')
        else:
            request.user.set_password(nouveau)
            request.user.save()
            log_action(request, 'connexion', f'{request.user.username} a change son mot de passe')
            from django.contrib.auth import update_session_auth_hash
            update_session_auth_hash(request, request.user)
            messages.success(request, 'Mot de passe change avec succes !')
            return redirect('profil_etudiant')

    return redirect('profil_etudiant')


# ==================== ANNULER DEMANDE ====================

@login_required
def annuler_demande(request, demande_id):
    demande = get_object_or_404(Demande, id=demande_id, utilisateur=request.user)

    if demande.statut in ['en_attente', 'approuvee']:
        ancien_statut = demande.statut
        demande.statut = 'refusee'
        demande.motif_refus = f"Annulee par l etudiant le {timezone.now().strftime('%d/%m/%Y a %H:%M')}"
        demande.save()

        # Remettre le materiel disponible si approuvee
        if ancien_statut == 'approuvee':
            for ligne in demande.lignes.all():
                ligne.materiel.etat = 'disponible'
                ligne.materiel.save()

        # Annuler la reservation
        from .models import Reservation
        Reservation.objects.filter(demande=demande).update(statut='annulee')

        log_action(request, 'demande_refusee', f"{request.user.username} a annule sa demande #{demande.id}", demande=demande)
        messages.success(request, f'Demande #{demande.id} annulee avec succes.')
    else:
        messages.error(request, 'Cette demande ne peut pas etre annulee.')

    return redirect('mes_demandes')


@login_required
def changer_nom_utilisateur(request):
    if request.method == 'POST':
        nouveau_nom = request.POST.get('nouveau_username')
        if nouveau_nom:
            # Vérifier si le nom existe déjà
            if Utilisateur.objects.filter(username=nouveau_nom).exclude(id=request.user.id).exists():
                messages.error(request, 'Ce nom d\'utilisateur est déjà pris.')
            else:
                ancien_nom = request.user.username
                request.user.username = nouveau_nom
                request.user.save()
                log_action(request, 'modification_profil',
                           f"{ancien_nom} a changé son nom d'utilisateur en {nouveau_nom}")
                messages.success(request, f'Nom d\'utilisateur changé avec succès en "{nouveau_nom}"')
        else:
            messages.error(request, 'Le nom d\'utilisateur ne peut pas être vide.')

        # Rediriger vers le profil approprié
        if request.user.role == 'enseignant':
            return redirect('profil_enseignant')
        elif request.user.role == 'technicien':
            return redirect('profil_technicien')
        else:
            return redirect('profil_etudiant')

    return redirect('espace_etudiant')


@login_required
def profil_technicien(request):
    if request.method == 'POST':
        # Récupérer les données
        username = request.POST.get('username')
        first_name = request.POST.get('first_name')
        last_name = request.POST.get('last_name')
        email = request.POST.get('email')
        telephone = request.POST.get('telephone')
        new_password = request.POST.get('new_password')

        # Vérifier si le nom d'utilisateur existe déjà
        if username and username != request.user.username:
            if Utilisateur.objects.filter(username=username).exists():
                messages.error(request, 'Ce nom d\'utilisateur est déjà pris.')
                return redirect('profil_technicien')
            request.user.username = username

        # Mettre à jour les champs
        request.user.first_name = first_name
        request.user.last_name = last_name
        request.user.email = email
        request.user.telephone = telephone

        # Changer le mot de passe si fourni
        if new_password:
            if len(new_password) >= 6:
                request.user.set_password(new_password)
                messages.success(request, 'Votre mot de passe a été modifié. Veuillez vous reconnecter.')
                from django.contrib.auth import update_session_auth_hash
                update_session_auth_hash(request, request.user)
            else:
                messages.error(request, 'Le mot de passe doit contenir au moins 6 caractères.')

        request.user.save()
        messages.success(request, 'Votre profil a été mis à jour avec succès !')
        return redirect('profil_technicien')

    return render(request, 'profil_technicien.html')


@login_required
def profil_enseignant(request):
    if request.method == 'POST':
        # Récupérer les données
        username = request.POST.get('username')
        first_name = request.POST.get('first_name')
        last_name = request.POST.get('last_name')
        email = request.POST.get('email')
        telephone = request.POST.get('telephone')
        filiere = request.POST.get('filiere')
        new_password = request.POST.get('new_password')

        # Vérifier si le nom d'utilisateur existe déjà
        if username and username != request.user.username:
            if Utilisateur.objects.filter(username=username).exists():
                messages.error(request, 'Ce nom d\'utilisateur est déjà pris.')
                return redirect('profil_enseignant')
            request.user.username = username

        # Mettre à jour les champs
        request.user.first_name = first_name
        request.user.last_name = last_name
        request.user.email = email
        request.user.telephone = telephone
        request.user.filiere = filiere

        # Changer le mot de passe si fourni
        if new_password:
            if len(new_password) >= 6:
                request.user.set_password(new_password)
                from django.contrib.auth import update_session_auth_hash
                update_session_auth_hash(request, request.user)
                messages.success(request, 'Mot de passe modifié. Veuillez vous reconnecter.')
            else:
                messages.error(request, 'Le mot de passe doit contenir au moins 6 caractères.')

        request.user.save()
        messages.success(request, 'Profil mis à jour avec succès !')
        return redirect('profil_enseignant')

    return render(request, 'profil_enseignant.html')

def inscription_enseignant(request):
    """Inscription pour les enseignants"""
    if request.method == 'POST':
        first_name = request.POST.get('first_name')
        last_name = request.POST.get('last_name')
        username = request.POST.get('username')
        email = request.POST.get('email')
        password = request.POST.get('password')
        password2 = request.POST.get('password2')
        telephone = request.POST.get('telephone')
        filiere = request.POST.get('filiere')

        # Validation email universitaire
        if not re.match(r'^[a-z]+\.[a-z]+[0-9]@univ-thies\.sn$', email):
            messages.error(request, 'Format d\'email invalide. Utilisez: prenom.nom3@univ-thies.sn')
            return render(request, 'inscription_enseignant.html')

        # Validation prénom et nom
        if not first_name or not last_name:
            messages.error(request, 'Veuillez renseigner votre prénom et votre nom.')
            return render(request, 'inscription_enseignant.html')

        if password == password2:
            if not Utilisateur.objects.filter(username=username).exists():
                if not Utilisateur.objects.filter(email=email).exists():
                    utilisateur = Utilisateur.objects.create_user(
                        username=username,
                        email=email,
                        password=password,
                        first_name=first_name,
                        last_name=last_name,
                        role='enseignant',
                        telephone=telephone,
                        filiere=filiere
                    )
                    login(request, utilisateur)
                    log_action(request, 'inscription_enseignant',
                               f"Nouvel enseignant inscrit : {first_name} {last_name} ({username}) - {filiere}")
                    messages.success(request, f'Bienvenue {first_name} {last_name} ! Votre compte enseignant a été créé avec succès.')
                    return redirect('espace_enseignant')
                else:
                    messages.error(request, 'Cet email est déjà utilisé.')
            else:
                messages.error(request, 'Ce nom d\'utilisateur existe déjà.')
        else:
            messages.error(request, 'Les mots de passe ne correspondent pas.')

    return render(request, 'inscription_enseignant.html')


def connexion_enseignant(request):
    """Connexion pour les enseignants"""
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)
        if user:
            if user.role == 'enseignant' or user.is_superuser:
                login(request, user)
                log_action(request, 'connexion_enseignant',
                           f"{user.username} s'est connecté (enseignant)")
                messages.success(request, f'Bienvenue {user.first_name} {user.last_name} !')
                return redirect('espace_enseignant')
            else:
                messages.error(request, 'Vous n\'avez pas les droits enseignant.')
        else:
            messages.error(request, 'Identifiants incorrects.')
    return render(request, 'connexion_enseignant.html')
