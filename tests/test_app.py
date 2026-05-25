"""Basic application-level smoke tests."""


def test_index_route_is_reachable(client):
    """Landing page should render successfully for anonymous users."""
    response = client.get("/")
    assert response.status_code == 200
    assert b"MediTrack" in response.data
