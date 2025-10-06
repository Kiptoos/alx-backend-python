from django.test import TestCase
from django.contrib.auth import get_user_model
from .models import Message, Notification, MessageHistory

User = get_user_model()

class MessagingSignalsTests(TestCase):
    def setUp(self):
        self.alice = User.objects.create_user(username="alice", password="pass")
        self.bob = User.objects.create_user(username="bob", password="pass")

    def test_post_save_creates_notification(self):
        m = Message.objects.create(sender=self.alice, receiver=self.bob, content="Hello")
        self.assertTrue(Notification.objects.filter(message=m, recipient=self.bob).exists())

    def test_pre_save_creates_history_on_edit(self):
        m = Message.objects.create(sender=self.alice, receiver=self.bob, content="Hello")
        m.content = "Hello (edited)"
        m.save()
        self.assertTrue(m.edited)
        self.assertTrue(MessageHistory.objects.filter(message=m, old_content="Hello").exists())
