from django.db.models.signals import post_save, pre_save, post_delete
from django.dispatch import receiver
from django.contrib.auth import get_user_model
from django.utils import timezone
from django.db.models import Q
from .models import Message, Notification, MessageHistory
User = get_user_model()
@receiver(post_save, sender=Message)
def create_notification_on_new_message(sender, instance, created, **kwargs):
    if created:
        Notification.objects.create(user=instance.receiver, message=instance, text=f"New message from {instance.sender}")
@receiver(pre_save, sender=Message)
def log_message_edit(sender, instance, **kwargs):
    if instance.pk:
        try: old = Message.objects.get(pk=instance.pk)
        except Message.DoesNotExist: return
        if old.content != instance.content:
            MessageHistory.objects.create(message=old, old_content=old.content, edited_at=timezone.now())
            instance.edited = True
@receiver(post_delete, sender=User)
def cleanup_user_related(sender, instance, **kwargs):
    Message.objects.filter(Q(sender=instance) | Q(receiver=instance)).delete()
    Notification.objects.filter(Q(user=instance)).delete()
