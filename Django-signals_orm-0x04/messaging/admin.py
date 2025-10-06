from django.contrib import admin
from .models import Message, Notification, MessageHistory

@admin.register(Message)
class MessageAdmin(admin.ModelAdmin):
    list_display = ("id", "sender", "receiver", "edited", "read", "timestamp", "parent_message")
    list_filter = ("edited", "read", "timestamp")
    search_fields = ("content", "sender__username", "receiver__username")

@admin.register(Notification)
class NotificationAdmin(admin.ModelAdmin):
    list_display = ("id", "recipient", "message", "read", "created_at")
    list_filter = ("read", "created_at")
    search_fields = ("recipient__username",)

@admin.register(MessageHistory)
class MessageHistoryAdmin(admin.ModelAdmin):
    list_display = ("id", "message", "edited_at")
    search_fields = ("message__content",)
