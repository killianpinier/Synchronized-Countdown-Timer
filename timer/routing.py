from django.urls import path
from timer.consumers import TimerConsumer

websocket_urlpatterns = [
    path("ws/timers/<session_id>/", TimerConsumer.as_asgi()),
]