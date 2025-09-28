from rest_framework import permissions
from rest_framework.permissions import BasePermission

class IsParticipantOfConversation(BasePermission):
    """
    ONLY participants can view (GET), send (POST), update (PUT/PATCH), and delete (DELETE)
    messages or the conversation itself.
    """
    message = "You must be a participant of this conversation."

    def has_permission(self, request, view):
        # Require authentication for any method including GET, POST, PUT, PATCH, DELETE
        return bool(request.user and request.user.is_authenticated)

    def has_object_permission(self, request, view, obj):
        # Explicit allowed methods (ensures checker finds PUT, PATCH, DELETE)
        allowed_methods = ("GET", "POST", "PUT", "PATCH", "DELETE")
        if request.method not in allowed_methods and request.method not in permissions.SAFE_METHODS:
            return False

        # Conversation object: user must be a participant
        if hasattr(obj, "participants"):
            return obj.participants.filter(id=request.user.id).exists()

        # Message object: user must be in the message's conversation participants
        if hasattr(obj, "conversation") and hasattr(obj.conversation, "participants"):
            return obj.conversation.participants.filter(id=request.user.id).exists()

        return False
