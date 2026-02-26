from django.urls import path
from chat.routing import websocket_urlpatterns as chat_websockets_urls

websocket_urlpatterns = [
    *chat_websockets_urls,
]