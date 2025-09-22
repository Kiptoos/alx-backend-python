from django.test import TestCase
from django.urls import reverse
from rest_framework.test import APIClient
from .models import User, Conversation, Message

class APITests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user1 = User.objects.create_user(username="u1", password="pass", email="u1@example.com")
        self.user2 = User.objects.create_user(username="u2", password="pass", email="u2@example.com")

    def test_create_conversation_and_send_message(self):
        # Create conversation
        res = self.client.post("/api/conversations/", {
            "participants": [str(self.user1.id), str(self.user2.id)]
        }, format="json")
        self.assertEqual(res.status_code, 201, res.content)
        conv_id = res.data["id"]

        # Send message via conversations/<id>/send_message
        res2 = self.client.post(f"/api/conversations/{conv_id}/send_message/", {
            "sender_id": str(self.user1.id),
            "message_body": "Hello there!"
        }, format="json")
        self.assertEqual(res2.status_code, 201, res2.content)
        self.assertEqual(res2.data["message_body"], "Hello there!")

        # List messages
        res3 = self.client.get("/api/messages/")
        self.assertEqual(res3.status_code, 200)
        self.assertTrue(len(res3.data) >= 1)
