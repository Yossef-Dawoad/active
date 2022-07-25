from django.urls import re_path
from . import consumers

websocket_urlpatterns = [
    re_path(r'ws/activelock/', consumers.ActiveLockHandlerConsumer.as_asgi()),
]



