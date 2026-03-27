"""Flask extension for Entrolytics."""

from __future__ import annotations

import logging
from typing import TYPE_CHECKING

from flask import g, request

from entrolytics import Entrolytics as EntrolyticsClient

if TYPE_CHECKING:
    from flask import Flask

logger = logging.getLogger(__name__)


class Entrolytics:
    """
    Flask extension for Entrolytics analytics.

    Usage:
        from flask import Flask
        from entrolytics.flask import FlaskEntrolytics

        app = Flask(__name__)
        app.config['ENTROLYTICS_WEBSITE_ID'] = 'your-website-id'
        app.config['ENTROLYTICS_API_KEY'] = 'ent_xxx'

        entrolytics = FlaskEntrolytics(app)

        # Or with factory pattern:
        entrolytics = FlaskEntrolytics()
        entrolytics.init_app(app)
    """

    def __init__(self, app: Flask | None = None) -> None:
        self._client: EntrolyticsClient | None = None
        self.website_id: str | None = None

        if app is not None:
            self.init_app(app)

    def init_app(self, app: Flask) -> None:
        """Initialize the extension with a Flask app."""
        app.config.setdefault("ENTROLYTICS_HOST", "https://entrolytics.click")
        app.config.setdefault("ENTROLYTICS_AUTO_TRACK", False)
        app.config.setdefault("ENTROLYTICS_EXCLUDE_PATHS", ["/static", "/health"])

        self.website_id = app.config.get("ENTROLYTICS_WEBSITE_ID")
        api_key = app.config.get("ENTROLYTICS_API_KEY")
        host = app.config.get("ENTROLYTICS_HOST")

        if api_key:
            self._client = EntrolyticsClient(api_key=api_key, host=host)

        # Register extension
        if not hasattr(app, "extensions"):
            app.extensions = {}
        app.extensions["entrolytics"] = self

        # Add request hooks if auto_track is enabled
        if app.config.get("ENTROLYTICS_AUTO_TRACK"):
            app.after_request(self._after_request)

    @property
    def client(self) -> EntrolyticsClient | None:
        """Get the Entrolytics client."""
        return self._client

    def _after_request(self, response):
        """Track page views after request."""
        if not self._client or not self.website_id:
            return response

        # Only track GET requests with successful responses
        if request.method != "GET" or response.status_code >= 400:
            return response

        # Check excluded paths
        from flask import current_app

        excluded = current_app.config.get("ENTROLYTICS_EXCLUDE_PATHS", [])
        for path in excluded:
            if request.path.startswith(path):
                return response

        try:
            self._track_page_view()
        except Exception as e:
            logger.warning(f"Entrolytics tracking failed: {e}")

        return response

    def _track_page_view(self) -> None:
        """Track a page view."""
        if not self._client or not self.website_id:
            return

        url = request.url
        referrer = request.referrer
        user_agent = request.user_agent.string

        # Get IP address
        ip_address = request.headers.get("X-Forwarded-For")
        ip_address = ip_address.split(",")[0].strip() if ip_address else request.remote_addr

        # Get user ID from g if set
        user_id = getattr(g, "user_id", None)

        self._client.page_view(
            website_id=self.website_id,
            url=url,
            referrer=referrer,
            user_agent=user_agent,
            ip_address=ip_address,
            user_id=user_id,
        )

    def track(
        self,
        event: str,
        data: dict | None = None,
        *,
        user_id: str | None = None,
    ) -> None:
        """
        Track a custom event.

        Args:
            event: Event name
            data: Event data
            user_id: User identifier
        """
        if not self._client or not self.website_id:
            return

        user_agent = request.user_agent.string if request else None

        ip_address = None
        if request:
            ip_address = request.headers.get("X-Forwarded-For")
            ip_address = ip_address.split(",")[0].strip() if ip_address else request.remote_addr

        if not user_id:
            user_id = getattr(g, "user_id", None)

        self._client.track(
            website_id=self.website_id,
            event=event,
            data=data,
            user_agent=user_agent,
            ip_address=ip_address,
            user_id=user_id,
        )

    def identify(
        self,
        user_id: str,
        traits: dict | None = None,
    ) -> None:
        """
        Identify a user.

        Args:
            user_id: User identifier
            traits: User traits
        """
        if not self._client or not self.website_id:
            return

        self._client.identify(
            website_id=self.website_id,
            user_id=user_id,
            traits=traits,
        )
