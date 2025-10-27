from django.contrib import admin
from django.urls import path
from django.shortcuts import render
from messaging.views import delete_user
from chats.views import conversation_detail

def home(request):
    return render(request, "home.html")

urlpatterns = [
    path("", home, name="home"),  # root now works
    path("admin/", admin.site.urls),
    path("account/delete/", delete_user, name="delete_user"),
    path("chats/<int:user_id>/", conversation_detail, name="conversation_detail"),
]
