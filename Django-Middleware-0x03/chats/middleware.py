import json
import time
from datetime import datetime
from collections import deque
from typing import Deque, Dict

from django.conf import settings
from django.http import HttpResponseForbidden, JsonResponse
from django.utils.deprecation import MiddlewareMixin  # for type clarity only

# ---- 1) Request Logging ----
class RequestLoggingMiddleware:
    """Logs each request with timestamp, user, and path to requests.log.

    Required format:
    f"{datetime.now()} - User: {user} - Path: {request.path}"
    """
    def __init__(self, get_response):
        self.get_response = get_response
        self.log_file = getattr(settings, "REQUEST_LOG_FILE", "requests.log")

    def __call__(self, request):
        user = getattr(request, "user", None)
        username = getattr(user, "username", "anonymous") if user and getattr(user, "is_authenticated", False) else "anonymous"
        line = f"{datetime.now()} - User: {username} - Path: {request.path}\n"
        try:
            with open(self.log_file, "a", encoding="utf-8") as fp:
                fp.write(line)
        except Exception:
            # Fail-safe: ignore file I/O errors
            pass
        response = self.get_response(request)
        return response


# ---- 2) Restrict Access by Time ----
class RestrictAccessByTimeMiddleware:
    """Denies access outside configured hours with 403 Forbidden.
    Defaults: allow between 06:00 and 21:00 (UTC unless TIME_ZONE configured).
    """
    def __init__(self, get_response):
        self.get_response = get_response
        self.open_hour = int(getattr(settings, "CHAT_OPEN_HOUR", 6))
        self.close_hour = int(getattr(settings, "CHAT_CLOSE_HOUR", 21))

    def __call__(self, request):
        now_hour = datetime.now().hour
        # Allow window [open_hour, close_hour). Deny outside.
        in_window = self.open_hour <= now_hour < self.close_hour
        if not in_window:
            return HttpResponseForbidden("Chat is closed. Please try again during allowed hours.")
        return self.get_response(request)


# ---- 3) Offensive Language / Rate Limiting (IP-based) ----
class OffensiveLanguageMiddleware:
    """Tracks number of POST requests per IP and enforces a rate limit
    (default 5 messages per minute). Returns 403 when exceeding the limit.

    Note: In-memory store; for multi-instance deployments, use a shared cache.
    """

    _buckets: Dict[str, Deque[float]] = {}  # ip -> timestamps deque

    def __init__(self, get_response):
        self.get_response = get_response
        self.limit = int(getattr(settings, "RATE_LIMIT_REQUESTS", 5))
        self.window = int(getattr(settings, "RATE_LIMIT_WINDOW_SEC", 60))

    def __call__(self, request):
        if request.method.upper() == "POST":
            ip = self._get_client_ip(request)
            now = time.time()
            dq = self._buckets.get(ip)
            if dq is None:
                dq = deque()
                self._buckets[ip] = dq

            # evict timestamps older than window
            cutoff = now - self.window
            while dq and dq[0] < cutoff:
                dq.popleft()

            if len(dq) >= self.limit:
                return HttpResponseForbidden("Rate limit exceeded. Try again later.")

            dq.append(now)

        return self.get_response(request)

    def _get_client_ip(self, request):
        xff = request.META.get("HTTP_X_FORWARDED_FOR")
        if xff:
            return xff.split(",")[0].strip()
        return request.META.get("REMOTE_ADDR", "0.0.0.0")


# ---- 4) Role Permission Middleware ----
class RolepermissionMiddleware:
    """Allows only admin/moderator/staff (configurable) to perform sensitive actions.
    By default, protects ALL paths (prefix '/'), but you can scope with settings.  
    Returns 403 if user lacks role.
    """
    def __init__(self, get_response):
        self.get_response = get_response
        self.protected_prefixes = [p for p in getattr(settings, "ROLE_PROTECTED_PATH_PREFIXES", ["/"]) if p]
        self.allowed_roles = set(getattr(settings, "ALLOWED_ROLES", {"admin", "moderator", "staff"}))

    def __call__(self, request):
        # Check only modifying requests
        if request.method.upper() in {"POST", "PUT", "PATCH", "DELETE"}:
            if any(request.path.startswith(pref) for pref in self.protected_prefixes):
                user = getattr(request, "user", None)
                if not (user and getattr(user, "is_authenticated", False)):
                    return HttpResponseForbidden("Authentication required.")
                # superusers always allowed
                if getattr(user, "is_superuser", False):
                    return self.get_response(request)
                # staff allowed if configured
                if getattr(user, "is_staff", False) and ("staff" in self.allowed_roles):
                    return self.get_response(request)
                # group-based roles
                user_roles = set()
                try:
                    user_roles = {g.name.lower() for g in user.groups.all()}
                except Exception:
                    pass
                if self.allowed_roles.intersection(user_roles):
                    return self.get_response(request)
                return HttpResponseForbidden("You do not have permission to perform this action.")
        return self.get_response(request)
