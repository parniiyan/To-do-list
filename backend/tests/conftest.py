import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.main import app
from app.database import get_db, Base
from app.auth import get_password_hash


SQLALCHEMY_DATABASE_URL = "sqlite:///:memory:"

engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


@pytest.fixture(scope="function")
def db():
    Base.metadata.create_all(bind=engine)
    db = TestingSessionLocal()
    yield db
    db.close()
    Base.metadata.drop_all(bind=engine)


@pytest.fixture(scope="function")
def client(db):
    def override_get_db():
        try:
            yield db
        finally:
            pass

    app.dependency_overrides[get_db] = override_get_db
    with TestClient(app) as c:
        yield c
    app.dependency_overrides.clear()


@pytest.fixture
def user(db):
    user_data = {
        "email": "test@example.com",
        "password": "password123"
    }
    from app.models import User
    user = User(email=user_data["email"], password=get_password_hash(user_data["password"]))
    db.add(user)
    db.commit()
    db.refresh(user)
    return user_data, user


@pytest.fixture
def user2(db):
    user_data = {
        "email": "user2@example.com",
        "password": "password456"
    }
    from app.models import User
    user = User(email=user_data["email"], password=get_password_hash(user_data["password"]))
    db.add(user)
    db.commit()
    db.refresh(user)
    return user_data, user


@pytest.fixture
def auth_headers(client, user):
    response = client.post(
        "/auth/login",
        data={"username": user[0]["email"], "password": user[0]["password"]}
    )
    token = response.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}


@pytest.fixture
def auth_headers_user2(client, user2):
    response = client.post(
        "/auth/login",
        data={"username": user2[0]["email"], "password": user2[0]["password"]}
    )
    token = response.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}


@pytest.fixture
def public_task(db, user):
    from app.models import Task
    task = Task(title="Public Task", user_id=None)
    db.add(task)
    db.commit()
    db.refresh(task)
    return task


@pytest.fixture
def private_task(db, user):
    from app.models import Task
    task = Task(title="Private Task", user_id=user[1].id)
    db.add(task)
    db.commit()
    db.refresh(task)
    return task


@pytest.fixture
def tag(db, user):
    from app.models import Tag
    tag = Tag(name="work", color="#ff0000", user_id=user[1].id)
    db.add(tag)
    db.commit()
    db.refresh(tag)
    return tag


@pytest.fixture
def public_tag(db):
    from app.models import Tag
    tag = Tag(name="public", color="#00ff00", user_id=None)
    db.add(tag)
    db.commit()
    db.refresh(tag)
    return tag
