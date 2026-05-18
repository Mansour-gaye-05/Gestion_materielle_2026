with open('gestion/views.py', 'r', encoding='utf-8') as f:
    content = f.read()

bon_sortie = '''

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
    p.drawString(40, height - 40, "UFR Sciences de l\'Ingenieur")
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
    p.drawString(40, y, f"Nom d\'utilisateur : {demande.utilisateur.username}")
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
    p.drawString(40, y, "DETAILS DE L\'EMPRUNT")
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
        p.drawString(40, y, f"Lieu d\'utilisation : {emplacement.adresse}")
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
    p.drawCentredString(width / 2, 30, f"Document genere le {timezone.now().strftime('%d/%m/%Y a %H:%M')} - UFR Sciences de l\'Ingenieur, Universite de Thies")

    p.save()
    return response
'''

content += bon_sortie

with open("gestion/views.py", "w", encoding="utf-8") as f:
    f.write(content)
print("Bon de sortie ajoute!")
