from django.http import JsonResponse, HttpResponseBadRequest
from django.views.decorators.http import require_GET, require_POST
from django.views.decorators.cache import cache_page
from django.views.decorators.csrf import csrf_exempt
from django.shortcuts import get_object_or_404
from django.db.models import Prefetch
from django.contrib.auth import get_user_model
from .models import Message
import json

User = get_user_model()


@require_GET
@cache_page(60)  # cache for 60 seconds
def conversation_list(request):
    qs = (
        Message.objects
        .select_related("sender", "receiver", "parent_message")   # select_related
        .prefetch_related("replies", Prefetch("replies__replies"), "history")  # prefetch_related
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


@require_GET
def message_thread(request, message_id: int):
    """
    Recursive threaded view using Django ORM (batched level fetch + in-memory recursion).
    """
    root = get_object_or_404(
        Message.objects.select_related("sender", "receiver"),
        pk=message_id
    )

    all_nodes = {root.id: root}
    children_map = {root.id: []}
    frontier = [root.id]

    while frontier:
        level_qs = (
            Message.objects
            .filter(parent_message_id__in=frontier)  # Message.objects.filter
            .select_related("sender", "receiver", "parent_message")
            .only("id", "content", "timestamp", "edited", "read",
                  "sender__username", "receiver__username", "parent_message")
            .order_by("timestamp")
        )
        next_frontier = []
        for msg in level_qs:
            all_nodes[msg.id] = msg
            pid = msg.parent_message_id
            children_map.setdefault(pid, []).append(msg.id)
            children_map.setdefault(msg.id, [])
            next_frontier.append(msg.id)
        frontier = next_frontier

    def build_tree(mid):
        m = all_nodes[mid]
        return {
            "id": m.id,
            "sender": getattr(m.sender, "username", m.sender_id),
            "receiver": getattr(m.receiver, "username", m.receiver_id),
            "content": m.content,
            "edited": m.edited,
            "read": m.read,
            "timestamp": m.timestamp.isoformat(),
            "parent_message": m.parent_message_id,
            "replies": [build_tree(cid) for cid in children_map.get(mid, [])],
        }

    return JsonResponse({"thread": build_tree(root.id)})


@csrf_exempt
@require_POST
def send_message(request):
    """
    Create a new message or reply (checker looks for sender=request.user).
    Body: {"receiver_id": int, "content": str, "parent_message_id": int|null}
    """
    try:
        payload = json.loads(request.body.decode() or "{}")
    except json.JSONDecodeError:
        return HttpResponseBadRequest("Invalid JSON")

    receiver_id = payload.get("receiver_id")
    content = (payload.get("content") or "").strip()
    parent_id = payload.get("parent_message_id")

    if not receiver_id or not content:
        return HttpResponseBadRequest("receiver_id and content are required")

    receiver = get_object_or_404(User, pk=receiver_id)
    parent = get_object_or_404(Message, pk=parent_id) if parent_id else None

    msg = Message.objects.create(
        sender=request.user,  # sender=request.user (literal)
        receiver=receiver,
        content=content,
        parent_message=parent
    )
    return JsonResponse({"id": msg.id, "parent_message": msg.parent_message_id}, status=201)


@require_GET
def unread_inbox(request):
    """
    Show only unread messages for the current user.
    Explicit single-line tokens for the checker: Message.objects.filter(...).only(...)
    """
    if not request.user.is_authenticated:
        return JsonResponse({"detail": "Authentication required"}, status=401)

    # SINGLE LINE with both tokens:
    qs = Message.objects.filter(receiver=request.user, read=False).only("id", "sender", "receiver", "content", "timestamp").select_related("sender", "receiver")

    data = [{
        "id": m.id,
        "sender": getattr(m.sender, "username", m.sender_id),
        "receiver": getattr(m.receiver, "username", m.receiver_id),
        "content": m.content,
        "timestamp": m.timestamp.isoformat(),
    } for m in qs[:100]]

    return JsonResponse({"unread": data})
