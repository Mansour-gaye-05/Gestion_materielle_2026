import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'Gestion_emprunt_materiels_SI.settings')
django.setup()

from gestion.models import Categorie, Materiel

# Créer la catégorie principale
categorie, created = Categorie.objects.get_or_create(
    libelle='Topographie et Géodésie',
    defaults={'description': 'Matériel de topographie, géodésie et géophysique'}
)

if created:
    print("✅ Catégorie créée")

# Liste complète des matériels
materiels = [
    # Stations totales
    ("Station totale non robotisée", 8, "Station totale pour mesures angulaires et distances"),
    ("Station Total CTS-112 R4", 7, "Station totale de précision pour relevés topographiques"),
    ("Station TOTAL 3", 1, "Station totale pour travaux topographiques courants"),

    # GPS / GNSS
    ("GPS différentiel i50 de précision", 4, "GPS différentiel avec accessoires complets"),
    ("Gps Différentiel i73", 5, "GPS GNSS haute précision pour relevés géodésiques"),
    ("Garmin MAPS 65 S (GPS de poche)", 20, "GPS de poche pour relevés rapides"),
    ("GPS Explorist Magellan 310", 3, "GPS de terrain pour géolocalisation"),

    # Niveaux
    ("Niveau électronique numérique", 1, "Niveau numérique de précision avec trépied et mire"),
    ("Niveau optique de précision", 9, "Niveau optique pour nivellement direct"),
    ("Niveau optique standard", 9, "Niveau optique standard pour chantier"),

    # Accessoires
    ("Trépied en aluminium", 42, "Trépied professionnel pour stations totales"),
    ("Embase + Adaptateur pour antenne GS14", 15, "Adaptateur pour fixation des antennes GPS"),
    ("Support pour prisme Leica GRT144", 2, "Support de prisme pour mesures de distance"),
    ("Prisme avec réflecteur Leica", 22, "Prisme réflecteur pour station totale"),
    ("Canne porte prisme Leica GLS 11", 2, "Canne télescopique pour prisme"),
    ("Paire de Talkie-Walkie", 6, "Communication sur le terrain"),
    ("Chargeur de batterie Leica GKL221", 10, "Chargeur pour batteries de stations totales"),
    ("Batterie externe pour récepteur GS14", 9, "Batterie supplémentaire pour GPS"),
    ("Mire télescopique en aluminium 4m", 9, "Mire graduée pour nivellement"),
    ("Tripote", 12, "Support pour trépied"),

    # Matériel géophysique
    ("Resistivimètre ADEM TERRAMETER", 1, "Appareil de mesure de résistivité électrique des sols"),
    ("Radar UNITI ESCAM + accessoires", 1, "Radar géologique pour imagerie sous-sol"),
    ("Conductivimètre EM31 MK2", 1, "Mesure de conductivité électrique du terrain"),
    ("Magnétométre MN1", 1, "Mesure du champ magnétique terrestre"),
    ("Sismograthe à 24 cannons", 1, "Appareil de sismique réflexion"),

    # Autres
    ("Vidéo-projecteurs Pack complet", 2, "Projecteur pour présentations terrains"),
]

compteur = 0
for nom, quantite, description in materiels:
    for i in range(quantite):
        # Créer un numéro de série unique
        numero_serie = f"{nom[:15].replace(' ', '_')}_{i + 1}_{hash(nom) % 10000}"

        # Vérifier si le matériel existe déjà
        if not Materiel.objects.filter(numero_serie=numero_serie).exists():
            materiel = Materiel.objects.create(
                nom=nom,
                numero_serie=numero_serie,
                categorie=categorie,
                description=description,
                etat='disponible'
            )
            compteur += 1
            print(f"✅ {nom} #{i + 1}")

print(f"\n🎉 {compteur} matériels importés !")
print(f"📊 Total dans la base: {Materiel.objects.count()} matériels")