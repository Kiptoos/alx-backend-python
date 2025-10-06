from django.urls import path
from .views import unread_inbox

urlpatterns = [
    path("unread/", unread_inbox, name="unread_inbox"),
]
