import os
from django.core.asgi import get_asgi_application
from channels.routing import ProtocolTypeRouter, URLRouter
from channels.auth import AuthMiddlewareStack
from django.urls import path
from gestion.consumers import EmpruntConsumer

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'Gestion_emprunt_materiels_SI.settings')

application = ProtocolTypeRouter({
    'http': get_asgi_application(),
    'websocket': AuthMiddlewareStack(
        URLRouter([
            path('ws/emprunts/', EmpruntConsumer.as_asgi()),
        ])
    ),
})