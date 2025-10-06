from django.urls import path
from .views import ping, conversation_list, message_thread, send_message, unread_inbox

urlpatterns = [
    path("ping/", ping, name="messages_ping"),
    path("conversations/", conversation_list, name="conversation_list"),
    path("thread/<int:message_id>/", message_thread, name="message_thread"),
    path("send/", send_message, name="send_message"),
    path("unread/", unread_inbox, name="unread_inbox"),
]
