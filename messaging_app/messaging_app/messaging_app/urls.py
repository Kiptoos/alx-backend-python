from django.contrib import admin
from django.urls import path
from messaging.views import delete_user
from chats.views import conversation_detail

urlpatterns = [
    path('admin/', admin.site.urls),
    path('account/delete/', delete_user, name='delete_user'),
    path('chats/<int:user_id>/', conversation_detail, name='conversation_detail'),
]
