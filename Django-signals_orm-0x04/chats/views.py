from django.contrib.auth.decorators import login_required
from django.shortcuts import render, get_object_or_404
from django.contrib.auth import get_user_model
from django.views.decorators.cache import cache_page
from django.db import models
from messaging.models import Message
User = get_user_model()
@login_required
@cache_page(60)
def conversation_detail(request, user_id):
    other = get_object_or_404(User, pk=user_id)
    qs = (Message.objects
        .filter((models.Q(sender=request.user, receiver=other) | models.Q(sender=other, receiver=request.user)))
        .select_related("sender","receiver","parent_message")
        .prefetch_related("replies__sender","replies__receiver")
        .order_by("created_at"))
    return render(request, "chats/conversation_detail.html", {"messages": qs, "other": other})
