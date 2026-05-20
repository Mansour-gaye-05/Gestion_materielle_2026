from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.cron import CronTrigger
from django.utils import timezone
from datetime import timedelta
import logging

logger = logging.getLogger(__name__)

def verifier_retards():
    """Marquer les demandes en retard et envoyer notifications"""
    try:
        from gestion.models import Demande, Notification
        today = timezone.now().date()
        
        # Demandes en cours dont la date de fin est depassee
        demandes_retard = Demande.objects.filter(
            statut='en_cours',
            date_fin__lt=today
        )
        for demande in demandes_retard:
            demande.statut = 'retard'
            demande.save()
            # Notifier l'etudiant
            Notification.objects.get_or_create(
                message=f"RETARD - Vous devez restituer le materiel emprunte (demande #{demande.id}). Date de retour depassee depuis le {demande.date_fin.strftime('%d/%m/%Y')}.",
                type='retard',
                demande=demande,
                defaults={'lu': False}
            )
            logger.info(f"Demande #{demande.id} marquee en retard")
        
        print(f"Retards: {demandes_retard.count()} demandes marquees")
    except Exception as e:
        logger.error(f"Erreur verifier_retards: {e}")

def envoyer_rappels():
    """Envoyer rappels 1 jour et 3 jours avant la date de retour"""
    try:
        from gestion.models import Demande, Notification
        today = timezone.now().date()
        
        # Rappel J-1
        demandes_j1 = Demande.objects.filter(
            statut='en_cours',
            date_fin=today + timedelta(days=1)
        )
        for demande in demandes_j1:
            Notification.objects.get_or_create(
                message=f"RAPPEL - Vous devez restituer le materiel de la demande #{demande.id} DEMAIN ({demande.date_fin.strftime('%d/%m/%Y')}). Presentez-vous au laboratoire.",
                type='rappel',
                demande=demande,
                defaults={'lu': False}
            )
            logger.info(f"Rappel J-1 envoye pour demande #{demande.id}")
        
        # Rappel J-3
        demandes_j3 = Demande.objects.filter(
            statut='en_cours',
            date_fin=today + timedelta(days=3)
        )
        for demande in demandes_j3:
            Notification.objects.get_or_create(
                message=f"RAPPEL - Vous devez restituer le materiel de la demande #{demande.id} dans 3 jours ({demande.date_fin.strftime('%d/%m/%Y')}).",
                type='rappel',
                demande=demande,
                defaults={'lu': False}
            )
            logger.info(f"Rappel J-3 envoye pour demande #{demande.id}")
        
        print(f"Rappels: J-1={demandes_j1.count()}, J-3={demandes_j3.count()}")
    except Exception as e:
        logger.error(f"Erreur envoyer_rappels: {e}")

def start():
    scheduler = BackgroundScheduler()
    
    # Verifier les retards toutes les heures
    scheduler.add_job(
        verifier_retards,
        trigger=CronTrigger(hour="*", minute="0"),
        id="verifier_retards",
        replace_existing=True
    )
    
    # Envoyer rappels tous les jours a 8h
    scheduler.add_job(
        envoyer_rappels,
        trigger=CronTrigger(hour="8", minute="0"),
        id="envoyer_rappels",
        replace_existing=True
    )
    
    scheduler.start()
    print("Scheduler demarre: rappels et retards actives")
    return scheduler
