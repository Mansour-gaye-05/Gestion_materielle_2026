from django.core.management.base import BaseCommand
from django.utils import timezone
from gestion.models import Demande


class Command(BaseCommand):
    help = 'Vérifie et met à jour les demandes en retard'

    def handle(self, *args, **options):
        aujourdhui = timezone.now().date()

        demandes_en_retard = Demande.objects.filter(
            statut='en_cours',
            date_fin__lt=aujourdhui
        )

        count = demandes_en_retard.count()

        for demande in demandes_en_retard:
            demande.statut = 'retard'
            demande.save()
            self.stdout.write(f"✅ Demande #{demande.id} marquée en retard")

        self.stdout.write(self.style.SUCCESS(f"{count} demande(s) marquée(s) en retard"))