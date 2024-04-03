from django.urls import re_path
from .consumer import Consumer

websocket_urlpatterns = [
    #Las peticiones http://localhost:8000/ws/chat/room_name/ seran manejadas por el Consumer
    re_path(r'ws/chat/(?P<room_name>\w+)/', Consumer.as_asgi()),
]