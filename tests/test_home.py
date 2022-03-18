import base64


def test_root(client):
    response = client.get("/")
    assert response.status_code == 302
    assert response.headers["Location"] == "http://localhost/api/"


def test_home(client):
    response = client.get("/api")
    assert response.headers["Location"] == "http://localhost/api/"

    response = client.get("/api/")
    assert response.headers["Location"] == "http://localhost/api/v1.0/"


def test_whoami_fail(client):
    response = client.get("/api/whoami")
    assert response.status_code == 403


def test_whoami_ok(client):
    response = client.get(
        "/api/whoami",
        headers={"Authorization": "Basic {}".format(base64.b64encode(b"user:user").decode("ascii"))},
    )
    assert response.status_code == 200
    assert response.json == {
        "claims": {},
        "email": "user@example.com",
        "email_verified": False,
        "id": "user",
        "name": "user",
        "roles": ["user"],
        "scopes": [],
    }
