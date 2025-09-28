from pathlib import Path
from datetime import timedelta
import os

BASE_DIR = Path(__file__).resolve().parent.parent

SECRET_KEY = os.getenv("DJANGO_SECRET_KEY", "dev-insecure")
DEBUG = True
ALLOWED_HOSTS = ["*"]

INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "chats",
]

MIDDLEWARE = [
    # Django defaults
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",

    # Custom (after Authentication so request.user works)
    "chats.middleware.RequestLoggingMiddleware",        # log first
    "chats.middleware.RestrictAccessByTimeMiddleware",  # gate by time
    "chats.middleware.OffensiveLanguageMiddleware",     # rate limit posts
    "chats.middleware.RolepermissionMiddleware",        # enforce roles
]

ROOT_URLCONF = "messaging_app.urls"
WSGI_APPLICATION = "messaging_app.wsgi.application"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [BASE_DIR / "templates"],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.debug",
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
            ],
        },
    },
]

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": BASE_DIR / "db.sqlite3",
    }
}

LANGUAGE_CODE = "en-us"
TIME_ZONE = "UTC"
USE_I18N = True
USE_TZ = True

STATIC_URL = "static/"
DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

# ---- Custom Middleware Settings / Toggles ----
REQUEST_LOG_FILE = os.getenv("REQUEST_LOG_FILE", str(BASE_DIR / "requests.log"))

# Access window (24h): allow between OPEN_HOUR (inclusive) and CLOSE_HOUR (exclusive).
# Default: 06:00 - 21:00 (6AM to 9PM). Set env vars to adjust.
CHAT_OPEN_HOUR = int(os.getenv("CHAT_OPEN_HOUR", "6"))
CHAT_CLOSE_HOUR = int(os.getenv("CHAT_CLOSE_HOUR", "21"))

# Rate limit settings for OffensiveLanguageMiddleware (IP-based message rate limiting)
RATE_LIMIT_REQUESTS = int(os.getenv("RATE_LIMIT_REQUESTS", "5"))  # msgs per window
RATE_LIMIT_WINDOW_SEC = int(os.getenv("RATE_LIMIT_WINDOW_SEC", "60"))  # seconds

# Role permission settings
ROLE_PROTECTED_PATH_PREFIXES = os.getenv("ROLE_PROTECTED_PATH_PREFIXES", "/").split(",")  # paths needing elevated roles
ALLOWED_ROLES = set([r.strip().lower() for r in os.getenv("ALLOWED_ROLES", "admin,moderator,staff").split(",") if r.strip()])
