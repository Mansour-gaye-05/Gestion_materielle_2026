"""
Génération automatique de documents PDF — UFR Sciences de l'Ingénieur
  - Fiche d'emprunt
  - Reçu de restitution
  - Bon de sortie
Chaque document inclut une zone de signature.
"""

from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.lib.units import mm
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, HRFlowable
)
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT
from reportlab.pdfgen import canvas
from io import BytesIO
import datetime

W, H = A4
PRIMARY   = colors.HexColor('#2c3e50')
ACCENT    = colors.HexColor('#2980b9')
LIGHT     = colors.HexColor('#ecf0f1')
SUCCESS   = colors.HexColor('#27ae60')
DANGER    = colors.HexColor('#e74c3c')
GRAY      = colors.HexColor('#95a5a6')
WHITE     = colors.white

# ─── Styles ────────────────────────────────────────────────────────────────

def _styles():
    s = getSampleStyleSheet()
    base = dict(fontName='Helvetica', leading=14)
    styles = {
        'title':    ParagraphStyle('title',    fontSize=16, fontName='Helvetica-Bold',
                                   textColor=PRIMARY, alignment=TA_CENTER, spaceAfter=4),
        'subtitle': ParagraphStyle('subtitle', fontSize=11, fontName='Helvetica',
                                   textColor=ACCENT,  alignment=TA_CENTER, spaceAfter=2),
        'ref':      ParagraphStyle('ref',      fontSize=9,  fontName='Helvetica',
                                   textColor=GRAY,    alignment=TA_CENTER, spaceAfter=8),
        'label':    ParagraphStyle('label',    fontSize=9,  fontName='Helvetica-Bold',
                                   textColor=PRIMARY),
        'value':    ParagraphStyle('value',    fontSize=9,  fontName='Helvetica',
                                   textColor=colors.black),
        'section':  ParagraphStyle('section',  fontSize=10, fontName='Helvetica-Bold',
                                   textColor=WHITE,   backColor=PRIMARY,
                                   leftIndent=6, spaceBefore=10, spaceAfter=4),
        'small':    ParagraphStyle('small',    fontSize=8,  fontName='Helvetica',
                                   textColor=GRAY,    alignment=TA_CENTER),
        'normal':   ParagraphStyle('normal',   fontSize=9,  fontName='Helvetica',
                                   textColor=colors.black),
    }
    return styles

# ─── En-tête commun ─────────────────────────────────────────────────────────

def _header(c, doc, titre, sous_titre, ref, couleur=PRIMARY):
    c.saveState()
    # Bandeau haut
    c.setFillColor(couleur)
    c.rect(0, H - 28*mm, W, 28*mm, fill=1, stroke=0)
    # Texte institution
    c.setFillColor(WHITE)
    c.setFont('Helvetica-Bold', 13)
    c.drawString(15*mm, H - 12*mm, 'UFR Sciences de l\'Ingénieur — Université de Thiès')
    c.setFont('Helvetica', 9)
    c.drawString(15*mm, H - 18*mm, 'Laboratoire de Matériel Topographique')
    # Titre doc (droite)
    c.setFont('Helvetica-Bold', 11)
    c.drawRightString(W - 15*mm, H - 12*mm, titre)
    c.setFont('Helvetica', 9)
    c.drawRightString(W - 15*mm, H - 18*mm, sous_titre)
    # Ref
    c.setFillColor(LIGHT)
    c.rect(0, H - 34*mm, W, 6*mm, fill=1, stroke=0)
    c.setFillColor(PRIMARY)
    c.setFont('Helvetica', 8)
    c.drawString(15*mm, H - 31*mm, ref)
    c.drawRightString(W - 15*mm, H - 31*mm,
                      'Généré le : ' + datetime.datetime.now().strftime('%d/%m/%Y à %H:%M'))
    c.restoreState()

def _footer(c, doc):
    c.saveState()
    c.setFillColor(LIGHT)
    c.rect(0, 0, W, 12*mm, fill=1, stroke=0)
    c.setFillColor(GRAY)
    c.setFont('Helvetica', 7)
    c.drawCentredString(W/2, 5*mm,
        'Document généré automatiquement — Système de Gestion des Emprunts — UFR Sciences')
    c.restoreState()

# ─── Zone de signature ───────────────────────────────────────────────────────

def _signature_table(signataires):
    """
    signataires : liste de dicts {label, nom, date}
    Ex: [{'label':'Étudiant','nom':'Alpha Diallo','date':'12/05/2026'}, ...]
    """
    col_w = (W - 30*mm) / len(signataires)
    data = []
    # Ligne "vu et approuvé"
    data.append([Paragraph('<i>Lu et approuvé</i>',
                 ParagraphStyle('si', fontSize=8, fontName='Helvetica',
                                textColor=GRAY, alignment=TA_CENTER))
                 ] * len(signataires))
    # Espace signature
    data.append([Spacer(1, 18*mm)] * len(signataires))
    # Noms
    row_label, row_nom, row_date = [], [], []
    for s in signataires:
        row_label.append(Paragraph(f'<b>{s["label"]}</b>',
            ParagraphStyle('sl', fontSize=9, fontName='Helvetica-Bold',
                           textColor=PRIMARY, alignment=TA_CENTER)))
        row_nom.append(Paragraph(s.get('nom',''),
            ParagraphStyle('sn', fontSize=8, fontName='Helvetica',
                           textColor=colors.black, alignment=TA_CENTER)))
        row_date.append(Paragraph('Date : ' + s.get('date','__________'),
            ParagraphStyle('sd', fontSize=8, fontName='Helvetica',
                           textColor=GRAY, alignment=TA_CENTER)))
    data += [row_label, row_nom, row_date]

    t = Table(data, colWidths=[col_w]*len(signataires))
    t.setStyle(TableStyle([
        ('BOX',         (0,0), (-1,-1), 0.5, GRAY),
        ('INNERGRID',   (0,0), (-1,-1), 0.3, LIGHT),
        ('BACKGROUND',  (0,0), (-1, 0), LIGHT),
        ('LINEBELOW',   (0,1), (-1,1),  1,   GRAY),
        ('TOPPADDING',  (0,0), (-1,-1), 4),
        ('BOTTOMPADDING',(0,0),(-1,-1), 4),
        ('VALIGN',      (0,0), (-1,-1), 'MIDDLE'),
    ]))
    return t

# ─── Tableau info ────────────────────────────────────────────────────────────

def _info_table(rows, col_widths=None):
    """rows : liste de (label, valeur)"""
    st = _styles()
    data = [[Paragraph(lbl, st['label']), Paragraph(val, st['value'])]
            for lbl, val in rows]
    cw = col_widths or [50*mm, W - 30*mm - 50*mm]
    t = Table(data, colWidths=cw)
    t.setStyle(TableStyle([
        ('BACKGROUND',   (0,0), (0,-1), LIGHT),
        ('GRID',         (0,0), (-1,-1), 0.3, GRAY),
        ('TOPPADDING',   (0,0), (-1,-1), 5),
        ('BOTTOMPADDING',(0,0), (-1,-1), 5),
        ('LEFTPADDING',  (0,0), (-1,-1), 8),
    ]))
    return t

# ═══════════════════════════════════════════════════════════════════════════
# 1. FICHE D'EMPRUNT
# ═══════════════════════════════════════════════════════════════════════════

def generer_fiche_emprunt(demande):
    """
    Retourne un BytesIO contenant le PDF de la fiche d'emprunt.
    `demande` : instance Django du modèle Demande
    """
    buf = BytesIO()
    st  = _styles()

    ref = f'Réf. EMPRUNT-{demande.id:04d} | {demande.date_demande.strftime("%d/%m/%Y")}'

    def on_page(c, doc):
        _header(c, doc, 'FICHE D\'EMPRUNT', 'Matériel Topographique', ref, PRIMARY)
        _footer(c, doc)

    doc = SimpleDocTemplate(buf, pagesize=A4,
                            topMargin=40*mm, bottomMargin=18*mm,
                            leftMargin=15*mm, rightMargin=15*mm)

    story = []

    # Section étudiant
    story.append(Paragraph('■  INFORMATIONS ÉTUDIANT', st['section']))
    story.append(_info_table([
        ('Nom d\'utilisateur', demande.utilisateur.username),
        ('Nom complet',        demande.utilisateur.get_full_name() or '—'),
        ('Email',              demande.utilisateur.email or '—'),
    ]))
    story.append(Spacer(1, 6))

    # Section demande
    story.append(Paragraph('■  DÉTAILS DE LA DEMANDE', st['section']))
    story.append(_info_table([
        ('N° de demande',  f'#{demande.id}'),
        ('Date de demande',demande.date_demande.strftime('%d/%m/%Y')),
        ('Date de début',  demande.date_debut.strftime('%d/%m/%Y')),
        ('Date de fin',    demande.date_fin.strftime('%d/%m/%Y')),
        ('Statut',         demande.get_statut_display()),
        ('Localisation',   getattr(demande, 'localisation', '—') or '—'),
        ('Motif',          getattr(demande, 'motif', '—') or '—'),
    ]))
    story.append(Spacer(1, 6))

    # Section matériels
    story.append(Paragraph('■  MATÉRIELS EMPRUNTÉS', st['section']))
    lignes = demande.lignes.all()
    mat_data = [['#', 'Matériel', 'N° Série', 'Catégorie', 'État']]
    for i, l in enumerate(lignes, 1):
        mat_data.append([
            str(i),
            l.materiel.nom,
            getattr(l.materiel, 'numero_serie', '—') or '—',
            l.materiel.categorie.libelle if l.materiel.categorie else '—',
            l.materiel.get_etat_display() if hasattr(l.materiel, 'get_etat_display') else l.materiel.etat,
        ])

    t = Table(mat_data, colWidths=[8*mm, 60*mm, 40*mm, 40*mm, 30*mm])
    t.setStyle(TableStyle([
        ('BACKGROUND',   (0,0), (-1,0),  PRIMARY),
        ('TEXTCOLOR',    (0,0), (-1,0),  WHITE),
        ('FONTNAME',     (0,0), (-1,0),  'Helvetica-Bold'),
        ('FONTSIZE',     (0,0), (-1,-1), 8),
        ('GRID',         (0,0), (-1,-1), 0.3, GRAY),
        ('ROWBACKGROUNDS',(0,1),(-1,-1), [WHITE, LIGHT]),
        ('TOPPADDING',   (0,0), (-1,-1), 5),
        ('BOTTOMPADDING',(0,0), (-1,-1), 5),
        ('LEFTPADDING',  (0,0), (-1,-1), 6),
        ('ALIGN',        (0,0), (0,-1),  'CENTER'),
    ]))
    story.append(t)
    story.append(Spacer(1, 10))

    # Conditions
    story.append(Paragraph('■  CONDITIONS D\'EMPRUNT', st['section']))
    cond = [
        '1. L\'étudiant s\'engage à restituer le matériel en bon état à la date prévue.',
        '2. Tout dommage ou perte sera signalé immédiatement au responsable du laboratoire.',
        '3. Le matériel ne peut être prêté à un tiers sans autorisation.',
        '4. En cas de panne, l\'étudiant doit signaler via l\'application avant toute intervention.',
    ]
    for c in cond:
        story.append(Paragraph(c, st['normal']))
    story.append(Spacer(1, 10))

    # Signatures
    story.append(Paragraph('■  SIGNATURES', st['section']))
    story.append(Spacer(1, 4))
    story.append(_signature_table([
        {'label': 'Étudiant emprunteur',
         'nom':   demande.utilisateur.get_full_name() or demande.utilisateur.username,
         'date':  demande.date_debut.strftime('%d/%m/%Y')},
        {'label': 'Responsable laboratoire', 'nom': '', 'date': ''},
        {'label': 'Chef de département',     'nom': '', 'date': ''},
    ]))

    doc.build(story, onFirstPage=on_page, onLaterPages=on_page)
    buf.seek(0)
    return buf

# ═══════════════════════════════════════════════════════════════════════════
# 2. REÇU DE RESTITUTION
# ═══════════════════════════════════════════════════════════════════════════

def generer_recu_restitution(demande, restitution=None):
    """
    Retourne un BytesIO contenant le PDF du reçu de restitution.
    `restitution` : instance optionnelle du modèle Restitution
    """
    buf = BytesIO()
    st  = _styles()

    ref = f'Réf. RESTITUTION-{demande.id:04d}'

    def on_page(c, doc):
        _header(c, doc, 'REÇU DE RESTITUTION', 'Matériel Topographique', ref, SUCCESS)
        _footer(c, doc)

    doc = SimpleDocTemplate(buf, pagesize=A4,
                            topMargin=40*mm, bottomMargin=18*mm,
                            leftMargin=15*mm, rightMargin=15*mm)
    story = []

    # Bannière de confirmation
    confirm_style = ParagraphStyle('confirm', fontSize=12, fontName='Helvetica-Bold',
                                   textColor=SUCCESS, alignment=TA_CENTER,
                                   borderColor=SUCCESS, borderWidth=1,
                                   borderPadding=8, backColor=colors.HexColor('#eafaf1'))
    story.append(Paragraph('✔  MATÉRIEL RESTITUÉ AVEC SUCCÈS', confirm_style))
    story.append(Spacer(1, 8))

    # Infos restitution
    story.append(Paragraph('■  INFORMATIONS DE RESTITUTION', st['section']))
    date_restitution = (restitution.date_restitution.strftime('%d/%m/%Y %H:%M')
                        if restitution and hasattr(restitution, 'date_restitution')
                        else datetime.datetime.now().strftime('%d/%m/%Y %H:%M'))
    etat_mat = (restitution.etat_materiel if restitution else '—')
    obs       = (restitution.observations  if restitution else '—')

    story.append(_info_table([
        ('N° de demande',      f'#{demande.id}'),
        ('Étudiant',           demande.utilisateur.get_full_name() or demande.utilisateur.username),
        ('Date d\'emprunt',    demande.date_debut.strftime('%d/%m/%Y')),
        ('Date de retour prévue', demande.date_fin.strftime('%d/%m/%Y')),
        ('Date de restitution', date_restitution),
        ('État du matériel',   etat_mat),
        ('Observations',       obs),
    ]))
    story.append(Spacer(1, 6))

    # Matériels restitués
    story.append(Paragraph('■  MATÉRIELS RESTITUÉS', st['section']))
    lignes = demande.lignes.all()
    mat_data = [['#', 'Matériel', 'N° Série', 'État au retour', 'Conforme']]
    for i, l in enumerate(lignes, 1):
        mat_data.append([
            str(i),
            l.materiel.nom,
            getattr(l.materiel, 'numero_serie', '—') or '—',
            etat_mat,
            '✔ Oui',
        ])
    t = Table(mat_data, colWidths=[8*mm, 60*mm, 40*mm, 40*mm, 25*mm])
    t.setStyle(TableStyle([
        ('BACKGROUND',    (0,0), (-1,0),  SUCCESS),
        ('TEXTCOLOR',     (0,0), (-1,0),  WHITE),
        ('FONTNAME',      (0,0), (-1,0),  'Helvetica-Bold'),
        ('FONTSIZE',      (0,0), (-1,-1), 8),
        ('GRID',          (0,0), (-1,-1), 0.3, GRAY),
        ('ROWBACKGROUNDS',(0,1), (-1,-1), [WHITE, colors.HexColor('#eafaf1')]),
        ('TOPPADDING',    (0,0), (-1,-1), 5),
        ('BOTTOMPADDING', (0,0), (-1,-1), 5),
        ('LEFTPADDING',   (0,0), (-1,-1), 6),
        ('ALIGN',         (-1,1),(-1,-1), 'CENTER'),
        ('TEXTCOLOR',     (-1,1),(-1,-1), SUCCESS),
        ('FONTNAME',      (-1,1),(-1,-1), 'Helvetica-Bold'),
    ]))
    story.append(t)
    story.append(Spacer(1, 10))

    # Signatures
    story.append(Paragraph('■  SIGNATURES DE RÉCEPTION', st['section']))
    story.append(Spacer(1, 4))
    story.append(_signature_table([
        {'label': 'Étudiant restituant',
         'nom':   demande.utilisateur.get_full_name() or demande.utilisateur.username,
         'date':  date_restitution},
        {'label': 'Réceptionnaire laboratoire', 'nom': '', 'date': ''},
    ]))

    doc.build(story, onFirstPage=on_page, onLaterPages=on_page)
    buf.seek(0)
    return buf

# ═══════════════════════════════════════════════════════════════════════════
# 3. BON DE SORTIE
# ═══════════════════════════════════════════════════════════════════════════

def generer_bon_sortie(demande):
    """
    Retourne un BytesIO contenant le PDF du bon de sortie.
    Document officiel autorisant la sortie du matériel du laboratoire.
    """
    buf = BytesIO()
    st  = _styles()

    ref = f'BS-{demande.id:04d}-{demande.date_debut.strftime("%Y%m%d")}'

    def on_page(c, doc):
        _header(c, doc, 'BON DE SORTIE', 'Autorisation de Sortie Matériel', ref, ACCENT)
        _footer(c, doc)

    doc = SimpleDocTemplate(buf, pagesize=A4,
                            topMargin=40*mm, bottomMargin=18*mm,
                            leftMargin=15*mm, rightMargin=15*mm)
    story = []

    # Numéro BS bien visible
    num_style = ParagraphStyle('num', fontSize=22, fontName='Helvetica-Bold',
                               textColor=ACCENT, alignment=TA_CENTER, spaceAfter=4)
    story.append(Paragraph(f'N° {ref}', num_style))
    story.append(Paragraph('BON DE SORTIE DE MATÉRIEL TOPOGRAPHIQUE',
                 ParagraphStyle('bst', fontSize=11, fontName='Helvetica-Bold',
                                textColor=PRIMARY, alignment=TA_CENTER, spaceAfter=2)))
    story.append(HRFlowable(width='100%', thickness=1, color=ACCENT, spaceAfter=10))

    # Bénéficiaire
    story.append(Paragraph('■  BÉNÉFICIAIRE', st['section']))
    story.append(_info_table([
        ('Nom d\'utilisateur', demande.utilisateur.username),
        ('Nom complet',        demande.utilisateur.get_full_name() or '—'),
        ('Email',              demande.utilisateur.email or '—'),
    ]))
    story.append(Spacer(1, 6))

    # Détails sortie
    story.append(Paragraph('■  DÉTAILS DE LA SORTIE', st['section']))
    story.append(_info_table([
        ('N° de demande',       f'#{demande.id}'),
        ('Date de sortie',      demande.date_debut.strftime('%d/%m/%Y')),
        ('Date de retour',      demande.date_fin.strftime('%d/%m/%Y')),
        ('Destination / Site',  getattr(demande, 'localisation', '—') or '—'),
        ('Objet de la mission', getattr(demande, 'motif', '—') or '—'),
    ]))
    story.append(Spacer(1, 6))

    # Liste matériels
    story.append(Paragraph('■  LISTE DES MATÉRIELS AUTORISÉS À SORTIR', st['section']))
    lignes = demande.lignes.all()
    mat_data = [['#', 'Désignation', 'N° Série', 'Catégorie', 'Qté', 'État départ']]
    for i, l in enumerate(lignes, 1):
        mat_data.append([
            str(i),
            l.materiel.nom,
            getattr(l.materiel, 'numero_serie', '—') or '—',
            l.materiel.categorie.libelle if l.materiel.categorie else '—',
            '1',
            l.materiel.get_etat_display() if hasattr(l.materiel, 'get_etat_display') else l.materiel.etat,
        ])

    t = Table(mat_data, colWidths=[8*mm, 55*mm, 38*mm, 35*mm, 12*mm, 25*mm])
    t.setStyle(TableStyle([
        ('BACKGROUND',    (0,0), (-1,0),  ACCENT),
        ('TEXTCOLOR',     (0,0), (-1,0),  WHITE),
        ('FONTNAME',      (0,0), (-1,0),  'Helvetica-Bold'),
        ('FONTSIZE',      (0,0), (-1,-1), 8),
        ('GRID',          (0,0), (-1,-1), 0.3, GRAY),
        ('ROWBACKGROUNDS',(0,1), (-1,-1), [WHITE, colors.HexColor('#eaf4fb')]),
        ('TOPPADDING',    (0,0), (-1,-1), 5),
        ('BOTTOMPADDING', (0,0), (-1,-1), 5),
        ('LEFTPADDING',   (0,0), (-1,-1), 6),
        ('ALIGN',         (4,0), (4,-1),  'CENTER'),
    ]))
    story.append(t)
    story.append(Spacer(1, 6))

    # Avertissement
    warn_style = ParagraphStyle('warn', fontSize=8, fontName='Helvetica',
                                textColor=DANGER, alignment=TA_CENTER,
                                backColor=colors.HexColor('#fdf2f2'),
                                borderColor=DANGER, borderWidth=0.5,
                                borderPadding=6)
    story.append(Paragraph(
        '⚠  Ce bon de sortie doit être présenté à la sortie du laboratoire. '
        'Tout matériel sorti sans bon sera signalé aux autorités compétentes.',
        warn_style))
    story.append(Spacer(1, 10))

    # Signatures
    story.append(Paragraph('■  AUTORISATIONS ET SIGNATURES', st['section']))
    story.append(Spacer(1, 4))
    story.append(_signature_table([
        {'label': 'Demandeur',
         'nom':   demande.utilisateur.get_full_name() or demande.utilisateur.username,
         'date':  demande.date_debut.strftime('%d/%m/%Y')},
        {'label': 'Responsable laboratoire', 'nom': '', 'date': ''},
        {'label': 'Autorisation sortie',     'nom': '', 'date': ''},
    ]))

    doc.build(story, onFirstPage=on_page, onLaterPages=on_page)
    buf.seek(0)
    return buf