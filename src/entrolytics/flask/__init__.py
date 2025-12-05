"""Flask integration for Entrolytics."""

from entrolytics.flask.extension import Entrolytics as FlaskEntrolytics
from entrolytics.flask.utils import track, page_view, identify

__all__ = [
    "FlaskEntrolytics",
    "track",
    "page_view",
    "identify",
]
