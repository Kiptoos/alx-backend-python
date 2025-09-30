from django.test import TestCase
from django.contrib.auth import get_user_model
from .models import Message, Notification, MessageHistory
User = get_user_model()
class MessagingSignalsTests(TestCase):
    def setUp(self):
        self.alice = User.objects.create_user(username="alice", password="x")
        self.bob = User.objects.create_user(username="bob", password="x")
    def test_notification_created_on_message(self):
        m = Message.objects.create(sender=self.alice, receiver=self.bob, content="Hi Bob")
        self.assertTrue(Notification.objects.filter(user=self.bob, message=m).exists())
    def test_message_history_on_edit(self):
        m = Message.objects.create(sender=self.alice, receiver=self.bob, content="v1")
        m.content = "v2"; m.save()
        self.assertTrue(m.edited); self.assertEqual(m.history.count(), 1)
        self.assertEqual(m.history.first().old_content, "v1")
    def test_unread_manager(self):
        Message.objects.create(sender=self.alice, receiver=self.bob, content="u1")
        Message.objects.create(sender=self.alice, receiver=self.bob, content="u2", read=True)
        self.assertEqual(Message.unread.for_user(self.bob).count(), 1)
    def test_thread_gather(self):
        root = Message.objects.create(sender=self.alice, receiver=self.bob, content="root")
        c1 = Message.objects.create(sender=self.bob, receiver=self.alice, content="c1", parent_message=root)
        c2 = Message.objects.create(sender=self.alice, receiver=self.bob, content="c2", parent_message=root)
        c11 = Message.objects.create(sender=self.bob, receiver=self.alice, content="c1.1", parent_message=c1)
        ids = {m.id for m in root.get_thread()}
        self.assertEqual(ids, {root.id, c1.id, c2.id, c11.id})
