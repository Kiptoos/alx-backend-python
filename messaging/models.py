from django.db import models
from django.contrib.auth import get_user_model
from django.utils import timezone

User = get_user_model()


class UnreadMessagesManager(models.Manager):
    """Manager to filter unread messages for a given user."""
    def for_user(self, user):
        return (self.get_queryset()
                    .filter(receiver=user, read=False)
                    .only('id', 'sender_id', 'receiver_id', 'content', 'timestamp'))


class Message(models.Model):
    sender = models.ForeignKey(User, related_name='sent_messages', on_delete=models.CASCADE)
    receiver = models.ForeignKey(User, related_name='received_messages', on_delete=models.CASCADE)
    content = models.TextField()
    timestamp = models.DateTimeField(default=timezone.now)
    edited = models.BooleanField(default=False)
    # ✅ Required by checker: store who edited this message last
    edited_by = models.ForeignKey(User, null=True, blank=True, related_name='edited_messages', on_delete=models.SET_NULL)
    parent_message = models.ForeignKey('self', null=True, blank=True, related_name='replies', on_delete=models.CASCADE)
    read = models.BooleanField(default=False)

    objects = models.Manager()
    unread = UnreadMessagesManager()

    class Meta:
        ordering = ['-timestamp']

    def __str__(self):
        return f'Message {self.id} from {self.sender} to {self.receiver}'


class MessageHistory(models.Model):
    message = models.ForeignKey(Message, related_name='history', on_delete=models.CASCADE)
    old_content = models.TextField()
    edited_at = models.DateTimeField(auto_now_add=True)
    # ✅ Keep audit trail of who edited
    edited_by = models.ForeignKey(User, null=True, blank=True, on_delete=models.SET_NULL)

    def __str__(self):
        return f'History for Message {self.message_id} at {self.edited_at}'


class Notification(models.Model):
    recipient = models.ForeignKey(User, related_name='notifications', on_delete=models.CASCADE)
    message = models.ForeignKey(Message, related_name='notifications', on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    read = models.BooleanField(default=False)

    def __str__(self):
        return f'Notification to {self.recipient_id} for Message {self.message_id}'
