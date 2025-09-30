from django.conf import settings
from django.db import models
from django.utils import timezone
from .managers import UnreadMessagesManager
User = settings.AUTH_USER_MODEL
class Message(models.Model):
    sender = models.ForeignKey(User, on_delete=models.CASCADE, related_name="sent_messages")
    receiver = models.ForeignKey(User, on_delete=models.CASCADE, related_name="received_messages")
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    edited = models.BooleanField(default=False)
    read = models.BooleanField(default=False)
    parent_message = models.ForeignKey("self", null=True, blank=True, on_delete=models.CASCADE, related_name="replies")
    objects = models.Manager()
    unread = UnreadMessagesManager()
    class Meta:
        indexes = [models.Index(fields=["receiver","read"]), models.Index(fields=["sender","created_at"])]
        ordering = ["created_at"]
    def __str__(self):
        return f"Msg #{self.pk} from {self.sender} to {self.receiver}"
    def get_thread(self):
        thread = [self]; frontier = [self]
        while frontier:
            ids = [m.id for m in frontier]
            children = list(Message.objects.filter(parent_message_id__in=ids)
                            .select_related("sender","receiver","parent_message"))
            thread.extend(children); frontier = children
        return thread
class MessageHistory(models.Model):
    message = models.ForeignKey(Message, on_delete=models.CASCADE, related_name="history")
    old_content = models.TextField()
    edited_at = models.DateTimeField(default=timezone.now)
    class Meta: ordering = ["-edited_at"]
class Notification(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="notifications")
    message = models.ForeignKey(Message, on_delete=models.CASCADE, related_name="notifications")
    text = models.CharField(max_length=255)
    created_at = models.DateTimeField(auto_now_add=True)
    is_read = models.BooleanField(default=False)
    class Meta: ordering = ["-created_at"]
    def __str__(self): return f"Notification for {self.user}: {self.text}"
