import os

import pytest

os.environ.setdefault("DATABASE_URL", "sqlite:///./test.db")
os.environ.setdefault("FLASK_SECRET_KEY", "test-secret-key")
os.environ.setdefault("ANALYZER_URL", "mock")


@pytest.fixture(scope="session")
def _engine():
    import importlib

    import config

    config.DATABASE_URL = "sqlite:///./test.db"
    config.FLASK_SECRET_KEY = "test-secret-key"
    config.ANALYZER_URL = "mock"

    import utility.database.main as db_main

    importlib.reload(db_main)
    db_main.init_db()
    return db_main.engine


@pytest.fixture(autouse=True)
def reset_db(_engine):
    from sqlmodel import SQLModel

    SQLModel.metadata.drop_all(_engine)
    SQLModel.metadata.create_all(_engine)


@pytest.fixture
def app(_engine):
    import importlib.util
    from pathlib import Path

    path = Path(__file__).resolve().parent / "app.py"
    spec = importlib.util.spec_from_file_location("safe_text_main", path)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)
    flask_app = module.app
    flask_app.config["TESTING"] = True
    return flask_app


@pytest.fixture
def client(app):
    return app.test_client()


@pytest.fixture
def db_session(_engine):
    from sqlmodel import Session

    session = Session(_engine)
    yield session
    session.close()


@pytest.fixture
def test_user(db_session):
    from werkzeug.security import generate_password_hash

    from utility.database.model import User

    user = User(email="user@test.com", password_hash=generate_password_hash("password123"))
    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)
    return user


@pytest.fixture
def test_admin(db_session):
    from werkzeug.security import generate_password_hash

    from utility.database.model import Admin

    admin = Admin(email="admin@test.com", password_hash=generate_password_hash("adminpass"))
    db_session.add(admin)
    db_session.commit()
    db_session.refresh(admin)
    return admin


@pytest.fixture
def user_api_key(db_session, test_user):
    from utility.database.model import APIKey

    key = APIKey(userid=test_user.id, thekey="safe_testkey123")
    db_session.add(key)
    db_session.commit()
    return key.thekey


@pytest.fixture
def authed_client(client, test_user):
    with client.session_transaction() as sess:
        sess["user_id"] = test_user.id
        sess["email"] = test_user.email
        sess["role"] = "user"
    return client
