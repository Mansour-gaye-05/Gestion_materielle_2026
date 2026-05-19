import json
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async
from django.utils import timezone
from datetime import timedelta
from django.db.models import Count
from django.db.models.functions import TruncDate
from .models import Demande


class EmpruntConsumer(AsyncWebsocketConsumer):
    async def connecte(self):
        await self.channel_layer.group_add("emprunts_group", self.channel_name)
        await self.accept()

    async def disconnecte(self, close_code):
        await self.channel_layer.group_discard("emprunts_group", self.channel_name)

    async def receive(self, text_data):
        pass

    async def emprunt_update(self, event):
        # Envoyer les données mises à jour
        data = await self.get_donnees_emprunts()
        await self.send(text_data=json.dumps(data))

    @database_sync_to_async
    def get_donnees_emprunts(self):
        aujourdhui = timezone.now().date()
        date_debut_30 = aujourdhui - timedelta(days=29)

        # Données des 30 derniers jours
        emprunts_par_jour = (
            Demande.objects
            .filter(statut__in=['approuvee', 'en_cours'], date_validation__isnull=False)
            .annotate(jour=TruncDate('date_validation'))
            .values('jour')
            .annotate(total=Count('id'))
            .order_by('jour')
        )

        jours_labels = []
        emprunts_valides = []

        for i in range(29, -1, -1):
            date_jour = aujourdhui - timedelta(days=i)
            jours_labels.append(date_jour.strftime('%d/%m'))

            valide = 0
            for e in emprunts_par_jour:
                if e['jour'] == date_jour:
                    valide = e['total']
                    break
            emprunts_valides.append(valide)

        return {
            'labels': jours_labels,
            'data': emprunts_valides,
            'total': sum(emprunts_valides)
        }