import pytest


@pytest.fixture
def test_data(app):
    from duma_backend import models

    with app.app_context():
        models.db.session.add(models.Example(count=5))
        models.db.session.commit()
