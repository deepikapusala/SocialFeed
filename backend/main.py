"""
Root ASGI application entrypoint.
Forwards directly to the production application in app.main.
"""

from app.main import app

__all__ = ["app"]
 