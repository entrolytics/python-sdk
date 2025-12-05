"""Type definitions for Entrolytics SDK."""

from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Literal, Optional


@dataclass
class EventData:
    """Data for a custom event."""

    website_id: str
    event: str
    data: dict[str, Any] = field(default_factory=dict)
    url: Optional[str] = None
    referrer: Optional[str] = None
    user_id: Optional[str] = None
    session_id: Optional[str] = None
    user_agent: Optional[str] = None
    ip_address: Optional[str] = None
    timestamp: Optional[str] = None


@dataclass
class PageViewData:
    """Data for a page view event."""

    website_id: str
    url: str
    referrer: Optional[str] = None
    title: Optional[str] = None
    user_id: Optional[str] = None
    session_id: Optional[str] = None
    user_agent: Optional[str] = None
    ip_address: Optional[str] = None
    timestamp: Optional[str] = None


@dataclass
class IdentifyData:
    """Data for user identification."""

    website_id: str
    user_id: str
    traits: dict[str, Any] = field(default_factory=dict)
    timestamp: Optional[str] = None


@dataclass
class TrackResponse:
    """Response from tracking API."""

    success: bool
    message: Optional[str] = None
    error: Optional[str] = None


# ============================================================================
# Phase 2: Web Vitals Types (requires entrolytics-ng)
# ============================================================================

VitalMetric = Literal["LCP", "INP", "CLS", "TTFB", "FCP"]
VitalRating = Literal["good", "needs-improvement", "poor"]
NavigationType = Literal[
    "navigate", "reload", "back-forward", "back-forward-cache", "prerender", "restore"
]


@dataclass
class WebVitalData:
    """Data for a Web Vital metric. Requires entrolytics-ng."""

    website_id: str
    metric: VitalMetric
    value: float
    rating: VitalRating
    delta: Optional[float] = None
    id: Optional[str] = None
    navigation_type: Optional[NavigationType] = None
    attribution: Optional[dict[str, Any]] = None
    url: Optional[str] = None
    path: Optional[str] = None
    session_id: Optional[str] = None


# ============================================================================
# Phase 2: Form Analytics Types (requires entrolytics-ng)
# ============================================================================

FormEventType = Literal[
    "start", "field_focus", "field_blur", "field_error", "submit", "abandon"
]


@dataclass
class FormEventData:
    """Data for a form interaction event. Requires entrolytics-ng."""

    website_id: str
    event_type: FormEventType
    form_id: str
    url_path: str
    form_name: Optional[str] = None
    field_name: Optional[str] = None
    field_type: Optional[str] = None
    field_index: Optional[int] = None
    time_on_field: Optional[int] = None
    time_since_start: Optional[int] = None
    error_message: Optional[str] = None
    success: Optional[bool] = None
    session_id: Optional[str] = None


# ============================================================================
# Phase 2: Deployment Types (requires entrolytics-ng)
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
    """Data for deployment context registration. Requires entrolytics-ng."""

    website_id: str
    deploy_id: str
    git_sha: Optional[str] = None
    git_branch: Optional[str] = None
    deploy_url: Optional[str] = None
    source: Optional[DeploymentSource] = None
