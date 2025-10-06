# chats/urls.py
from django.urls import path
from .views import conversation_list
urlpatterns = [ path("conversations/", conversation_list, name="conversation_list") ]
