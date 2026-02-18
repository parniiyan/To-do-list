import pytest
from datetime import datetime, timedelta


class TestTaskCreate:
    def test_create_task_without_auth(self, client):
        response = client.post(
            "/tasks",
            json={"title": "New Task", "priority": 3}
        )
        assert response.status_code == 201
        data = response.json()
        assert data["title"] == "New Task"
        assert data["priority"] == 3
        assert data["completed"] is False
        assert data["user_id"] is None

    def test_create_task_with_auth(self, client, auth_headers):
        response = client.post(
            "/tasks",
            headers=auth_headers,
            json={"title": "Private Task", "priority": 5}
        )
        assert response.status_code == 201
        data = response.json()
        assert data["title"] == "Private Task"
        assert data["priority"] == 5
        assert data["user_id"] == 1

    def test_create_task_with_description(self, client):
        response = client.post(
            "/tasks",
            json={"title": "Task", "description": "Some description"}
        )
        assert response.status_code == 201
        assert response.json()["description"] == "Some description"

    def test_create_task_with_due_date(self, client):
        due_date = (datetime.now() + timedelta(days=7)).isoformat()
        response = client.post(
            "/tasks",
            json={"title": "Task", "due_date": due_date}
        )
        assert response.status_code == 201
        assert response.json()["due_date"] is not None

    def test_create_task_with_tags(self, client, tag):
        response = client.post(
            "/tasks",
            json={"title": "Task", "tag_ids": [tag.id]}
        )
        assert response.status_code == 201
        assert len(response.json()["tags"]) == 1

    def test_create_task_invalid_priority(self, client):
        response = client.post(
            "/tasks",
            json={"title": "Task", "priority": 10}
        )
        assert response.status_code == 422

    def test_create_task_priority_zero(self, client):
        response = client.post(
            "/tasks",
            json={"title": "Task", "priority": 0}
        )
        assert response.status_code == 422

    def test_create_task_missing_title(self, client):
        response = client.post(
            "/tasks",
            json={"description": "No title"}
        )
        assert response.status_code == 422


class TestTaskRead:
    def test_get_all_tasks_without_auth(self, client, public_task):
        response = client.get("/tasks")
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 1
        assert data[0]["title"] == "Public Task"

    def test_get_all_tasks_with_auth_sees_public_and_private(self, client, auth_headers, public_task, private_task):
        response = client.get("/tasks", headers=auth_headers)
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 2

    def test_get_single_task(self, client, public_task):
        response = client.get(f"/tasks/{public_task.id}")
        assert response.status_code == 200
        assert response.json()["title"] == "Public Task"

    def test_get_single_task_not_found(self, client):
        response = client.get("/tasks/9999")
        assert response.status_code == 404


class TestTaskUpdate:
    def test_update_task(self, client, public_task):
        response = client.patch(
            f"/tasks/{public_task.id}",
            json={"title": "Updated Title", "priority": 5}
        )
        assert response.status_code == 200
        data = response.json()
        assert data["title"] == "Updated Title"
        assert data["priority"] == 5

    def test_update_task_partial(self, client, public_task):
        response = client.patch(
            f"/tasks/{public_task.id}",
            json={"completed": True}
        )
        assert response.status_code == 200
        assert response.json()["completed"] is True
        assert response.json()["title"] == "Public Task"

    def test_update_task_not_found(self, client):
        response = client.patch(
            "/tasks/9999",
            json={"title": "Updated"}
        )
        assert response.status_code == 404


class TestTaskDelete:
    def test_delete_task(self, client, public_task):
        response = client.delete(f"/tasks/{public_task.id}")
        assert response.status_code == 204

        get_response = client.get(f"/tasks/{public_task.id}")
        assert get_response.status_code == 404

    def test_delete_task_not_found(self, client):
        response = client.delete("/tasks/9999")
        assert response.status_code == 404


class TestTaskToggle:
    def test_toggle_task_completed(self, client, public_task):
        assert public_task.completed is False

        response = client.patch(f"/tasks/{public_task.id}/toggle")
        assert response.status_code == 200
        assert response.json()["completed"] is True

        response = client.patch(f"/tasks/{public_task.id}/toggle")
        assert response.status_code == 200
        assert response.json()["completed"] is False

    def test_toggle_task_not_found(self, client):
        response = client.patch("/tasks/9999/toggle")
        assert response.status_code == 404


class TestTaskReorder:
    def test_reorder_tasks(self, client, db):
        from app.models import Task

        task1 = Task(title="Task 1", position=1.0)
        task2 = Task(title="Task 2", position=2.0)
        task3 = Task(title="Task 3", position=3.0)
        db.add_all([task1, task2, task3])
        db.commit()

        response = client.put(
            "/tasks/reorder",
            json={
                "tasks": [
                    {"id": task1.id, "position": 3.0},
                    {"id": task2.id, "position": 1.0},
                    {"id": task3.id, "position": 2.0}
                ]
            }
        )
        assert response.status_code == 204

        db.refresh(task1)
        db.refresh(task2)
        db.refresh(task3)
        assert task1.position == 3.0
        assert task2.position == 1.0
        assert task3.position == 2.0
