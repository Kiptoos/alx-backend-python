from django.db import models

class UnreadMessagesManager(models.Manager):
    """Filter unread messages for a specific user and limit fetched fields."""
    def for_user(self, user):
        return (
            self.get_queryset()
            .filter(receiver=user, read=False)
            .only("id", "sender", "receiver", "content", "timestamp")  # <- .only() optimization
        )
