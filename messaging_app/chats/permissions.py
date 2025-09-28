from rest_framework import permissions
from rest_framework.permissions import BasePermission


class IsParticipantOfConversation(BasePermission):
    """
    Custom permission that:
    - Allows only authenticated users (handled globally in settings.py).
    - Allows access ONLY if the user is a participant of the relevant conversation.
    - For Message objects, allows participants to view, send, update, and delete.
    """

    message = "You must be a participant of this conversation."

    def has_permission(self, request, view):
        # Defensive check: user must be authenticated
        return bool(request.user and request.user.is_authenticated)

    def has_object_permission(self, request, view, obj):
        """
        Supports objects of type:
        - Conversation: obj.participants contains request.user
        - Message: obj.conversation.participants contains request.user
        """
        if hasattr(obj, "participants"):  # Conversation
            return obj.participants.filter(id=request.user.id).exists()

        if hasattr(obj, "conversation"):  # Message
            return obj.conversation.participants.filter(id=request.user.id).exists()

        return False
