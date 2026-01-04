<div align="center">
  <img src="https://raw.githubusercontent.com/entrolytics/.github/main/media/entrov2.png" alt="Entrolytics" width="64" height="64">

  [![PyPI](https://img.shields.io/pypi/v/entrolytics.svg?logo=pypi&logoColor=white)](https://pypi.org/project/entrolytics/)
  [![License: MIT](https://img.shields.io/badge/License-MIT-green.svg)](https://opensource.org/licenses/MIT)
  [![Python](https://img.shields.io/badge/Python-3.9+-3776AB.svg?logo=python&logoColor=white)](https://www.python.org/)

</div>

---

## Overview

**entrolytics** is the official Python SDK for Entrolytics - first-party growth analytics for the edge. Track events server-side from Django, FastAPI, Flask, or any Python application.

**Why use this SDK?**
- Django, FastAPI, and Flask integrations included
- Async support with `AsyncEntrolytics` client
- Intelligent routing to optimal collection endpoints
- TypeScript-like type hints throughout

## Key Features

<table>
<tr>
<td width="50%">

### Analytics
- Custom event tracking
- Page view tracking
- User identification
- Middleware auto-tracking

</td>
<td width="50%">

### Framework Integrations
- Django middleware + decorators
- FastAPI dependency injection
- Flask extension
- Async/sync client options

</td>
</tr>
</table>

## Quick Start

<table>
<tr>
<td align="center" width="25%">
<img src="https://api.iconify.design/lucide:download.svg?color=%236366f1" width="48"><br>
<strong>1. Install</strong><br>
<code>pip install entrolytics</code>
</td>
<td align="center" width="25%">
<img src="https://api.iconify.design/lucide:code.svg?color=%236366f1" width="48"><br>
<strong>2. Create Client</strong><br>
<code>Entrolytics(api_key)</code>
</td>
<td align="center" width="25%">
<img src="https://api.iconify.design/lucide:settings.svg?color=%236366f1" width="48"><br>
<strong>3. Configure</strong><br>
Set API key and Website ID
</td>
<td align="center" width="25%">
<img src="https://api.iconify.design/lucide:bar-chart-3.svg?color=%236366f1" width="48"><br>
<strong>4. Track</strong><br>
View analytics in dashboard
</td>
</tr>
</table>

## Installation

```bash
pip install entrolytics

# With framework integrations
pip install entrolytics[django]
pip install entrolytics[fastapi]
pip install entrolytics[flask]
pip install entrolytics[all]  # All frameworks
```

```python
from entrolytics import Entrolytics

client = Entrolytics(api_key="ent_xxx")

# Track events
client.track(
    website_id="abc123",
    event="purchase",
    data={
        "revenue": 99.99,
        "currency": "USD",
        "product": "pro-plan"
    }
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
    traits={
        "email": "user@example.com",
        "plan": "pro"
    }
)
```

## Collection Endpoints

Entrolytics provides three collection endpoints optimized for different use cases:

### `/api/collect` - Intelligent Routing (Recommended)

The default endpoint that automatically routes to the optimal storage backend based on your plan and website settings.

**Features:**
- Automatic optimization (Free/Pro → Edge, Business/Enterprise → Node.js)
- Zero configuration required
- Best balance of performance and features

**Use when:**
- You want automatic optimization based on your plan
- You're using Entrolytics Cloud
- You don't have specific latency or feature requirements

### `/api/send-native` - Edge Runtime (Fastest)

Direct edge endpoint for sub-50ms global latency.

**Features:**
- Sub-50ms response times globally
- Runs on Vercel Edge Runtime
- Upstash Redis + Neon Serverless
- Best for high-traffic applications

**Limitations:**
- No ClickHouse export
- Basic geo data (country-level)

**Use when:**
- Latency is critical (<50ms required)
- You have high request volume
- You don't need ClickHouse export

### `/api/send` - Node.js Runtime (Full-Featured)

Traditional Node.js endpoint with advanced capabilities.

**Features:**
- ClickHouse export support
- MaxMind GeoIP (city-level accuracy)
- PostgreSQL storage
- Advanced analytics features

**Latency:** 50-150ms (regional)

**Use when:**
- Self-hosted deployments without edge support
- You need ClickHouse data export
- You require city-level geo accuracy
- Custom server-side analytics workflows

## Configuration

### Default (Intelligent Routing)

```python
from entrolytics import Entrolytics

# Uses /api/collect by default
client = Entrolytics(api_key="ent_xxx")
```

### Edge Runtime Endpoint

```python
from entrolytics import Entrolytics

# Use edge endpoint for sub-50ms latency
client = Entrolytics(
    api_key="ent_xxx",
    host="https://entrolytics.click",
    endpoint="/api/send-native"
)
```

### Node.js Runtime Endpoint

```python
from entrolytics import Entrolytics

# Use Node.js endpoint for ClickHouse export and MaxMind GeoIP
client = Entrolytics(
    api_key="ent_xxx",
    host="https://entrolytics.click",
    endpoint="/api/send"
)
```

See the [Routing documentation](https://entrolytics.click/docs/concepts/routing) for more details.

## Async Support

```python
from entrolytics import AsyncEntrolytics

async with AsyncEntrolytics(api_key="ent_xxx") as client:
    await client.track(
        website_id="abc123",
        event="purchase",
        data={"revenue": 99.99}
    )
```

## Django Integration

### Configuration

```python
# settings.py
INSTALLED_APPS = [
    # ...
]

MIDDLEWARE = [
    'entrolytics.django.EntrolyticsMiddleware',  # Add for auto page tracking
    # ...
]

ENTROLYTICS = {
    'WEBSITE_ID': 'your-website-id',
    'API_KEY': 'ent_xxx',
    'TRACK_ADMIN': False,  # Skip admin pages
    'EXCLUDED_PATHS': ['/health', '/api/'],
}
```

### Manual Tracking

```python
from entrolytics.django import track, identify

def purchase_view(request):
    # Track purchase event
    track('purchase', {'revenue': 99.99}, request=request)
    return JsonResponse({'status': 'ok'})

def login_view(request):
    # After successful login
    identify(str(request.user.pk), {
        'email': request.user.email,
        'plan': 'pro'
    })
    return redirect('dashboard')
```

## FastAPI Integration

### Middleware (Auto Page Tracking)

```python
from fastapi import FastAPI
from entrolytics.fastapi import EntrolyticsMiddleware

app = FastAPI()
app.add_middleware(
    EntrolyticsMiddleware,
    website_id="your-website-id",
    api_key="ent_xxx",
)
```

### Dependency Injection

```python
from fastapi import FastAPI, Depends
from entrolytics.fastapi import get_entrolytics, EntrolyticsTracker

app = FastAPI()
tracker = get_entrolytics(
    website_id="your-website-id",
    api_key="ent_xxx"
)

@app.post("/purchase")
async def purchase(
    tracker: EntrolyticsTracker = Depends(tracker)
):
    await tracker.track("purchase", {"revenue": 99.99})
    return {"status": "ok"}

@app.post("/login")
async def login(
    user_id: str,
    tracker: EntrolyticsTracker = Depends(tracker)
):
    await tracker.identify(user_id, {"plan": "pro"})
    return {"status": "ok"}
```

## Flask Integration

### Extension Setup

```python
from flask import Flask
from entrolytics.flask import FlaskEntrolytics

app = Flask(__name__)
app.config['ENTROLYTICS_WEBSITE_ID'] = 'your-website-id'
app.config['ENTROLYTICS_API_KEY'] = 'ent_xxx'
app.config['ENTROLYTICS_AUTO_TRACK'] = True  # Optional: auto page tracking

entrolytics = FlaskEntrolytics(app)
```

### Manual Tracking

```python
from entrolytics.flask import track, identify

@app.route('/purchase', methods=['POST'])
def purchase():
    track('purchase', {'revenue': 99.99})
    return {'status': 'ok'}

@app.route('/login', methods=['POST'])
def login():
    # After authentication
    identify(user.id, {'email': user.email})
    return redirect('/dashboard')
```

## API Reference

### Entrolytics / AsyncEntrolytics

#### `track(website_id, event, data=None, **kwargs)`

Track a custom event.

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| website_id | str | Yes | Your Entrolytics website ID |
| event | str | Yes | Event name (e.g., 'purchase', 'signup') |
| data | dict | No | Additional event data |
| url | str | No | Page URL where event occurred |
| referrer | str | No | Referrer URL |
| user_id | str | No | User identifier |
| session_id | str | No | Session identifier |
| user_agent | str | No | User agent string |
| ip_address | str | No | Client IP address |

#### `page_view(website_id, url, **kwargs)`

Track a page view.

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| website_id | str | Yes | Your Entrolytics website ID |
| url | str | Yes | Page URL |
| referrer | str | No | Referrer URL |
| title | str | No | Page title |
| user_id | str | No | User identifier |
| user_agent | str | No | User agent string |
| ip_address | str | No | Client IP address |

#### `identify(website_id, user_id, traits=None)`

Identify a user with traits.

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| website_id | str | Yes | Your Entrolytics website ID |
| user_id | str | Yes | Unique user identifier |
| traits | dict | No | User traits (email, plan, etc.) |

## Error Handling

```python
from entrolytics import (
    Entrolytics,
    EntrolyticsError,
    AuthenticationError,
    ValidationError,
    RateLimitError,
    NetworkError,
)

client = Entrolytics(api_key="ent_xxx")

try:
    client.track(website_id="abc123", event="test")
except AuthenticationError:
    print("Invalid API key")
except ValidationError as e:
    print(f"Invalid data: {e.message}")
except RateLimitError as e:
    print(f"Rate limited. Retry after {e.retry_after}s")
except NetworkError:
    print("Network request failed")
except EntrolyticsError as e:
    print(f"Error: {e.message}")
```

## Configuration

| Option | Type | Default | Description |
|--------|------|---------|-------------|
| api_key | str | Required | Your Entrolytics API key |
| host | str | `https://entrolytics.click` | Entrolytics host URL |
| timeout | float | 10.0 | Request timeout in seconds |

## Self-Hosted

For self-hosted Entrolytics instances:

```python
client = Entrolytics(
    api_key="ent_xxx",
    host="https://analytics.yourdomain.com"
)
```

## License

MIT License - see [LICENSE](LICENSE) for details.
