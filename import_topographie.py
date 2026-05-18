import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'Gestion_emprunt_materiels_SI.settings')
django.setup()

from gestion.models import Categorie, Materiel

# 1. Supprimer tous les matériels existants
print("🗑️ Suppression des anciens matériels...")
Materiel.objects.all().delete()
print("✅ Anciens matériels supprimés")

# 2. Supprimer les anciennes catégories
Categorie.objects.all().delete()
print("✅ Anciennes catégories supprimées")

# 3. Créer la nouvelle catégorie
categorie, created = Categorie.objects.get_or_create(
    libelle='Topographie et Géodésie',
    defaults={'description': 'Matériel de topographie, géodésie et accessoires'}
)
print(f"✅ Catégorie '{categorie.libelle}' créée")

# Liste des matériels (nom, quantite_totale, description, etat)
materiels = [
    # GPS / GNSS
    ("GPS différentiel i50 de précision", 4, "GPS différentiel avec accessoires complets, précision centimétrique",
     "disponible"),
    ("Gps Différentiel i73", 5, "GPS GNSS haute précision pour relevés géodésiques", "disponible"),
    ("Garmin MAPS 65 S (GPS de poche)", 20, "GPS de poche pour relevés rapides et navigation", "disponible"),

    # Stations totales
    ("Station totale non robotisée", 8, "Station totale pour mesures angulaires et distances", "disponible"),
    ("Station Total CTS-112 R4", 7, "Station totale de précision pour relevés topographiques", "disponible"),

    # Niveaux
    ("Niveau électronique numérique", 1, "Niveau numérique de précision avec trépied et mire code barre",
     "maintenance"),  # en panne
    ("Niveau optique de précision", 9, "Niveau optique pour nivellement direct", "maintenance"),  # 1 EN PANNE

    # Accessoires
    ("Trépied en aluminium", 42, "Trépied professionnel pour stations totales et niveaux", "disponible"),
    ("Embase + Adaptateur pour antenne GS14", 15, "Adaptateur pour fixation des antennes GPS", "disponible"),
    ("Support pour prisme Leica GRT144", 2, "Support de prisme pour mesures de distance", "disponible"),
    ("Prisme avec réflecteur Leica", 22, "Prisme réflecteur pour station totale", "disponible"),
    ("Canne porte prisme Leica GLS 11", 2, "Canne télescopique pour prisme", "disponible"),
    ("Paire de Talkie-Walkie", 6, "Communication sur le terrain", "maintenance"),  # dont 4 gaté
    ("Chargeur de batterie Leica GKL221", 10, "Chargeur pour batteries de stations totales", "disponible"),
    ("Batterie externe pour récepteur GS14", 9, "Batterie supplémentaire pour GPS", "disponible"),
    ("Mire télescopique aluminium 4m", 9, "Mire graduée pour nivellement", "disponible"),
    ("Tripote", 12, "Support pour trépied", "maintenance"),  # 1 gaté
    ("Chargeur de Batterie externe", 7, "Chargeur pour batteries externes", "disponible"),
    ("Batterie Interne pour station totale Leica", 2, "Batterie interne pour station totale", "disponible"),

    # Mobilier de laboratoire
    ("Armoire Métallique", 4, "Armoire de rangement pour matériel", "disponible"),
    ("Tables étudiants", 12, "Tables pour travaux pratiques", "disponible"),
    ("Tables en bois", 4, "Tables pour bureau", "disponible"),
    ("Chaises pipitres en noir", 74, "Chaises pour amphithéâtre", "disponible"),
    ("Coffre fort", 1, "Coffre pour matériel de valeur", "disponible"),

    # Électronique
    ("Ordinateur fixe lenovo", 48, "Ordinateur pour traitement de données", "disponible"),
    ("Ordinateur Portable HP Core i5", 4, "Ordinateur portable pour terrain", "disponible"),
    ("Ordinateur portable HP OMEN Core i7", 3, "Ordinateur haute performance", "disponible"),
    ("Tablettes Galaxy + accessoires", 50, "Tablettes pour relevés terrain", "disponible"),
    ("Imprimante multifonction", 1, "Impression de rapports", "disponible"),
    ("Imprimante grand format A0", 1, "Impression de plans", "disponible"),

    # Divers
    ("Casques de protection", 300, "Casques de protection pour chantier", "maintenance"),  # à vérifier
    ("Rideaux", 1, "Rideaux pour laboratoire", "disponible"),
    ("Sonde", 1, "Sonde de mesure", "disponible"),
    ("Bouteille de gaz 12kg", 1, "Gaz pour laboratoire", "disponible"),
    ("Câble HDMI", 1, "Câble pour vidéoprojecteur", "disponible"),
    ("Antivirus Kaspersky", 20, "Licences antivirus", "disponible"),
]

compteur = 0
for nom, quantite_totale, description, etat in materiels:
    obj = Materiel.objects.create(
        nom=nom,
        numero_serie=f"{nom[:20].replace(' ', '_')}_{compteur + 1}",
        categorie=categorie,
        description=description,
        etat=etat,
        quantite_totale=quantite_totale,
        quantite_disponible=quantite_totale if etat == 'disponible' else 0
    )
    compteur += 1
    print(f"✅ {nom} (x{quantite_totale}) - État: {etat}")

print(f"\n🎉 {compteur} matériels importés !")
print(f"📊 Total dans la base: {Materiel.objects.count()} matériels")