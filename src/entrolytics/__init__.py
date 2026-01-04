"""
Entrolytics Python SDK

First-party growth analytics for the edge.

Usage:
    from entrolytics import Entrolytics

    client = Entrolytics(api_key="ent_xxx")

    # Track events
    client.track(
        website_id="abc123",
        event="purchase",
        data={"revenue": 99.99, "currency": "USD"}
    )

    # Track page views
    client.page_view(
        website_id="abc123",
        url="/pricing",
        referrer="https://google.com"
    )

    # Identify users
    client.identify(
        website_id="abc123",
        user_id="user_456",
        traits={"plan": "pro"}
    )

    # Phase 2: Track Web Vitals (requires entrolytics)
    client.track_vital(
        website_id="abc123",
        metric="LCP",
        value=2500.0,
        rating="good"
    )

    # Phase 2: Track form events (requires entrolytics)
    client.track_form_event(
        website_id="abc123",
        event_type="submit",
        form_id="contact-form",
        url_path="/contact",
        success=True
    )

    # Phase 2: Set deployment context (requires entrolytics)
    client.set_deployment(
        website_id="abc123",
        deploy_id="deploy_123",
        git_sha="abc1234",
        source="vercel"
    )
"""

from entrolytics.client import Entrolytics, AsyncEntrolytics
from entrolytics.exceptions import (
    EntrolyticsError,
    AuthenticationError,
    ValidationError,
    RateLimitError,
    NetworkError,
)
from entrolytics.types import (
    # Core types
    EventData,
    PageViewData,
    IdentifyData,
    TrackResponse,
    # Phase 2: Web Vitals types
    VitalMetric,
    VitalRating,
    NavigationType,
    WebVitalData,
    # Phase 2: Form Analytics types
    FormEventType,
    FormEventData,
    # Phase 2: Deployment types
    DeploymentSource,
    DeploymentData,
)

__version__ = "1.1.0"
__all__ = [
    # Clients
    "Entrolytics",
    "AsyncEntrolytics",
    # Exceptions
    "EntrolyticsError",
    "AuthenticationError",
    "ValidationError",
    "RateLimitError",
    "NetworkError",
    # Core types
    "EventData",
    "PageViewData",
    "IdentifyData",
    "TrackResponse",
    # Phase 2: Web Vitals types
    "VitalMetric",
    "VitalRating",
    "NavigationType",
    "WebVitalData",
    # Phase 2: Form Analytics types
    "FormEventType",
    "FormEventData",
    # Phase 2: Deployment types
    "DeploymentSource",
    "DeploymentData",
]
