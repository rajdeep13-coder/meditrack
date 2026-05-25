import pytest

from app import create_app


def test_index_route_returns_ok():
    app = create_app()
    client = app.test_client()
    resp = client.get('/')
    # Landing page may redirect to dashboard when signed in; accept 200 or 302
    assert resp.status_code in (200, 302)
