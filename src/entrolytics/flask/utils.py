"""Flask utilities for Entrolytics tracking."""

from __future__ import annotations

from typing import Any

from flask import current_app, g, request


def _get_extension():
    """Get the Entrolytics extension from the current app."""
    return current_app.extensions.get("entrolytics")


def track(
    event: str,
    data: dict[str, Any] | None = None,
    *,
    user_id: str | None = None,
) -> None:
    """
    Track a custom event.

    Usage:
        from entrolytics.flask import track

        @app.route('/purchase', methods=['POST'])
        def purchase():
            track('purchase', {'revenue': 99.99})
            return {'status': 'ok'}
    """
    ext = _get_extension()
    if ext:
        ext.track(event, data, user_id=user_id)


def page_view(
    url: str | None = None,
    *,
    title: str | None = None,
    user_id: str | None = None,
) -> None:
    """
    Track a page view.

    Usage:
        from entrolytics.flask import page_view

        @app.route('/dashboard')
        def dashboard():
            page_view(title='Dashboard')
            return render_template('dashboard.html')
    """
    ext = _get_extension()
    if not ext or not ext.client or not ext.website_id:
        return

    if url is None:
        url = request.url

    referrer = request.referrer
    user_agent = request.user_agent.string

    ip_address = request.headers.get("X-Forwarded-For")
    ip_address = ip_address.split(",")[0].strip() if ip_address else request.remote_addr

    if not user_id:
        user_id = getattr(g, "user_id", None)

    ext.client.page_view(
        website_id=ext.website_id,
        url=url,
        referrer=referrer,
        title=title,
        user_agent=user_agent,
        ip_address=ip_address,
        user_id=user_id,
    )


def identify(
    user_id: str,
    traits: dict[str, Any] | None = None,
) -> None:
    """
    Identify a user with traits.

    Usage:
        from entrolytics.flask import identify

        @app.route('/login', methods=['POST'])
        def login():
            # After successful authentication
            identify(user.id, {'email': user.email, 'plan': 'pro'})
            return redirect('/dashboard')
    """
    ext = _get_extension()
    if ext:
        ext.identify(user_id, traits)
