import base64

from flask_tern.testing.fixtures import monkeypatch_session, cache_spec, basic_auth
import pytest

from duma_backend import create_app
from duma_backend.models import db


@pytest.fixture
def app():
    app = create_app(
        {
            "TESTING": True,
            "SQLALCHEMY_DATABASE_URI": "sqlite:///:memory:",
            "SQLALCHEMY_ENGINE_OPTIONS": {},
            "OIDC_DISCOVERY_URL": "https://auth.example.com/.well-known/openid-configuration",
            "OIDC_CLIENT_ID": "oidc-test",
        }
    )
    # setup db
    with app.app_context():
        db.drop_all()
        db.create_all()
        # here we would set up initial data for all tests if needed

    yield app


@pytest.fixture
def client(app, basic_auth):
    return app.test_client()
