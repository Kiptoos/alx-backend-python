# Django-Middleware-0x03

This project demonstrates custom Django middleware for:
- Request logging
- Time-based access restriction
- IP-based POST rate limiting (5/min by default)
- Role-based permission checks

## Quickstart

```bash
pip install django
python manage.py migrate
python manage.py runserver
```

- Visit `/ping/` to test a simple endpoint.
- Check `requests.log` for logged entries.
- Adjust behavior via environment variables in `messaging_app/settings.py`.
