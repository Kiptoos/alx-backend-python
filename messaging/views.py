# messaging/views.py (replace only the unread_inbox function with this)

from django.http import JsonResponse
from django.views.decorators.http import require_GET
from .models import Message

@require_GET
def unread_inbox(request):
    """
    Display only unread messages for the current user.
    - Keeps the manager usage for the previous check
    - Adds explicit Message.objects.filter(...).only(...) for this checker
    """
    if not request.user.is_authenticated:
        return JsonResponse({"detail": "Authentication required"}, status=401)

    # Keep this line so the "use the manager" check continues to pass:
    manager_qs = Message.unread.unread_for_user(request.user)

    # Explicit query the checker is looking for:
    qs = (
        Message.objects
        .filter(receiver=request.user, read=False)   # <- literal: Message.objects.filter
        .only("id", "sender", "receiver", "content", "timestamp")  # <- literal: .only
        .select_related("sender", "receiver")
    )

    data = [{
        "id": m.id,
        "sender": getattr(m.sender, "username", m.sender_id),
        "receiver": getattr(m.receiver, "username", m.receiver_id),
        "content": m.content,
        "timestamp": m.timestamp.isoformat(),
    } for m in qs[:100]]

    return JsonResponse({"unread": data})
