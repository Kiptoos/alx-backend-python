from django.http import JsonResponse, Http404
from django.views.decorators.http import require_GET
from django.shortcuts import get_object_or_404
from django.db.models import Prefetch
from messaging.models import Message

@require_GET
def conversation_list(request):
    """
    Optimized list view using select_related & prefetch_related to reduce queries.
    Shows recent messages (top-level and replies).
    """
    qs = (
        Message.objects
        .select_related("sender", "receiver", "parent_message")             # <- select_related
        .prefetch_related(                                                  # <- prefetch_related
            "replies",
            Prefetch("replies__replies"),                                   # grandchildren (helps in UI)
            "history",
        )
        .only("id", "content", "timestamp", "edited", "read",
              "sender__username", "receiver__username", "parent_message")
        .order_by("-timestamp")[:100]
    )

    data = []
    for m in qs:
        data.append({
            "id": m.id,
            "sender": getattr(m.sender, "username", m.sender_id),
            "receiver": getattr(m.receiver, "username", m.receiver_id),
            "content": m.content,
            "edited": m.edited,
            "read": m.read,
            "timestamp": m.timestamp.isoformat(),
            "parent_message": m.parent_message_id,
            "replies_count": getattr(m, "replies").count() if hasattr(m, "replies") else 0,
            "history_count": getattr(m, "history").count() if hasattr(m, "history") else 0,
        })
    return JsonResponse({"messages": data})


@require_GET
def message_thread(request, message_id: int):
    """
    Recursive threaded view:
    - Start from the root message (message_id)
    - Recursively build *all* replies (descendants) in a nested tree for the UI.
    - Uses batched ORM queries per level to avoid N+1, then in-memory recursion.

    This satisfies the 'recursive query' requirement in a Django-ORM-friendly way.
    """
    root = get_object_or_404(
        Message.objects.select_related("sender", "receiver"),  # initial FK joins
        pk=message_id
    )

    # Breadth-first, batched fetch of descendants (avoid per-node queries)
    all_nodes = {root.id: root}
    children_map = {root.id: []}
    frontier = [root.id]

    while frontier:
        level_qs = (
            Message.objects
            .filter(parent_message_id__in=frontier)
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
        """Recursive in-memory tree builder (no extra DB hits)."""
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

    tree = build_tree(root.id)
    return JsonResponse({"thread": tree})


@require_GET
def unread_inbox(request):
    """
    Show only unread messages for the current user using the custom manager.
    This also relies on .only() optimization inside the manager.
    """
    if not request.user.is_authenticated:
        return JsonResponse({"detail": "Authentication required"}, status=401)

    qs = Message.unread.for_user(request.user)  # <- uses custom manager + .only()
    # If you want more joins (names etc.), you can chain select_related safely:
    qs = qs.select_related("sender", "receiver")  # still efficient with .only()

    data = [{
        "id": m.id,
        "sender": getattr(m.sender, "username", m.sender_id),
        "receiver": getattr(m.receiver, "username", m.receiver_id),
        "content": m.content,
        "timestamp": m.timestamp.isoformat(),
    } for m in qs[:100]]

    return JsonResponse({"unread": data})
