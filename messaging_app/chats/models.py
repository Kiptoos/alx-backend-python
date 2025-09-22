import uuid
from django.db import models
from django.contrib.auth.models import AbstractUser

class User(AbstractUser):
    class Roles(models.TextChoices):
        GUEST = "guest", "Guest"
        HOST = "host", "Host"
        ADMIN = "admin", "Admin"

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False, db_index=True)
    # AbstractUser already has: username, first_name, last_name, email, password
    phone_number = models.CharField(max_length=32, null=True, blank=True)
    role = models.CharField(max_length=10, choices=Roles.choices, default=Roles.GUEST)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.username} ({self.email})"

class Conversation(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False, db_index=True, verbose_name="conversation_id")
    participants = models.ManyToManyField(User, related_name="conversations")
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Conversation {self.id}"

class Message(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False, db_index=True, verbose_name="message_id")
    conversation = models.ForeignKey(Conversation, related_name="messages", on_delete=models.CASCADE)
    sender = models.ForeignKey(User, related_name="sent_messages", on_delete=models.CASCADE)
    message_body = models.TextField()
    sent_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["sent_at"]

    def __str__(self):
        return f"Msg {self.id} in {self.conversation_id}"
