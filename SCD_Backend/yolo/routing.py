from channels.routing import ProtocolTypeRouter, URLRouter 
from django.urls import path 
from django.core.asgi import get_asgi_application
from channels.auth import AuthMiddlewareStack
from yolo.consumers import MyConsumer

application = ProtocolTypeRouter({
    'http': get_asgi_application(), 
    'websocket': AuthMiddlewareStack(
        URLRouter([ 
            path('ws-api/inferImage', MyConsumer.as_asgi()), 
        ])
    ), 
}) 