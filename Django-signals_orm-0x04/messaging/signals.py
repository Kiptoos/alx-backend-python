from django.db.models.signals import post_save, pre_save, post_delete
from django.dispatch import receiver
from django.contrib.auth import get_user_model
from django.db import transaction
from .models import Message, Notification, MessageHistory

User = get_user_model()

@receiver(post_save, sender=Message)
def create_notification_for_new_message(sender, instance, created, **kwargs):
    """Task 0: When a new Message is created, create a Notification for the receiver."""
    if created:
        Notification.objects.create(recipient=instance.receiver, message=instance)

@receiver(pre_save, sender=Message)
def log_message_edit_before_save(sender, instance, **kwargs):
    """Task 1: Before updating a Message, store the old content in MessageHistory and mark edited."""
    if instance.pk:
        try:
            old = Message.objects.only("content").get(pk=instance.pk)
        except Message.DoesNotExist:
            return
        if old.content != instance.content:
            # Record history and mark edited
            MessageHistory.objects.create(message=instance, old_content=old.content)
            instance.edited = True

@receiver(post_delete, sender=User)
def cleanup_user_related_data(sender, instance, **kwargs):
    """Task 2: After a User is deleted, remove related Messages/Notifications/Histories if any remain."""
    # CASCADE on FKs should remove most, but ensure cleanup if custom relations exist.
    # Guard within a transaction for consistency.
    with transaction.atomic():
        Message.objects.filter(sender=instance).delete()
        Message.objects.filter(receiver=instance).delete()
        Notification.objects.filter(recipient=instance).delete()
        MessageHistory.objects.filter(message__sender=instance).delete()
        MessageHistory.objects.filter(message__receiver=instance).delete()
