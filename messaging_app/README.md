# Building Robust APIs — Messaging App (Django + DRF)

This repository contains a minimal yet robust REST API for a messaging system,
aligned to your assignment tasks (0–5).

## Quick start

```bash
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate
pip install -r requirements.txt
python manage.py makemigrations
python manage.py migrate
python manage.py runserver 0.0.0.0:8000
```

## Apps & URLs

- App: `chats`
- API Base: `/api/`
  - `/api/conversations/`
  - `/api/messages/`
  - `/api/conversations/<id>/send_message/` (POST)

## Models

- `User` (extends `AbstractUser`) with UUID primary key, `phone_number`, `role`.
- `Conversation` with M2M `participants` to `User`.
- `Message` with FK `conversation`, FK `sender`, `message_body`, timestamps.

## Serializers

- `UserSerializer`, `ConversationSerializer` (nested `messages`), `MessageSerializer`.

## ViewSets

- `ConversationViewSet` (create/list/retrieve + `send_message` action)
- `MessageViewSet` (CRUD)

## Testing

```bash
python manage.py test
```

## Notes

- Custom user model is set via `AUTH_USER_MODEL = "chats.User"`.
- Database is SQLite for simplicity; swap `DATABASES` in `settings.py` for Postgres/MySQL in production.
