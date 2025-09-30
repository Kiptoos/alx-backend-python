from django.contrib import admin
from .models import Message, MessageHistory, Notification

@admin.register(Message)
class MessageAdmin(admin.ModelAdmin):
    list_display = ('id', 'sender', 'receiver', 'short_content', 'edited', 'read', 'created_at')
    list_filter = ('edited', 'read', 'created_at')
    search_fields = ('content', 'sender__username', 'receiver__username')

    def short_content(self, obj):
        return (obj.content[:40] + '…') if len(obj.content) > 43 else obj.content

@admin.register(MessageHistory)
class MessageHistoryAdmin(admin.ModelAdmin):
    list_display = ('id', 'message', 'edited_at')
    search_fields = ('message__content',)

@admin.register(Notification)
class NotificationAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'message', 'text', 'is_read', 'created_at')
    list_filter = ('is_read', 'created_at')
    search_fields = ('text', 'user__username')
