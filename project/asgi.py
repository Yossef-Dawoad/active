import os
from channels.auth import AuthMiddlewareStack
from channels.routing import ProtocolTypeRouter, URLRouter #? NEW
from django.core.asgi import get_asgi_application  #? NEW
import pages.routing 
import toggle.routing

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'project.settings')


#? NEW
application = ProtocolTypeRouter({
    "http": get_asgi_application(),
    "websocket": AuthMiddlewareStack(
        URLRouter(
             pages.routing.websocket_urlpatterns
            + toggle.routing.websocket_urlpatterns
            
        )
    ),
})
