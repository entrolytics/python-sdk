"""FastAPI dependencies for Entrolytics."""

from __future__ import annotations

from typing import Any
from dataclasses import dataclass

from starlette.requests import Request

from entrolytics import AsyncEntrolytics


@dataclass
class EntrolyticsTracker:
    """
    Tracker instance for use in FastAPI routes.

    Provides convenience methods that automatically include request context.
    """

    client: AsyncEntrolytics
    website_id: str
    request: Request

    async def track(
        self,
        event: str,
        data: dict[str, Any] | None = None,
        *,
        user_id: str | None = None,
    ) -> None:
        """Track a custom event with request context."""
        url = str(self.request.url)
        referrer = self.request.headers.get("referer")
        user_agent = self.request.headers.get("user-agent")

        ip_address = None
        x_forwarded_for = self.request.headers.get("x-forwarded-for")
        if x_forwarded_for:
            ip_address = x_forwarded_for.split(",")[0].strip()
        elif self.request.client:
            ip_address = self.request.client.host

        # Use request state user_id if not provided
        if not user_id:
            user_id = getattr(self.request.state, "user_id", None)

        await self.client.track(
            website_id=self.website_id,
            event=event,
            data=data,
            url=url,
            referrer=referrer,
            user_agent=user_agent,
            ip_address=ip_address,
            user_id=user_id,
        )

    async def page_view(
        self,
        url: str | None = None,
        *,
        title: str | None = None,
        user_id: str | None = None,
    ) -> None:
        """Track a page view with request context."""
        if url is None:
            url = str(self.request.url)

        referrer = self.request.headers.get("referer")
        user_agent = self.request.headers.get("user-agent")

        ip_address = None
        x_forwarded_for = self.request.headers.get("x-forwarded-for")
        if x_forwarded_for:
            ip_address = x_forwarded_for.split(",")[0].strip()
        elif self.request.client:
            ip_address = self.request.client.host

        if not user_id:
            user_id = getattr(self.request.state, "user_id", None)

        await self.client.page_view(
            website_id=self.website_id,
            url=url,
            referrer=referrer,
            title=title,
            user_agent=user_agent,
            ip_address=ip_address,
            user_id=user_id,
        )

    async def identify(
        self,
        user_id: str,
        traits: dict[str, Any] | None = None,
    ) -> None:
        """Identify a user."""
        await self.client.identify(
            website_id=self.website_id,
            user_id=user_id,
            traits=traits,
        )


def get_entrolytics(
    website_id: str,
    api_key: str,
    *,
    host: str = "https://ng.entrolytics.click",
):
    """
    Create a FastAPI dependency for Entrolytics tracking.

    Usage:
        from fastapi import FastAPI, Depends
        from entrolytics.fastapi import get_entrolytics, EntrolyticsTracker

        app = FastAPI()
        tracker_dep = get_entrolytics(
            website_id="your-website-id",
            api_key="ent_xxx"
        )

        @app.post("/purchase")
        async def purchase(tracker: EntrolyticsTracker = Depends(tracker_dep)):
            await tracker.track("purchase", {"revenue": 99.99})
            return {"status": "ok"}
    """
    client = AsyncEntrolytics(api_key=api_key, host=host)

    async def dependency(request: Request) -> EntrolyticsTracker:
        return EntrolyticsTracker(
            client=client,
            website_id=website_id,
            request=request,
        )

    return dependency
