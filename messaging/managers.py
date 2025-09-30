from django.db import models

class MessageQuerySet(models.QuerySet):
    def unread_for(self, user):
        return self.filter(receiver=user, read=False)

class UnreadMessagesManager(models.Manager):
    def get_queryset(self):
        return MessageQuerySet(self.model, using=self._db)

    def for_user(self, user):
        return (self.get_queryset()
                    .unread_for(user)
                    .only('id', 'sender', 'receiver', 'content', 'created_at', 'read'))
