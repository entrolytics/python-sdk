"""Type definitions for Entrolytics SDK."""

from dataclasses import dataclass, field
from typing import Any, Literal


@dataclass
class EventData:
    """Data for a custom event."""

    website_id: str
    event: str
    data: dict[str, Any] = field(default_factory=dict)
    url: str | None = None
    referrer: str | None = None
    user_id: str | None = None
    session_id: str | None = None
    user_agent: str | None = None
    ip_address: str | None = None
    timestamp: str | None = None


@dataclass
class PageViewData:
    """Data for a page view event."""

    website_id: str
    url: str
    referrer: str | None = None
    title: str | None = None
    user_id: str | None = None
    session_id: str | None = None
    user_agent: str | None = None
    ip_address: str | None = None
    timestamp: str | None = None


@dataclass
class IdentifyData:
    """Data for user identification."""

    website_id: str
    user_id: str
    traits: dict[str, Any] = field(default_factory=dict)
    timestamp: str | None = None


@dataclass
class TrackResponse:
    """Response from tracking API."""

    success: bool
    message: str | None = None
    error: str | None = None


# ============================================================================
# Phase 2: Web Vitals Types (requires entrolytics)
# ============================================================================

VitalMetric = Literal["LCP", "INP", "CLS", "TTFB", "FCP"]
VitalRating = Literal["good", "needs-improvement", "poor"]
NavigationType = Literal[
    "navigate", "reload", "back-forward", "back-forward-cache", "prerender", "restore"
]


@dataclass
class WebVitalData:
    """Data for a Web Vital metric. Requires entrolytics."""

    website_id: str
    metric: VitalMetric
    value: float
    rating: VitalRating
    delta: float | None = None
    id: str | None = None
    navigation_type: NavigationType | None = None
    attribution: dict[str, Any] | None = None
    url: str | None = None
    path: str | None = None
    session_id: str | None = None


# ============================================================================
# Phase 2: Form Analytics Types (requires entrolytics)
# ============================================================================

FormEventType = Literal[
    "start", "field_focus", "field_blur", "field_error", "submit", "abandon"
]


@dataclass
class FormEventData:
    """Data for a form interaction event. Requires entrolytics."""

    website_id: str
    event_type: FormEventType
    form_id: str
    url_path: str
    form_name: str | None = None
    field_name: str | None = None
    field_type: str | None = None
    field_index: int | None = None
    time_on_field: int | None = None
    time_since_start: int | None = None
    error_message: str | None = None
    success: bool | None = None
    session_id: str | None = None


# ============================================================================
# Phase 2: Deployment Types (requires entrolytics)
# ============================================================================

DeploymentSource = Literal[
    "vercel",
    "netlify",
    "cloudflare",
    "railway",
    "render",
    "fly",
    "heroku",
    "aws",
    "gcp",
    "azure",
    "custom",
]


@dataclass
class DeploymentData:
    """Data for deployment context registration. Requires entrolytics."""

    website_id: str
    deploy_id: str
    git_sha: str | None = None
    git_branch: str | None = None
    deploy_url: str | None = None
    source: DeploymentSource | None = None
