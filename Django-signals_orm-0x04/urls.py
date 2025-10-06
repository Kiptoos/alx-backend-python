from django.urls import path, include

urlpatterns = [
    path("messages/", include("messaging.urls")),
]
