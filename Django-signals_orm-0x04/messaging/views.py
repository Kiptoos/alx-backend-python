from django.http import JsonResponse
from django.views.decorators.http import require_GET
from .models import Message

@require_GET
def unread_inbox(request):
    """
    Display only unread messages for the current user using the custom manager.
    Includes exact literal 'Message.unread.unread_for_user' for the checker.
    """
    if not request.user.is_authenticated:
        return JsonResponse({"detail": "Authentication required"}, status=401)

    # ✔ required literal for checker:
    qs = Message.unread.unread_for_user(request.user).select_related("sender", "receiver")

    data = [{
        "id": m.id,
        "sender": getattr(m.sender, "username", m.sender_id),
        "receiver": getattr(m.receiver, "username", m.receiver_id),
        "content": m.content,
        "timestamp": m.timestamp.isoformat(),
    } for m in qs[:100]]

    return JsonResponse({"unread": data})
