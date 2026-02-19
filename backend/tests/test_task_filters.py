import pytest
from datetime import datetime, timedelta


class TestTaskFiltering:
    def test_filter_by_status_completed(self, client, auth_headers, db):
        from app.models import Task

        task1 = Task(title="Task 1", user_id=1, completed=False)
        task2 = Task(title="Task 2", user_id=1, completed=True)
        task3 = Task(title="Task 3", user_id=1, completed=False)
        db.add_all([task1, task2, task3])
        db.commit()

        response = client.get("/tasks?status=completed", headers=auth_headers)
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 1
        assert data[0]["title"] == "Task 2"

    def test_filter_by_status_pending(self, client, auth_headers, db):
        from app.models import Task

        task1 = Task(title="Task 1", user_id=1, completed=False)
        task2 = Task(title="Task 2", user_id=1, completed=True)
        db.add_all([task1, task2])
        db.commit()

        response = client.get("/tasks?status=pending", headers=auth_headers)
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 1
        assert data[0]["title"] == "Task 1"

    def test_filter_by_priority(self, client, auth_headers, db):
        from app.models import Task

        task1 = Task(title="Task 1", user_id=1, priority=1)
        task2 = Task(title="Task 2", user_id=1, priority=3)
        task3 = Task(title="Task 3", user_id=1, priority=5)
        db.add_all([task1, task2, task3])
        db.commit()

        response = client.get("/tasks?priority=3", headers=auth_headers)
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 1
        assert data[0]["priority"] == 3

    def test_filter_by_tag(self, client, auth_headers, db):
        from app.models import Task, Tag

        tag = Tag(name="work", user_id=1)
        db.add(tag)
        db.commit()
        db.refresh(tag)

        task1 = Task(title="Task with tag", user_id=1)
        task2 = Task(title="Task without tag", user_id=1)
        task1.tags.append(tag)
        db.add_all([task1, task2])
        db.commit()

        response = client.get(f"/tasks?tag_id={tag.id}", headers=auth_headers)
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 1
        assert data[0]["title"] == "Task with tag"

    def test_filter_by_due_before(self, client, auth_headers, db):
        from app.models import Task

        past_date = datetime.now() - timedelta(days=5)
        future_date = datetime.now() + timedelta(days=5)

        task1 = Task(title="Past due", user_id=1, due_date=past_date)
        task2 = Task(title="Future due", user_id=1, due_date=future_date)
        db.add_all([task1, task2])
        db.commit()

        response = client.get(f"/tasks?due_before={future_date.isoformat()}", headers=auth_headers)
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 2

        response = client.get(f"/tasks?due_before={past_date.isoformat()}", headers=auth_headers)
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 1
        assert data[0]["title"] == "Past due"

    def test_filter_by_due_after(self, client, auth_headers, db):
        from app.models import Task

        past_date = datetime.now() - timedelta(days=5)
        future_date = datetime.now() + timedelta(days=5)

        task1 = Task(title="Past due", user_id=1, due_date=past_date)
        task2 = Task(title="Future due", user_id=1, due_date=future_date)
        db.add_all([task1, task2])
        db.commit()

        response = client.get(f"/tasks?due_after={past_date.isoformat()}", headers=auth_headers)
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 2

    def test_filter_overdue(self, client, auth_headers, db):
        from app.models import Task

        past_date = datetime.now() - timedelta(days=5)
        future_date = datetime.now() + timedelta(days=5)

        task1 = Task(title="Overdue", user_id=1, due_date=past_date, completed=False)
        task2 = Task(title="Future", user_id=1, due_date=future_date, completed=False)
        task3 = Task(title="Completed overdue", user_id=1, due_date=past_date, completed=True)
        db.add_all([task1, task2, task3])
        db.commit()

        response = client.get("/tasks?overdue=true", headers=auth_headers)
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 1
        assert data[0]["title"] == "Overdue"

    def test_filter_no_due_date(self, client, auth_headers, db):
        from app.models import Task

        task1 = Task(title="No due date", user_id=1)
        task2 = Task(title="With due date", user_id=1, due_date=datetime.now())
        db.add_all([task1, task2])
        db.commit()

        response = client.get("/tasks?no_due_date=true", headers=auth_headers)
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 1
        assert data[0]["title"] == "No due date"


class TestTaskSorting:
    def test_sort_by_position_asc(self, client, auth_headers, db):
        from app.models import Task

        task1 = Task(title="Task 1", user_id=1, position=3.0)
        task2 = Task(title="Task 2", user_id=1, position=1.0)
        task3 = Task(title="Task 3", user_id=1, position=2.0)
        db.add_all([task1, task2, task3])
        db.commit()

        response = client.get("/tasks?sort_by=position&sort_order=asc", headers=auth_headers)
        assert response.status_code == 200
        data = response.json()
        assert data[0]["title"] == "Task 2"
        assert data[1]["title"] == "Task 3"
        assert data[2]["title"] == "Task 1"

    def test_sort_by_position_desc(self, client, auth_headers, db):
        from app.models import Task

        task1 = Task(title="Task 1", user_id=1, position=1.0)
        task2 = Task(title="Task 2", user_id=1, position=2.0)
        db.add_all([task1, task2])
        db.commit()

        response = client.get("/tasks?sort_by=position&sort_order=desc", headers=auth_headers)
        assert response.status_code == 200
        data = response.json()
        assert data[0]["title"] == "Task 2"
        assert data[1]["title"] == "Task 1"

    def test_sort_by_created_at(self, client, auth_headers, db):
        from app.models import Task

        task1 = Task(title="Task 1", user_id=1)
        db.add(task1)
        db.commit()

        import time
        time.sleep(0.1)

        task2 = Task(title="Task 2", user_id=1)
        db.add(task2)
        db.commit()

        response = client.get("/tasks?sort_by=created_at&sort_order=asc", headers=auth_headers)
        assert response.status_code == 200
        data = response.json()
        assert data[0]["title"] == "Task 1"
        assert data[1]["title"] == "Task 2"

    def test_sort_by_priority_desc(self, client, auth_headers, db):
        from app.models import Task

        task1 = Task(title="Low", user_id=1, priority=1)
        task2 = Task(title="High", user_id=1, priority=5)
        task3 = Task(title="Medium", user_id=1, priority=3)
        db.add_all([task1, task2, task3])
        db.commit()

        response = client.get("/tasks?sort_by=priority&sort_order=desc", headers=auth_headers)
        assert response.status_code == 200
        data = response.json()
        assert data[0]["title"] == "High"
        assert data[1]["title"] == "Medium"
        assert data[2]["title"] == "Low"
