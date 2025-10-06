from django.contrib import admin
from django.urls import path, include
from django.views.generic import RedirectView
from messaging.views import delete_user
from chats.views import conversation_detail
from .views import conversation_list, message_thread

urlpatterns = [
    path("", RedirectView.as_view(pattern_name="admin:index", permanent=False)),  # <-- add this
    path("admin/", admin.site.urls),
    path("account/delete/", delete_user, name="delete_user"),
    path("chats/<int:user_id>/", conversation_detail, name="conversation_detail"),
    path("conversations/", conversation_list, name="conversation_list"),
    path("thread/<int:message_id>/", message_thread, name="message_thread"),
    # (optional) built-in auth views like /accounts/login/ if you want them:
    # path("accounts/", include("django.contrib.auth.urls")),
]

