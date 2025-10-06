from django.urls import path
from .views import conversation_list, message_thread, send_message

urlpatterns = [
    path("conversations/", conversation_list, name="conversation_list"),
    path("thread/<int:message_id>/", message_thread, name="message_thread"),
    path("send/", send_message, name="send_message"),
]
