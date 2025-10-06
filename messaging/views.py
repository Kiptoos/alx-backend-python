# messaging/views.py
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
        .select_related("sender", "receiver", "parent_message")            # JOIN FKs
        .prefetch_related(                                                 # Prefetch reverse relations
            "replies",
            Prefetch("replies__replies"),                                  # pull grandchildren too (helps in UI)
            "history",
        )
        .only("id", "content", "timestamp", "edited", "read",
              "sender__username", "receiver__username", "parent_message")  # load only what we need
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
    Recursive thread view:
    - Starts from the root message (message_id)
    - Recursively fetches *all* replies (descendants) using batched ORM queries
    - Returns a nested (tree) JSON for UI threaded display

    Uses select_related / prefetch_related to minimize DB hits per level.
    """
    root = get_object_or_404(
        Message.objects.select_related("sender", "receiver"),
        pk=message_id
    )

    # Breadth-first batched fetch to avoid N+1:
    # Collect descendants level by level with IN queries.
    all_nodes = {root.id: root}
    children_map = {root.id: []}

    frontier = [root.id]
    while frontier:
        # Fetch replies to all nodes in the current frontier in one go
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
            if pid not in children_map:
                children_map[pid] = []
            children_map[pid].append(msg.id)
            children_map[msg.id] = []   # ensure key exists
            next_frontier.append(msg.id)
        frontier = next_frontier

    # Recursive builder (in-memory) — no extra DB queries here
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

    tree = build_tree(root.id)
    return JsonResponse({"thread": tree})
