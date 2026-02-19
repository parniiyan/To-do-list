import pytest


class TestTaskOwnership:
    def test_user_cannot_access_other_users_private_task(
        self, client, auth_headers, auth_headers_user2, db
    ):
        from app.models import Task

        task = Task(title="User 1 Private Task", user_id=1)
        db.add(task)
        db.commit()
        db.refresh(task)

        response = client.get(f"/tasks/{task.id}", headers=auth_headers_user2)
        assert response.status_code == 404

    def test_user_cannot_update_other_users_private_task(
        self, client, auth_headers, auth_headers_user2, db
    ):
        from app.models import Task

        task = Task(title="User 1 Private Task", user_id=1)
        db.add(task)
        db.commit()
        db.refresh(task)

        response = client.patch(
            f"/tasks/{task.id}",
            headers=auth_headers_user2,
            json={"title": "Hacked!"}
        )
        assert response.status_code == 404

    def test_user_cannot_delete_other_users_private_task(
        self, client, auth_headers, auth_headers_user2, db
    ):
        from app.models import Task

        task = Task(title="User 1 Private Task", user_id=1)
        db.add(task)
        db.commit()
        db.refresh(task)

        response = client.delete(f"/tasks/{task.id}", headers=auth_headers_user2)
        assert response.status_code == 404

    def test_user_can_access_own_private_task(self, client, auth_headers, db):
        from app.models import Task

        task = Task(title="My Private Task", user_id=1)
        db.add(task)
        db.commit()
        db.refresh(task)

        response = client.get(f"/tasks/{task.id}", headers=auth_headers)
        assert response.status_code == 200
        assert response.json()["title"] == "My Private Task"

    def test_anonymous_cannot_access_task(self, client, db):
        from app.models import Task

        task = Task(title="Private Task", user_id=1)
        db.add(task)
        db.commit()
        db.refresh(task)

        response = client.get(f"/tasks/{task.id}")
        assert response.status_code == 401


class TestTagOwnership:
    def test_user_cannot_access_other_users_tag(
        self, client, auth_headers, auth_headers_user2, db
    ):
        from app.models import Tag

        tag = Tag(name="User 1 Tag", user_id=1)
        db.add(tag)
        db.commit()
        db.refresh(tag)

        response = client.delete(f"/tags/{tag.id}", headers=auth_headers_user2)
        assert response.status_code == 404

    def test_user_can_access_own_tag(self, client, auth_headers, db):
        from app.models import Tag

        tag = Tag(name="My Tag", user_id=1)
        db.add(tag)
        db.commit()
        db.refresh(tag)

        response = client.delete(f"/tags/{tag.id}", headers=auth_headers)
        assert response.status_code == 204

    def test_anonymous_cannot_access_tag(self, client, db):
        response = client.get("/tags")
        assert response.status_code == 401


class TestTaskCreateWithAuth:
    def test_authenticated_user_creates_task(
        self, client, auth_headers, db
    ):
        from app.models import Task

        response = client.post(
            "/tasks",
            headers=auth_headers,
            json={"title": "My Task"}
        )
        assert response.status_code == 201
        task = db.query(Task).first()
        assert task.user_id == 1

    def test_anonymous_cannot_create_task(self, client, db):
        response = client.post(
            "/tasks",
            json={"title": "Task"}
        )
        assert response.status_code == 401
