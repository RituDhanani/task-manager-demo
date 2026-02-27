import os
from django.core.asgi import get_asgi_application
from channels.routing import ProtocolTypeRouter, URLRouter

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "task_manager.settings")

django_asgi_app = get_asgi_application()

import task_manager.routing
from chat.middleware import JWTAuthMiddleware 
application = ProtocolTypeRouter(
    {
        "http": django_asgi_app,
        "websocket": JWTAuthMiddleware(
            URLRouter(task_manager.routing.websocket_urlpatterns)
        ),
    }
)