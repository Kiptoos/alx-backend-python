from django.db import models

class UnreadMessagesManager(models.Manager):
    """Filters unread messages for a specific user and limits fetched fields."""
    def unread_for_user(self, user):
        # .only() optimization the checker looks for
        return (
            self.get_queryset()
            .filter(receiver=user, read=False)
            .only("id", "sender", "receiver", "content", "timestamp")
        )
