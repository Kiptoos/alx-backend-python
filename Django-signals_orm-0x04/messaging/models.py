from django.db import models
from django.contrib.auth import get_user_model
from django.utils import timezone

User = get_user_model()

class UnreadMessagesManager(models.Manager):
    """Manager to filter unread messages for a given user."""
    def for_user(self, user):
        return (self.get_queryset()
                    .filter(receiver=user, read=False)
                    .only("id", "sender_id", "receiver_id", "content", "timestamp"))

class Message(models.Model):
    sender = models.ForeignKey(User, related_name="sent_messages", on_delete=models.CASCADE)
    receiver = models.ForeignKey(User, related_name="received_messages", on_delete=models.CASCADE)
    content = models.TextField()
    timestamp = models.DateTimeField(default=timezone.now)
    # Task 1: edited flag to mark if message has been edited
    edited = models.BooleanField(default=False)
    # Task 3: threaded conversations (self-referential)
    parent_message = models.ForeignKey("self", null=True, blank=True, related_name="replies", on_delete=models.CASCADE)
    # Task 4: read boolean
    read = models.BooleanField(default=False)

    objects = models.Manager()
    unread = UnreadMessagesManager()

    class Meta:
        ordering = ["-timestamp"]

    def __str__(self):
        return f"Msg {self.id} from {self.sender} to {self.receiver}"

class MessageHistory(models.Model):
    message = models.ForeignKey(Message, related_name="history", on_delete=models.CASCADE)
    old_content = models.TextField()
    edited_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"History for Msg {self.message_id} @ {self.edited_at}"

class Notification(models.Model):
    recipient = models.ForeignKey(User, related_name="notifications", on_delete=models.CASCADE)
    message = models.ForeignKey(Message, related_name="notifications", on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    read = models.BooleanField(default=False)

    def __str__(self):
        return f"Notification to {self.recipient_id} for Msg {self.message_id}"
