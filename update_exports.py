with open('gestion/views.py', 'r', encoding='utf-8') as f:
    content = f.read()

old_exports = '''# ==================== EXPORT PDF/EXCEL ====================

@staff_member_required
def export_statistiques_excel(request):
    data = {
        'Cat\u00e9gorie': [cat.libelle for cat in Categorie.objects.all()],
        'Nombre de mat\u00e9riels': [cat.materiels.count() for cat in Categorie.objects.all()],
    }
    df = pd.DataFrame(data)

    output = BytesIO()
    with pd.ExcelWriter(output, engine='openpyxl') as writer:
        df.to_excel(writer, sheet_name='Statistiques', index=False)
        materiels_data = list(Materiel.objects.values('nom', 'categorie__libelle', 'etat', 'numero_serie'))
        df_materiels = pd.DataFrame(materiels_data)
        df_materiels.to_excel(writer, sheet_name='Mat\u00e9riels', index=False)

    output.seek(0)
    response = HttpResponse(output, content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
    response['Content-Disposition'] = 'attachment; filename=statistiques_materiels.xlsx'
    return response


@staff_member_required
def export_rapport_pdf(request):
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = 'attachment; filename=rapport_materiels.pdf'

    p = canvas.Canvas(response, pagesize=A4)
    width, height = A4

    p.setFont("Helvetica-Bold", 16)
    p.drawString(50, height - 50, "Rapport d'inventaire - UFR Sciences de l'Ing\u00e9nieur")
    p.setFont("Helvetica", 10)
    p.drawString(50, height - 70, f"G\u00e9n\u00e9r\u00e9 le: {timezone.now().strftime('%d/%m/%Y %H:%M')}")

    y = height - 110
    p.setFont("Helvetica-Bold", 12)
    p.drawString(50, y, "Statistiques g\u00e9n\u00e9rales:")
    y -= 25

    p.setFont("Helvetica", 10)
    p.drawString(50, y, f"Total mat\u00e9riels: {Materiel.objects.count()}")
    y -= 20
    p.drawString(50, y, f"Mat\u00e9riels disponibles: {Materiel.objects.filter(etat='disponible').count()}")
    y -= 20
    p.drawString(50, y, f"Mat\u00e9riels emprunt\u00e9s: {Materiel.objects.filter(etat='emprunte').count()}")
    y -= 20
    p.drawString(50, y, f"Mat\u00e9riels en maintenance: {Materiel.objects.filter(etat='maintenance').count()}")
    y -= 20
    p.drawString(50, y, f"Total cat\u00e9gories: {Categorie.objects.count()}")
    y -= 20
    p.drawString(50, y, f"Total utilisateurs: {Utilisateur.objects.count()}")

    p.save()
    return response'''

new_exports = '''# ==================== EXPORT PDF/EXCEL ====================

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
    return response'''

if old_exports in content:
    content = content.replace(old_exports, new_exports)
    print('Exports remplaces!')
else:
    print('Pattern non trouve - remplacement par position')
    import re
    content = re.sub(
        r'# ==================== EXPORT PDF/EXCEL ====================.*?# ==================== CARTOGRAPHIE ====================',
        new_exports + '\n\n\n# ==================== CARTOGRAPHIE ====================',
        content,
        flags=re.DOTALL
    )
    print('Remplacement par regex effectue!')

with open('gestion/views.py', 'w', encoding='utf-8') as f:
    f.write(content)
print('views.py mis a jour!')
