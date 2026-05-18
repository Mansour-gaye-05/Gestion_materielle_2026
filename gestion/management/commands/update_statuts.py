from django.core.management.base import BaseCommand
from django.utils import timezone
from gestion.models import Demande


class Command(BaseCommand):
    help = 'Met à jour automatiquement les statuts des demandes (approuvée → en cours → retard)'

    def handle(self, *args, **options):
        aujourdhui = timezone.now().date()

        self.stdout.write("=" * 50)
        self.stdout.write("🔄 MISE À JOUR DES STATUTS DES DEMANDES")
        self.stdout.write("=" * 50)

        compteur_approuvees = 0
        compteur_retard = 0

        # 1. Approuvées → En cours (quand la date de début est atteinte)
        demandes_approuvees = Demande.objects.filter(statut='approuvee', date_debut__lte=aujourdhui)
        for demande in demandes_approuvees:
            demande.statut = 'en_cours'
            demande.save()
            compteur_approuvees += 1
            self.stdout.write(f"✅ Demande #{demande.id} : approuvée → en_cours (début: {demande.date_debut})")

        # 2. En cours → Retard (quand la date de fin est dépassée)
        demandes_retard = Demande.objects.filter(statut='en_cours', date_fin__lt=aujourdhui)
        for demande in demandes_retard:
            demande.statut = 'retard'
            demande.save()
            compteur_retard += 1
            self.stdout.write(f"⚠️ Demande #{demande.id} : en_cours → retard (fin prévue: {demande.date_fin})")

        # Résumé
        self.stdout.write("=" * 50)
        if compteur_approuvees == 0 and compteur_retard == 0:
            self.stdout.write(self.style.SUCCESS("📊 Aucune mise à jour nécessaire"))
        else:
            self.stdout.write(self.style.SUCCESS(
                f"📊 Résumé: {compteur_approuvees} demandes → en_cours, {compteur_retard} demandes → retard"))
        self.stdout.write("=" * 50)