from django.db import models
from django.contrib.auth import get_user_model
from django.utils import timezone
from .managers import UnreadMessagesManager  # <- import the custom manager

User = get_user_model()

class Message(models.Model):
    sender = models.ForeignKey(User, on_delete=models.CASCADE, related_name="sent_messages")
    receiver = models.ForeignKey(User, on_delete=models.CASCADE, related_name="received_messages")
    content = models.TextField()
    timestamp = models.DateTimeField(default=timezone.now)
    edited = models.BooleanField(default=False)
    edited_by = models.ForeignKey(User, null=True, blank=True, on_delete=models.SET_NULL, related_name="edited_messages")
    parent_message = models.ForeignKey("self", null=True, blank=True, on_delete=models.CASCADE, related_name="replies")
    read = models.BooleanField(default=False)

    objects = models.Manager()
    unread = UnreadMessagesManager()  # <- use the custom manager

    class Meta:
        ordering = ["-timestamp"]

    def __str__(self):
        return f"Message {self.id} from {self.sender} to {self.receiver}"
