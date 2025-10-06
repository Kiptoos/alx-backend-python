from django.db.models.signals import post_save, pre_save, post_delete
from django.dispatch import receiver
from django.db import transaction
from django.contrib.auth import get_user_model
from .models import Message, Notification, MessageHistory

User = get_user_model()


@receiver(post_save, sender=Message)
def create_notification_for_new_message(sender, instance, created, **kwargs):
    if created:
        Notification.objects.create(user=instance.receiver, message=instance)


@receiver(pre_save, sender=Message)
def log_message_edit_before_save(sender, instance: Message, **kwargs):
    # Only on update (instance has a primary key)
    if not instance.pk:
        return

    try:
        old = Message.objects.only("content").get(pk=instance.pk)
    except Message.DoesNotExist:
        return

    if old.content != instance.content:
        editor = getattr(instance, "edited_by", None) or getattr(instance, "_editor", None)
        MessageHistory.objects.create(message=instance, old_content=old.content, edited_by=editor)
        instance.edited = True
        if editor and not instance.edited_by:
            instance.edited_by = editor


@receiver(post_delete, sender=User)
def cleanup_user_related_data(sender, instance, **kwargs):
    with transaction.atomic():
        Message.objects.filter(sender=instance).delete()
        Message.objects.filter(receiver=instance).delete()
        Notification.objects.filter(user=instance).delete()
        MessageHistory.objects.filter(message__sender=instance).delete()
        MessageHistory.objects.filter(message__receiver=instance).delete()
