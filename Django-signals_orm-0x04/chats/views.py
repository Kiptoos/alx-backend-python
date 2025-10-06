from django.shortcuts import get_object_or_404
from django.http import JsonResponse
from django.views.decorators.http import require_GET
from django.utils.decorators import method_decorator
from django.views.decorators.cache import cache_page
from messaging.models import Message

@require_GET
@cache_page(60)  # Task 5: cache for 60 seconds
def conversation_list(request):
    """Return latest messages with optimized related loading."""
    qs = (Message.objects
          .select_related("sender", "receiver", "parent_message")
          .prefetch_related("replies"))
    data = [{
        "id": m.id,
        "sender": getattr(m.sender, "username", str(m.sender_id)),
        "receiver": getattr(m.receiver, "username", str(m.receiver_id)),
        "content": m.content,
        "edited": m.edited,
        "read": m.read,
        "timestamp": m.timestamp.isoformat(),
        "parent_message": m.parent_message_id,
        "replies_count": getattr(m, "replies", []).count() if hasattr(m, "replies") else 0,
    } for m in qs[:100]]
    return JsonResponse({"messages": data})
