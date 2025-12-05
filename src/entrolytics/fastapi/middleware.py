"""FastAPI middleware for automatic tracking."""

from __future__ import annotations

import logging
from typing import Callable

from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import Response

from entrolytics import AsyncEntrolytics

logger = logging.getLogger(__name__)


class EntrolyticsMiddleware(BaseHTTPMiddleware):
    """
    FastAPI/Starlette middleware for automatic page view tracking.

    Usage:
        from fastapi import FastAPI
        from entrolytics.fastapi import EntrolyticsMiddleware

        app = FastAPI()
        app.add_middleware(
            EntrolyticsMiddleware,
            website_id="your-website-id",
            api_key="ent_xxx",
        )
    """

    def __init__(
        self,
        app: Callable,
        website_id: str,
        api_key: str,
        *,
        host: str = "https://ng.entrolytics.click",
        track_paths: list[str] | None = None,
        exclude_paths: list[str] | None = None,
    ) -> None:
        """
        Initialize the middleware.

        Args:
            app: The ASGI app
            website_id: Your Entrolytics website ID
            api_key: Your Entrolytics API key
            host: Entrolytics host URL
            track_paths: Only track these path prefixes (if set)
            exclude_paths: Exclude these path prefixes
        """
        super().__init__(app)
        self.website_id = website_id
        self.api_key = api_key
        self.host = host
        self.track_paths = track_paths
        self.exclude_paths = exclude_paths or ["/docs", "/redoc", "/openapi.json", "/health"]
        self._client: AsyncEntrolytics | None = None

    @property
    def client(self) -> AsyncEntrolytics:
        """Lazy-initialize the async client."""
        if self._client is None:
            self._client = AsyncEntrolytics(
                api_key=self.api_key,
                host=self.host,
            )
        return self._client

    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        """Process the request and track page views."""
        response = await call_next(request)

        # Only track successful GET requests
        if request.method != "GET" or response.status_code >= 400:
            return response

        # Check if we should track this path
        if not self._should_track(request.url.path):
            return response

        # Track asynchronously
        try:
            await self._track_page_view(request)
        except Exception as e:
            logger.warning(f"Entrolytics tracking failed: {e}")

        return response

    def _should_track(self, path: str) -> bool:
        """Determine if this path should be tracked."""
        # Check exclusions first
        for excluded in self.exclude_paths:
            if path.startswith(excluded):
                return False

        # If track_paths is set, only track those
        if self.track_paths:
            for included in self.track_paths:
                if path.startswith(included):
                    return True
            return False

        return True

    async def _track_page_view(self, request: Request) -> None:
        """Track a page view for the request."""
        url = str(request.url)
        referrer = request.headers.get("referer")
        user_agent = request.headers.get("user-agent")

        # Get client IP
        ip_address = None
        x_forwarded_for = request.headers.get("x-forwarded-for")
        if x_forwarded_for:
            ip_address = x_forwarded_for.split(",")[0].strip()
        elif request.client:
            ip_address = request.client.host

        # Get user ID from state if set
        user_id = getattr(request.state, "user_id", None)

        await self.client.page_view(
            website_id=self.website_id,
            url=url,
            referrer=referrer,
            user_agent=user_agent,
            ip_address=ip_address,
            user_id=user_id,
        )
