from django.apps import AppConfig

class GestionConfig(AppConfig):
    name = 'gestion'

    def ready(self):
        import os
        if os.environ.get('RUN_MAIN') != 'true':
            return
        try:
            from gestion import scheduler
            scheduler.start()
        except Exception as e:
            print(f"Erreur scheduler: {e}")
