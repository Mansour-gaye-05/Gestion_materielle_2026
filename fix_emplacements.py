from gestion.models import Emplacement, Demande
from django.utils import timezone

# Supprimer tous les emplacements sans coordonn?es valides
Emplacement.objects.filter(
    Q(latitude__isnull=True) | 
    Q(longitude__isnull=True) | 
    Q(latitude=0) | 
    Q(longitude=0)
).delete()

print("Anciens emplacements nettoy?s")

# Mettre ? jour les demandes en retard
demandes_retard = Demande.objects.filter(
    statut='en_cours',
    date_fin__lt=timezone.now().date()
)
count = demandes_retard.update(statut='retard')
print(f"{count} demandes marqu?es en retard")
