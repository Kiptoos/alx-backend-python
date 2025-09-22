from django.contrib import admin
from .models import User, Conversation, Message

@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    list_display = ("id", "username", "email", "first_name", "last_name", "role", "created_at")
    search_fields = ("username", "email", "first_name", "last_name")

@admin.register(Conversation)
class ConversationAdmin(admin.ModelAdmin):
    list_display = ("id", "created_at")
    filter_horizontal = ("participants",)

@admin.register(Message)
class MessageAdmin(admin.ModelAdmin):
    list_display = ("id", "conversation", "sender", "sent_at")
    search_fields = ("message_body",)
