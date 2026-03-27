"""Main Entrolytics client classes."""

from __future__ import annotations

from typing import Any
from uuid import uuid4

import httpx

from entrolytics.exceptions import (
    AuthenticationError,
    EntrolyticsError,
    NetworkError,
    RateLimitError,
    ValidationError,
)
from entrolytics.types import (
    DeploymentSource,
    FormEventType,
    NavigationType,
    TrackResponse,
    VitalMetric,
    VitalRating,
)

DEFAULT_HOST = "https://entrolytics.click"
DEFAULT_TIMEOUT = 10.0


def _generate_uuid() -> str:
    return str(uuid4())


def _normalize_url(host: str, raw_url: str | None, fallback_path: str) -> str:
    if raw_url and (raw_url.startswith("http://") or raw_url.startswith("https://")):
        return raw_url

    path = raw_url or fallback_path
    if not path.startswith("/"):
        path = f"/{path}"

    return f"{host.rstrip('/')}{path}"


def _normalize_referrer(referrer: str | None) -> str | None:
    if not referrer:
        return None
    if referrer.startswith("http://") or referrer.startswith("https://"):
        return referrer
    return None


class Entrolytics:
    """
    Synchronous Entrolytics client for server-side tracking.

    Usage:
        client = Entrolytics(api_key="ent_xxx")
        client.track(website_id="abc123", event="purchase", data={"revenue": 99.99})
    """

    def __init__(
        self,
        api_key: str,
        *,
        host: str = DEFAULT_HOST,
        timeout: float = DEFAULT_TIMEOUT,
    ) -> None:
        """
        Initialize the Entrolytics client.

        Args:
            api_key: Your Entrolytics API key (starts with 'ent_')
            host: Entrolytics host URL (for self-hosted instances)
            timeout: Request timeout in seconds
        """
        if not api_key:
            raise AuthenticationError("API key is required")

        self.api_key = api_key
        self.host = host.rstrip("/")
        self.timeout = timeout
        self._client: httpx.Client | None = None

    @property
    def client(self) -> httpx.Client:
        """Lazy-initialize the HTTP client."""
        if self._client is None:
            self._client = httpx.Client(
                base_url=self.host,
                timeout=self.timeout,
                headers={
                    "x-api-key": self.api_key,
                    "Content-Type": "application/json",
                    "User-Agent": "entrolytics-python/1.1.0",
                },
            )
        return self._client

    def close(self) -> None:
        """Close the HTTP client."""
        if self._client is not None:
            self._client.close()
            self._client = None

    def __enter__(self) -> Entrolytics:
        return self

    def __exit__(self, *args: Any) -> None:
        self.close()

    def _handle_response(self, response: httpx.Response) -> TrackResponse:
        """Handle API response and raise appropriate exceptions."""
        if response.status_code in (200, 201, 202):
            return TrackResponse(success=True)

        if response.status_code == 401:
            raise AuthenticationError()

        if response.status_code == 400:
            try:
                data = response.json()
                message = data.get("error", "Invalid request")
            except Exception:
                message = "Invalid request"
            raise ValidationError(message)

        if response.status_code == 429:
            retry_after = response.headers.get("Retry-After")
            raise RateLimitError(
                retry_after=int(retry_after) if retry_after else None
            )

        raise EntrolyticsError(
            f"Request failed with status {response.status_code}",
            status_code=response.status_code,
        )

    def track(
        self,
        website_id: str,
        event: str,
        data: dict[str, Any] | None = None,
        *,
        url: str | None = None,
        referrer: str | None = None,
        user_id: str | None = None,
        session_id: str | None = None,
        user_agent: str | None = None,
        ip_address: str | None = None,
    ) -> TrackResponse:
        """
        Track a custom event.

        Args:
            website_id: Your Entrolytics website ID
            event: Event name (e.g., 'purchase', 'signup', 'click')
            data: Additional event data (e.g., revenue, product_id)
            url: Page URL where event occurred
            referrer: Referrer URL
            user_id: User identifier for logged-in users
            session_id: Session identifier
            user_agent: User agent string
            ip_address: Client IP address (for geo data)

        Returns:
            TrackResponse with success status
        """
        if not website_id:
            raise ValidationError("website_id is required")
        if not event:
            raise ValidationError("event is required")

        properties = dict(data or {})
        if user_id:
            properties["distinctId"] = user_id

        payload: dict[str, Any] = {
            "websiteId": website_id,
            "sessionId": session_id or _generate_uuid(),
            "visitorId": _generate_uuid(),
            "url": _normalize_url(self.host, url, "/track"),
            "eventType": "custom_event",
            "eventName": event,
            "properties": properties,
        }

        normalized_referrer = _normalize_referrer(referrer)
        if normalized_referrer:
            payload["referrer"] = normalized_referrer

        headers = {}
        if user_agent:
            headers["User-Agent"] = user_agent
        if ip_address:
            headers["X-Forwarded-For"] = ip_address

        try:
            response = self.client.post("/collect", json=payload, headers=headers)
            return self._handle_response(response)
        except httpx.RequestError as e:
            raise NetworkError(f"Request failed: {e}") from e

    def page_view(
        self,
        website_id: str,
        url: str,
        *,
        referrer: str | None = None,
        title: str | None = None,
        user_id: str | None = None,
        session_id: str | None = None,
        user_agent: str | None = None,
        ip_address: str | None = None,
    ) -> TrackResponse:
        """
        Track a page view.

        Args:
            website_id: Your Entrolytics website ID
            url: Page URL
            referrer: Referrer URL
            title: Page title
            user_id: User identifier
            session_id: Session identifier
            user_agent: User agent string
            ip_address: Client IP address

        Returns:
            TrackResponse with success status
        """
        if not website_id:
            raise ValidationError("website_id is required")
        if not url:
            raise ValidationError("url is required")

        properties: dict[str, Any] = {}
        if title:
            properties["title"] = title
        if user_id:
            properties["distinctId"] = user_id

        payload: dict[str, Any] = {
            "websiteId": website_id,
            "sessionId": session_id or _generate_uuid(),
            "visitorId": _generate_uuid(),
            "url": _normalize_url(self.host, url, "/"),
            "eventType": "pageview",
            "properties": properties,
        }

        normalized_referrer = _normalize_referrer(referrer)
        if normalized_referrer:
            payload["referrer"] = normalized_referrer

        headers = {}
        if user_agent:
            headers["User-Agent"] = user_agent
        if ip_address:
            headers["X-Forwarded-For"] = ip_address

        try:
            response = self.client.post("/collect", json=payload, headers=headers)
            return self._handle_response(response)
        except httpx.RequestError as e:
            raise NetworkError(f"Request failed: {e}") from e

    def identify(
        self,
        website_id: str,
        user_id: str,
        traits: dict[str, Any] | None = None,
    ) -> TrackResponse:
        """
        Identify a user with traits.

        Args:
            website_id: Your Entrolytics website ID
            user_id: Unique user identifier
            traits: User traits (e.g., email, plan, company)

        Returns:
            TrackResponse with success status
        """
        if not website_id:
            raise ValidationError("website_id is required")
        if not user_id:
            raise ValidationError("user_id is required")

        payload: dict[str, Any] = {
            "websiteId": website_id,
            "sessionId": _generate_uuid(),
            "visitorId": _generate_uuid(),
            "url": _normalize_url(self.host, "/identify", "/identify"),
            "eventType": "custom_event",
            "eventName": "identify",
            "properties": {
                "distinctId": user_id,
                **(traits or {}),
            },
        }

        try:
            response = self.client.post("/collect", json=payload)
            return self._handle_response(response)
        except httpx.RequestError as e:
            raise NetworkError(f"Request failed: {e}") from e

    # ========================================================================
    # Phase 2: Web Vitals (requires entrolytics)
    # ========================================================================

    def track_vital(
        self,
        website_id: str,
        metric: VitalMetric,
        value: float,
        rating: VitalRating,
        *,
        delta: float | None = None,
        id: str | None = None,
        navigation_type: NavigationType | None = None,
        attribution: dict[str, Any] | None = None,
        url: str | None = None,
        path: str | None = None,
        session_id: str | None = None,
        visitor_id: str | None = None,
    ) -> TrackResponse:
        """
        Track a Web Vital metric.

        Note: This feature requires entrolytics.

        Args:
            website_id: Your Entrolytics website ID
            metric: Vital type (LCP, INP, CLS, TTFB, or FCP)
            value: Metric value in milliseconds (except CLS which is unitless)
            rating: Performance rating (good, needs-improvement, or poor)
            delta: Difference from previous value
            id: Unique identifier for deduplication
            navigation_type: How the page was navigated to
            attribution: Debug information about the metric
            url: Full page URL
            path: URL path component
            session_id: Session identifier

        Returns:
            TrackResponse with success status
        """
        if not website_id:
            raise ValidationError("website_id is required")
        if not metric:
            raise ValidationError("metric is required (LCP, INP, CLS, TTFB, or FCP)")
        if not rating:
            raise ValidationError("rating is required (good, needs-improvement, or poor)")

        payload: dict[str, Any] = {
            "websiteId": website_id,
            "visitorId": visitor_id or _generate_uuid(),
            "sessionId": session_id or _generate_uuid(),
            "url": _normalize_url(self.host, url, "/vital"),
            "path": path or "/vital",
            "metricName": metric,
            "metricValue": value,
        }

        try:
            response = self.client.post("/api/collect/vitals", json=payload)
            return self._handle_response(response)
        except httpx.RequestError as e:
            raise NetworkError(f"Request failed: {e}") from e

    # ========================================================================
    # Phase 2: Form Analytics (requires entrolytics)
    # ========================================================================

    def track_form_event(
        self,
        website_id: str,
        event_type: FormEventType,
        form_id: str,
        url_path: str,
        *,
        form_name: str | None = None,
        field_name: str | None = None,
        field_type: str | None = None,
        field_index: int | None = None,
        time_on_field: int | None = None,
        time_since_start: int | None = None,
        error_message: str | None = None,
        success: bool | None = None,
        session_id: str | None = None,
        visitor_id: str | None = None,
    ) -> TrackResponse:
        """
        Track a form interaction event.

        Note: This feature requires entrolytics.

        Args:
            website_id: Your Entrolytics website ID
            event_type: Form event type (start, field_focus, field_blur, etc.)
            form_id: Unique form identifier
            url_path: Page path where the form is located
            form_name: Human-readable form name
            field_name: Field name (for field events)
            field_type: Input type (text, email, select, etc.)
            field_index: Position of the field in the form
            time_on_field: Milliseconds spent on the field
            time_since_start: Milliseconds since form interaction started
            error_message: Validation error message (for error events)
            success: Whether the submission was successful
            session_id: Session identifier

        Returns:
            TrackResponse with success status
        """
        if not website_id:
            raise ValidationError("website_id is required")
        if not event_type:
            raise ValidationError("event_type is required")
        if not form_id:
            raise ValidationError("form_id is required")
        if not url_path:
            raise ValidationError("url_path is required")

        payload: dict[str, Any] = {
            "websiteId": website_id,
            "visitorId": visitor_id or _generate_uuid(),
            "sessionId": session_id or _generate_uuid(),
            "eventType": event_type,
            "formId": form_id,
            "urlPath": url_path,
        }

        if form_name:
            payload["formName"] = form_name
        if field_name:
            payload["fieldName"] = field_name
        if field_type:
            payload["fieldType"] = field_type
        if field_index is not None:
            payload["fieldIndex"] = field_index
        if time_on_field is not None:
            payload["timeOnField"] = time_on_field
        if time_since_start is not None:
            payload["timeSinceStart"] = time_since_start
        if error_message:
            payload["errorMessage"] = error_message
        if success is not None:
            payload["success"] = success
        try:
            response = self.client.post("/api/collect/forms", json=payload)
            return self._handle_response(response)
        except httpx.RequestError as e:
            raise NetworkError(f"Request failed: {e}") from e

    # ========================================================================
    # Phase 2: Deployment Tracking (requires entrolytics)
    # ========================================================================

    def set_deployment(
        self,
        website_id: str,
        deploy_id: str,
        *,
        git_sha: str | None = None,
        git_branch: str | None = None,
        deploy_url: str | None = None,
        source: DeploymentSource | None = None,
    ) -> TrackResponse:
        """
        Register deployment context.

        Note: This feature requires entrolytics.

        Args:
            website_id: Your Entrolytics website ID
            deploy_id: Unique deployment identifier
            git_sha: Git commit SHA
            git_branch: Git branch name
            deploy_url: Deployment URL
            source: Deployment platform (vercel, netlify, etc.)

        Returns:
            TrackResponse with success status
        """
        if not website_id:
            raise ValidationError("website_id is required")
        if not deploy_id:
            raise ValidationError("deploy_id is required")

        payload: dict[str, Any] = {
            "website": website_id,
            "deployId": deploy_id,
        }

        if git_sha:
            payload["gitSha"] = git_sha
        if git_branch:
            payload["gitBranch"] = git_branch
        if deploy_url:
            payload["deployUrl"] = deploy_url
        if source:
            payload["source"] = source

        try:
            response = self.client.post(
                f"/api/websites/{website_id}/deployments", json=payload
            )
            return self._handle_response(response)
        except httpx.RequestError as e:
            raise NetworkError(f"Request failed: {e}") from e


class AsyncEntrolytics:
    """
    Asynchronous Entrolytics client for server-side tracking.

    Usage:
        async with AsyncEntrolytics(api_key="ent_xxx") as client:
            await client.track(website_id="abc123", event="purchase")
    """

    def __init__(
        self,
        api_key: str,
        *,
        host: str = DEFAULT_HOST,
        timeout: float = DEFAULT_TIMEOUT,
    ) -> None:
        """
        Initialize the async Entrolytics client.

        Args:
            api_key: Your Entrolytics API key
            host: Entrolytics host URL
            timeout: Request timeout in seconds
        """
        if not api_key:
            raise AuthenticationError("API key is required")

        self.api_key = api_key
        self.host = host.rstrip("/")
        self.timeout = timeout
        self._client: httpx.AsyncClient | None = None

    @property
    def client(self) -> httpx.AsyncClient:
        """Lazy-initialize the async HTTP client."""
        if self._client is None:
            self._client = httpx.AsyncClient(
                base_url=self.host,
                timeout=self.timeout,
                headers={
                    "x-api-key": self.api_key,
                    "Content-Type": "application/json",
                    "User-Agent": "entrolytics-python/1.0.0",
                },
            )
        return self._client

    async def close(self) -> None:
        """Close the async HTTP client."""
        if self._client is not None:
            await self._client.aclose()
            self._client = None

    async def __aenter__(self) -> AsyncEntrolytics:
        return self

    async def __aexit__(self, *args: Any) -> None:
        await self.close()

    def _handle_response(self, response: httpx.Response) -> TrackResponse:
        """Handle API response and raise appropriate exceptions."""
        if response.status_code in (200, 201, 202):
            return TrackResponse(success=True)

        if response.status_code == 401:
            raise AuthenticationError()

        if response.status_code == 400:
            try:
                data = response.json()
                message = data.get("error", "Invalid request")
            except Exception:
                message = "Invalid request"
            raise ValidationError(message)

        if response.status_code == 429:
            retry_after = response.headers.get("Retry-After")
            raise RateLimitError(
                retry_after=int(retry_after) if retry_after else None
            )

        raise EntrolyticsError(
            f"Request failed with status {response.status_code}",
            status_code=response.status_code,
        )

    async def track(
        self,
        website_id: str,
        event: str,
        data: dict[str, Any] | None = None,
        *,
        url: str | None = None,
        referrer: str | None = None,
        user_id: str | None = None,
        session_id: str | None = None,
        user_agent: str | None = None,
        ip_address: str | None = None,
    ) -> TrackResponse:
        """Track a custom event asynchronously."""
        if not website_id:
            raise ValidationError("website_id is required")
        if not event:
            raise ValidationError("event is required")

        properties = dict(data or {})
        if user_id:
            properties["distinctId"] = user_id

        payload: dict[str, Any] = {
            "websiteId": website_id,
            "sessionId": session_id or _generate_uuid(),
            "visitorId": _generate_uuid(),
            "url": _normalize_url(self.host, url, "/track"),
            "eventType": "custom_event",
            "eventName": event,
            "properties": properties,
        }

        normalized_referrer = _normalize_referrer(referrer)
        if normalized_referrer:
            payload["referrer"] = normalized_referrer

        headers = {}
        if user_agent:
            headers["User-Agent"] = user_agent
        if ip_address:
            headers["X-Forwarded-For"] = ip_address

        try:
            response = await self.client.post("/collect", json=payload, headers=headers)
            return self._handle_response(response)
        except httpx.RequestError as e:
            raise NetworkError(f"Request failed: {e}") from e

    async def page_view(
        self,
        website_id: str,
        url: str,
        *,
        referrer: str | None = None,
        title: str | None = None,
        user_id: str | None = None,
        session_id: str | None = None,
        user_agent: str | None = None,
        ip_address: str | None = None,
    ) -> TrackResponse:
        """Track a page view asynchronously."""
        if not website_id:
            raise ValidationError("website_id is required")
        if not url:
            raise ValidationError("url is required")

        properties: dict[str, Any] = {}
        if title:
            properties["title"] = title
        if user_id:
            properties["distinctId"] = user_id

        payload: dict[str, Any] = {
            "websiteId": website_id,
            "sessionId": session_id or _generate_uuid(),
            "visitorId": _generate_uuid(),
            "url": _normalize_url(self.host, url, "/"),
            "eventType": "pageview",
            "properties": properties,
        }

        normalized_referrer = _normalize_referrer(referrer)
        if normalized_referrer:
            payload["referrer"] = normalized_referrer

        headers = {}
        if user_agent:
            headers["User-Agent"] = user_agent
        if ip_address:
            headers["X-Forwarded-For"] = ip_address

        try:
            response = await self.client.post("/collect", json=payload, headers=headers)
            return self._handle_response(response)
        except httpx.RequestError as e:
            raise NetworkError(f"Request failed: {e}") from e

    async def identify(
        self,
        website_id: str,
        user_id: str,
        traits: dict[str, Any] | None = None,
    ) -> TrackResponse:
        """Identify a user asynchronously."""
        if not website_id:
            raise ValidationError("website_id is required")
        if not user_id:
            raise ValidationError("user_id is required")

        payload: dict[str, Any] = {
            "websiteId": website_id,
            "sessionId": _generate_uuid(),
            "visitorId": _generate_uuid(),
            "url": _normalize_url(self.host, "/identify", "/identify"),
            "eventType": "custom_event",
            "eventName": "identify",
            "properties": {
                "distinctId": user_id,
                **(traits or {}),
            },
        }

        try:
            response = await self.client.post("/collect", json=payload)
            return self._handle_response(response)
        except httpx.RequestError as e:
            raise NetworkError(f"Request failed: {e}") from e

    # ========================================================================
    # Phase 2: Web Vitals (requires entrolytics)
    # ========================================================================

    async def track_vital(
        self,
        website_id: str,
        metric: VitalMetric,
        value: float,
        rating: VitalRating,
        *,
        delta: float | None = None,
        id: str | None = None,
        navigation_type: NavigationType | None = None,
        attribution: dict[str, Any] | None = None,
        url: str | None = None,
        path: str | None = None,
        session_id: str | None = None,
        visitor_id: str | None = None,
    ) -> TrackResponse:
        """
        Track a Web Vital metric asynchronously.

        Note: This feature requires entrolytics.

        Args:
            website_id: Your Entrolytics website ID
            metric: Vital type (LCP, INP, CLS, TTFB, or FCP)
            value: Metric value in milliseconds (except CLS which is unitless)
            rating: Performance rating (good, needs-improvement, or poor)
            delta: Difference from previous value
            id: Unique identifier for deduplication
            navigation_type: How the page was navigated to
            attribution: Debug information about the metric
            url: Full page URL
            path: URL path component
            session_id: Session identifier

        Returns:
            TrackResponse with success status
        """
        if not website_id:
            raise ValidationError("website_id is required")
        if not metric:
            raise ValidationError("metric is required (LCP, INP, CLS, TTFB, or FCP)")
        if not rating:
            raise ValidationError("rating is required (good, needs-improvement, or poor)")

        payload: dict[str, Any] = {
            "websiteId": website_id,
            "visitorId": visitor_id or _generate_uuid(),
            "sessionId": session_id or _generate_uuid(),
            "url": _normalize_url(self.host, url, "/vital"),
            "path": path or "/vital",
            "metricName": metric,
            "metricValue": value,
        }

        try:
            response = await self.client.post("/api/collect/vitals", json=payload)
            return self._handle_response(response)
        except httpx.RequestError as e:
            raise NetworkError(f"Request failed: {e}") from e

    # ========================================================================
    # Phase 2: Form Analytics (requires entrolytics)
    # ========================================================================

    async def track_form_event(
        self,
        website_id: str,
        event_type: FormEventType,
        form_id: str,
        url_path: str,
        *,
        form_name: str | None = None,
        field_name: str | None = None,
        field_type: str | None = None,
        field_index: int | None = None,
        time_on_field: int | None = None,
        time_since_start: int | None = None,
        error_message: str | None = None,
        success: bool | None = None,
        session_id: str | None = None,
        visitor_id: str | None = None,
    ) -> TrackResponse:
        """
        Track a form interaction event asynchronously.

        Note: This feature requires entrolytics.

        Args:
            website_id: Your Entrolytics website ID
            event_type: Form event type (start, field_focus, field_blur, etc.)
            form_id: Unique form identifier
            url_path: Page path where the form is located
            form_name: Human-readable form name
            field_name: Field name (for field events)
            field_type: Input type (text, email, select, etc.)
            field_index: Position of the field in the form
            time_on_field: Milliseconds spent on the field
            time_since_start: Milliseconds since form interaction started
            error_message: Validation error message (for error events)
            success: Whether the submission was successful
            session_id: Session identifier

        Returns:
            TrackResponse with success status
        """
        if not website_id:
            raise ValidationError("website_id is required")
        if not event_type:
            raise ValidationError("event_type is required")
        if not form_id:
            raise ValidationError("form_id is required")
        if not url_path:
            raise ValidationError("url_path is required")

        payload: dict[str, Any] = {
            "websiteId": website_id,
            "visitorId": visitor_id or _generate_uuid(),
            "sessionId": session_id or _generate_uuid(),
            "eventType": event_type,
            "formId": form_id,
            "urlPath": url_path,
        }

        if form_name:
            payload["formName"] = form_name
        if field_name:
            payload["fieldName"] = field_name
        if field_type:
            payload["fieldType"] = field_type
        if field_index is not None:
            payload["fieldIndex"] = field_index
        if time_on_field is not None:
            payload["timeOnField"] = time_on_field
        if time_since_start is not None:
            payload["timeSinceStart"] = time_since_start
        if error_message:
            payload["errorMessage"] = error_message
        if success is not None:
            payload["success"] = success
        try:
            response = await self.client.post("/api/collect/forms", json=payload)
            return self._handle_response(response)
        except httpx.RequestError as e:
            raise NetworkError(f"Request failed: {e}") from e

    # ========================================================================
    # Phase 2: Deployment Tracking (requires entrolytics)
    # ========================================================================

    async def set_deployment(
        self,
        website_id: str,
        deploy_id: str,
        *,
        git_sha: str | None = None,
        git_branch: str | None = None,
        deploy_url: str | None = None,
        source: DeploymentSource | None = None,
    ) -> TrackResponse:
        """
        Register deployment context asynchronously.

        Note: This feature requires entrolytics.

        Args:
            website_id: Your Entrolytics website ID
            deploy_id: Unique deployment identifier
            git_sha: Git commit SHA
            git_branch: Git branch name
            deploy_url: Deployment URL
            source: Deployment platform (vercel, netlify, etc.)

        Returns:
            TrackResponse with success status
        """
        if not website_id:
            raise ValidationError("website_id is required")
        if not deploy_id:
            raise ValidationError("deploy_id is required")

        payload: dict[str, Any] = {
            "website": website_id,
            "deployId": deploy_id,
        }

        if git_sha:
            payload["gitSha"] = git_sha
        if git_branch:
            payload["gitBranch"] = git_branch
        if deploy_url:
            payload["deployUrl"] = deploy_url
        if source:
            payload["source"] = source

        try:
            response = await self.client.post(
                f"/api/websites/{website_id}/deployments", json=payload
            )
            return self._handle_response(response)
        except httpx.RequestError as e:
            raise NetworkError(f"Request failed: {e}") from e
