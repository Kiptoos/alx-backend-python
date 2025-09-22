from rest_framework import viewsets, permissions, status
from rest_framework.response import Response
from rest_framework.decorators import action
from django.shortcuts import get_object_or_404

from .models import User, Conversation, Message
from .serializers import UserSerializer, ConversationSerializer, MessageSerializer

class ConversationViewSet(viewsets.ModelViewSet):
    queryset = Conversation.objects.all().prefetch_related("participants", "messages__sender")
    serializer_class = ConversationSerializer
    permission_classes = [permissions.AllowAny]

    @action(detail=True, methods=["post"])
    def send_message(self, request, pk=None):
        conversation = self.get_object()
        user = None
        # If you have auth, use request.user. For now allow anonymous sender via query param for testing.
        sender_id = request.data.get("sender_id")
        if sender_id:
            user = get_object_or_404(User, id=sender_id)
        elif request.user and request.user.is_authenticated:
            user = request.user
        else:
            return Response({"detail": "sender_id is required (or authenticate)."}, status=400)

        serializer = MessageSerializer(data={
            "conversation": str(conversation.id),
            "message_body": request.data.get("message_body", ""),
        })
        serializer.is_valid(raise_exception=True)
        message = Message.objects.create(
            conversation=conversation,
            sender=user,
            message_body=serializer.validated_data["message_body"],
        )
        return Response(MessageSerializer(message).data, status=status.HTTP_201_CREATED)

class MessageViewSet(viewsets.ModelViewSet):
    queryset = Message.objects.select_related("conversation", "sender").all()
    serializer_class = MessageSerializer
    permission_classes = [permissions.AllowAny]

    def perform_create(self, serializer):
        sender = None
        sender_id = self.request.data.get("sender_id")
        if sender_id:
            sender = get_object_or_404(User, id=sender_id)
        elif self.request.user and self.request.user.is_authenticated:
            sender = self.request.user
        else:
            raise ValueError("sender_id is required (or authenticate).")
        serializer.save(sender=sender)
