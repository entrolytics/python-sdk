"""Django utilities for Entrolytics tracking."""

from __future__ import annotations

from functools import lru_cache
from typing import Any

from entrolytics import Entrolytics


@lru_cache(maxsize=1)
def get_client() -> Entrolytics | None:
    """
    Get or create the Entrolytics client singleton.

    Reads configuration from Django settings:
        ENTROLYTICS = {
            'WEBSITE_ID': 'your-website-id',
            'API_KEY': 'ent_xxx',
            'HOST': 'https://ng.entrolytics.click',  # optional
        }
    """
    from django.conf import settings

    config = getattr(settings, "ENTROLYTICS", {})
    api_key = config.get("API_KEY")

    if not api_key:
        return None

    host = config.get("HOST", "https://ng.entrolytics.click")
    return Entrolytics(api_key=api_key, host=host)


def track(
    event: str,
    data: dict[str, Any] | None = None,
    *,
    website_id: str | None = None,
    user_id: str | None = None,
    request: Any = None,
) -> None:
    """
    Track a custom event.

    Args:
        event: Event name
        data: Event data
        website_id: Override website ID from settings
        user_id: User identifier
        request: Django request object (for IP/user agent)

    Usage:
        from entrolytics.django import track

        def my_view(request):
            track('purchase', {'revenue': 99.99}, request=request)
    """
    from django.conf import settings

    client = get_client()
    if not client:
        return

    config = getattr(settings, "ENTROLYTICS", {})
    site_id = website_id or config.get("WEBSITE_ID")

    if not site_id:
        return

    kwargs: dict[str, Any] = {
        "website_id": site_id,
        "event": event,
        "data": data,
    }

    if user_id:
        kwargs["user_id"] = user_id

    if request:
        kwargs["user_agent"] = request.META.get("HTTP_USER_AGENT")
        x_forwarded_for = request.META.get("HTTP_X_FORWARDED_FOR")
        if x_forwarded_for:
            kwargs["ip_address"] = x_forwarded_for.split(",")[0].strip()
        else:
            kwargs["ip_address"] = request.META.get("REMOTE_ADDR")

        if not user_id and hasattr(request, "user") and request.user.is_authenticated:
            kwargs["user_id"] = str(request.user.pk)

    client.track(**kwargs)


def page_view(
    url: str,
    *,
    website_id: str | None = None,
    referrer: str | None = None,
    title: str | None = None,
    user_id: str | None = None,
    request: Any = None,
) -> None:
    """
    Track a page view.

    Args:
        url: Page URL
        website_id: Override website ID from settings
        referrer: Referrer URL
        title: Page title
        user_id: User identifier
        request: Django request object
    """
    from django.conf import settings

    client = get_client()
    if not client:
        return

    config = getattr(settings, "ENTROLYTICS", {})
    site_id = website_id or config.get("WEBSITE_ID")

    if not site_id:
        return

    kwargs: dict[str, Any] = {
        "website_id": site_id,
        "url": url,
        "referrer": referrer,
        "title": title,
    }

    if user_id:
        kwargs["user_id"] = user_id

    if request:
        kwargs["user_agent"] = request.META.get("HTTP_USER_AGENT")
        x_forwarded_for = request.META.get("HTTP_X_FORWARDED_FOR")
        if x_forwarded_for:
            kwargs["ip_address"] = x_forwarded_for.split(",")[0].strip()
        else:
            kwargs["ip_address"] = request.META.get("REMOTE_ADDR")

        if not user_id and hasattr(request, "user") and request.user.is_authenticated:
            kwargs["user_id"] = str(request.user.pk)

    client.page_view(**kwargs)


def identify(
    user_id: str,
    traits: dict[str, Any] | None = None,
    *,
    website_id: str | None = None,
) -> None:
    """
    Identify a user with traits.

    Args:
        user_id: User identifier
        traits: User traits
        website_id: Override website ID from settings

    Usage:
        from entrolytics.django import identify

        def login_view(request):
            # After successful login
            identify(str(request.user.pk), {
                'email': request.user.email,
                'plan': 'pro'
            })
    """
    from django.conf import settings

    client = get_client()
    if not client:
        return

    config = getattr(settings, "ENTROLYTICS", {})
    site_id = website_id or config.get("WEBSITE_ID")

    if not site_id:
        return

    client.identify(
        website_id=site_id,
        user_id=user_id,
        traits=traits,
    )
