"""WSGI entrypoint for Gunicorn deployment.

Wraps the FastAPI ASGI app using a2wsgi for plain gunicorn compatibility.
Usage: gunicorn wsgi:app
"""
from a2wsgi import ASGIMiddleware
from server import app as _asgi_app

# Expose WSGI-compatible app for gunicorn
app = ASGIMiddleware(_asgi_app)
