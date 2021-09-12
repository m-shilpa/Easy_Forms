import pytest

from app import app as flask_app


@pytest.fixture
def app():
    yield flask_app


@pytest.fixture
def client(app):
    return app.test_client()


def test_home_page(app,client):
    """Start with a blank database."""

    rv = client.get('/')
    assert b'Welcome' in rv.data