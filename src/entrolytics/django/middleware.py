"""Django middleware for automatic page view tracking."""

from __future__ import annotations

from typing import TYPE_CHECKING, Callable
import logging

from entrolytics.django.utils import get_client

if TYPE_CHECKING:
    from django.http import HttpRequest, HttpResponse

logger = logging.getLogger(__name__)


class EntrolyticsMiddleware:
    """
    Django middleware for automatic page view tracking.

    Add to MIDDLEWARE in settings.py:
        MIDDLEWARE = [
            'entrolytics.django.EntrolyticsMiddleware',
            ...
        ]

    Configure in settings.py:
        ENTROLYTICS = {
            'WEBSITE_ID': 'your-website-id',
            'API_KEY': 'ent_xxx',  # For server-side tracking
            'TRACK_ADMIN': False,  # Skip admin pages (default)
            'TRACK_STATIC': False,  # Skip static files (default)
            'EXCLUDED_PATHS': ['/health', '/api/'],  # Paths to skip
        }
    """

    def __init__(self, get_response: Callable[[HttpRequest], HttpResponse]) -> None:
        self.get_response = get_response
        self._client = None

    def __call__(self, request: HttpRequest) -> HttpResponse:
        response = self.get_response(request)

        # Only track successful GET requests
        if request.method != "GET" or response.status_code >= 400:
            return response

        # Skip if configured to do so
        if not self._should_track(request):
            return response

        # Track page view
        try:
            self._track_page_view(request)
        except Exception as e:
            logger.warning(f"Entrolytics tracking failed: {e}")

        return response

    def _should_track(self, request: HttpRequest) -> bool:
        """Determine if this request should be tracked."""
        from django.conf import settings

        config = getattr(settings, "ENTROLYTICS", {})
        path = request.path

        # Skip admin pages
        if not config.get("TRACK_ADMIN", False):
            if path.startswith("/admin"):
                return False

        # Skip static/media files
        if not config.get("TRACK_STATIC", False):
            static_url = getattr(settings, "STATIC_URL", "/static/")
            media_url = getattr(settings, "MEDIA_URL", "/media/")
            if path.startswith(static_url) or path.startswith(media_url):
                return False

        # Check excluded paths
        excluded = config.get("EXCLUDED_PATHS", [])
        for excluded_path in excluded:
            if path.startswith(excluded_path):
                return False

        return True

    def _track_page_view(self, request: HttpRequest) -> None:
        """Track a page view for the request."""
        from django.conf import settings

        config = getattr(settings, "ENTROLYTICS", {})
        website_id = config.get("WEBSITE_ID")

        if not website_id:
            return

        client = get_client()
        if not client:
            return

        # Build full URL
        url = request.build_absolute_uri()

        # Get referrer
        referrer = request.META.get("HTTP_REFERER")

        # Get user agent
        user_agent = request.META.get("HTTP_USER_AGENT")

        # Get IP address
        ip_address = self._get_client_ip(request)

        # Get user ID if authenticated
        user_id = None
        if hasattr(request, "user") and request.user.is_authenticated:
            user_id = str(request.user.pk)

        client.page_view(
            website_id=website_id,
            url=url,
            referrer=referrer,
            user_agent=user_agent,
            ip_address=ip_address,
            user_id=user_id,
        )

    def _get_client_ip(self, request: HttpRequest) -> str | None:
        """Extract client IP from request."""
        x_forwarded_for = request.META.get("HTTP_X_FORWARDED_FOR")
        if x_forwarded_for:
            return x_forwarded_for.split(",")[0].strip()
        return request.META.get("REMOTE_ADDR")
