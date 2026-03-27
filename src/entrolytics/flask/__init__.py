"""Flask integration for Entrolytics."""

from entrolytics.flask.extension import Entrolytics as FlaskEntrolytics
from entrolytics.flask.utils import identify, page_view, track

__all__ = [
    "FlaskEntrolytics",
    "track",
    "page_view",
    "identify",
]
