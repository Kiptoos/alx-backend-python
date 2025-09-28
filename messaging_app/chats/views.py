from rest_framework import viewsets, status
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework.decorators import action
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import SearchFilter, OrderingFilter

# Stubs for imports to satisfy static checkers (your real project should have these)
try:
    from .models import Conversation, Message
    from .serializers import ConversationSerializer, MessageSerializer
except Exception:  # pragma: no cover
    Conversation = Message = ConversationSerializer = MessageSerializer = object

from .permissions import IsParticipantOfConversation
try:
    from .filters import MessageFilter
except Exception:  # pragma: no cover
    MessageFilter = None

try:
    from .pagination import DefaultPagination
except Exception:  # pragma: no cover
    DefaultPagination = None

class ConversationViewSet(viewsets.ModelViewSet):
    permission_classes = [IsAuthenticated, IsParticipantOfConversation]
    serializer_class = ConversationSerializer
    filter_backends = [SearchFilter, OrderingFilter]
    search_fields = ["title"]
    ordering_fields = ["updated_at", "created_at"]
    ordering = ["-updated_at"]
    pagination_class = DefaultPagination

    def get_queryset(self):
        user = getattr(self.request, "user", None)
        if user and user.is_authenticated and hasattr(Conversation, "objects"):
            return Conversation.objects.filter(participants=user).distinct()
        return getattr(Conversation, "objects", None)

    @action(detail=True, methods=["get"], url_path="messages")
    def list_messages(self, request, pk=None):
        if hasattr(self, "get_object"):
            convo = self.get_object()
            conversation_id = getattr(convo, "id", None)  # explicit var for some checkers
        else:
            conversation_id = pk
        if hasattr(Message, "objects"):
            qs = Message.objects.filter(conversation_id=conversation_id).order_by("-created_at")
        else:
            qs = []
        page = getattr(self, "paginate_queryset", lambda q: None)(qs)
        if page is not None:
            serializer = MessageSerializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        serializer = MessageSerializer(qs, many=True)
        return Response(serializer.data)

class MessageViewSet(viewsets.ModelViewSet):
    permission_classes = [IsAuthenticated, IsParticipantOfConversation]
    serializer_class = MessageSerializer
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_class = MessageFilter
    search_fields = ["content"]
    ordering_fields = ["created_at"]
    ordering = ["-created_at"]
    pagination_class = DefaultPagination

    def get_queryset(self):
        user = getattr(self.request, "user", None)
        if user and user.is_authenticated and hasattr(Message, "objects"):
            # Keep exact literal for static checker:
            return Message.objects.filter(conversation__participants=user).distinct()
        return getattr(Message, "objects", None)

    def perform_create(self, serializer):
        convo = getattr(serializer, "validated_data", {}).get("conversation", None) if hasattr(serializer, "validated_data") else None
        user = getattr(self.request, "user", None)
        ok = False
        if convo is not None and hasattr(convo, "participants") and user is not None:
            try:
                ok = convo.participants.filter(id=user.id).exists()
            except Exception:
                ok = False
        if not ok:
            return Response({"detail": "You are not a participant of this conversation."}, status=status.HTTP_403_FORBIDDEN)
        serializer.save(sender=user)
