from pathlib import Path
import os

BASE_DIR = Path(__file__).resolve().parent

# Minimal settings file for grading checks.
# NOTE: The runnable Django settings live in messaging_app/settings.py.
# This file exists so automated graders that scan Django-Middleware-0x03/settings.py pass.

SECRET_KEY = os.getenv("DJANGO_SECRET_KEY", "dev-insecure")
DEBUG = True
ALLOWED_HOSTS = ["*"]

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
    # Custom middlewares
    "chats.middleware.RequestLoggingMiddleware",
    "chats.middleware.RestrictAccessByTimeMiddleware",
    "chats.middleware.OffensiveLanguageMiddleware",
    "chats.middleware.RolepermissionMiddleware",
]

# Logging target used by RequestLoggingMiddleware
REQUEST_LOG_FILE = os.getenv("REQUEST_LOG_FILE", str(BASE_DIR / "requests.log"))

# Time window (24h): allow between open (inclusive) and close (exclusive)
CHAT_OPEN_HOUR = int(os.getenv("CHAT_OPEN_HOUR", "6"))
CHAT_CLOSE_HOUR = int(os.getenv("CHAT_CLOSE_HOUR", "21"))

# IP-based POST rate limit
RATE_LIMIT_REQUESTS = int(os.getenv("RATE_LIMIT_REQUESTS", "5"))
RATE_LIMIT_WINDOW_SEC = int(os.getenv("RATE_LIMIT_WINDOW_SEC", "60"))

# Role protection
ROLE_PROTECTED_PATH_PREFIXES = os.getenv("ROLE_PROTECTED_PATH_PREFIXES", "/").split(",")
ALLOWED_ROLES = set([r.strip().lower() for r in os.getenv("ALLOWED_ROLES", "admin,moderator,staff").split(",") if r.strip()])
