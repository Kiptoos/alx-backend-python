from django.contrib import admin
from django.urls import path, include
from django.views.generic import RedirectView
from messaging.views import delete_user
from chats.views import conversation_detail

urlpatterns = [
    path("", RedirectView.as_view(pattern_name="admin:index", permanent=False)),  # <-- add this
    path("admin/", admin.site.urls),
    path("account/delete/", delete_user, name="delete_user"),
    path("chats/<int:user_id>/", conversation_detail, name="conversation_detail"),
    # (optional) built-in auth views like /accounts/login/ if you want them:
    # path("accounts/", include("django.contrib.auth.urls")),
]
