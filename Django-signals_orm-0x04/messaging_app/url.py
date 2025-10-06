# project urls.py (e.g., messaging_app/messaging_app/urls.py)
from django.urls import path, include
urlpatterns = [ path("chats/", include("chats.urls")) ]
