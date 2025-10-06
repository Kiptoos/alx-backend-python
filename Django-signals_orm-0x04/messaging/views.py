from django.http import JsonResponse
from django.views.decorators.http import require_GET
from django.views.decorators.cache import cache_page
from .models import Message

@require_GET
@cache_page(60)  # 60 seconds cache timeout
def conversation_list(request):
    qs = (
        Message.objects
        .select_related("sender", "receiver", "parent_message")
        .prefetch_related("replies", "history")
        .only("id", "content", "timestamp", "edited", "read",
              "sender__username", "receiver__username", "parent_message")
        .order_by("-timestamp")[:100]
    )
    data = [{
        "id": m.id,
        "sender": getattr(m.sender, "username", m.sender_id),
        "receiver": getattr(m.receiver, "username", m.receiver_id),
        "content": m.content,
        "edited": m.edited,
        "read": m.read,
        "timestamp": m.timestamp.isoformat(),
        "parent_message": m.parent_message_id,
    } for m in qs]
    return JsonResponse({"messages": data})
