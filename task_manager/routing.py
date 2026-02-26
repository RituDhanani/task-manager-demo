from django.urls import path
from chat.routing import websocket_urlpatterns as chat_ws_urls

websocket_urlpatterns = [
    *chat_ws_urls,
]