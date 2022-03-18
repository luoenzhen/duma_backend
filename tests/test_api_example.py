import base64

import pytest


@pytest.fixture
def test_data(app):
    from duma_backend import models 

    with app.app_context():
        models.db.session.add(models.Example(count=5))
        models.db.session.commit()


def test_hello_get(client):
    response = client.get("/api/v1.0/example")
    assert response.json == {"counter": 1}


def test_hello_post_403(client):
    response = client.post("/api/v1.0/example/param1")
    assert response.status_code == 403


def test_hello_post_200(client, test_data):
    response = client.post(
        "/api/v1.0/example/param1",
        headers={"Authorization": "Basic {}".format(base64.b64encode(b"user:user").decode("ascii"))},
    )
    assert bool(response.json["current_user"])
    assert response.json["counter"] == 5
