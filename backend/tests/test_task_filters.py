import pytest
from datetime import datetime, timedelta


class TestTaskFiltering:
    def test_filter_by_status_completed(self, client, db):
        from app.models import Task

        task1 = Task(title="Task 1", completed=False)
        task2 = Task(title="Task 2", completed=True)
        task3 = Task(title="Task 3", completed=False)
        db.add_all([task1, task2, task3])
        db.commit()

        response = client.get("/tasks?status=completed")
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 1
        assert data[0]["title"] == "Task 2"

    def test_filter_by_status_pending(self, client, db):
        from app.models import Task

        task1 = Task(title="Task 1", completed=False)
        task2 = Task(title="Task 2", completed=True)
        db.add_all([task1, task2])
        db.commit()

        response = client.get("/tasks?status=pending")
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 1
        assert data[0]["title"] == "Task 1"

    def test_filter_by_priority(self, client, db):
        from app.models import Task

        task1 = Task(title="Task 1", priority=1)
        task2 = Task(title="Task 2", priority=3)
        task3 = Task(title="Task 3", priority=5)
        db.add_all([task1, task2, task3])
        db.commit()

        response = client.get("/tasks?priority=3")
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 1
        assert data[0]["priority"] == 3

    def test_filter_by_tag(self, client, db, tag):
        from app.models import Task

        task1 = Task(title="Task with tag")
        task2 = Task(title="Task without tag")
        task1.tags.append(tag)
        db.add_all([task1, task2])
        db.commit()

        response = client.get(f"/tasks?tag_id={tag.id}")
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 1
        assert data[0]["title"] == "Task with tag"

    def test_filter_by_due_before(self, client, db):
        from app.models import Task

        past_date = datetime.now() - timedelta(days=5)
        future_date = datetime.now() + timedelta(days=5)

        task1 = Task(title="Past due", due_date=past_date)
        task2 = Task(title="Future due", due_date=future_date)
        db.add_all([task1, task2])
        db.commit()

        response = client.get(f"/tasks?due_before={future_date.isoformat()}")
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 2

        response = client.get(f"/tasks?due_before={past_date.isoformat()}")
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 1
        assert data[0]["title"] == "Past due"

    def test_filter_by_due_after(self, client, db):
        from app.models import Task

        past_date = datetime.now() - timedelta(days=5)
        future_date = datetime.now() + timedelta(days=5)

        task1 = Task(title="Past due", due_date=past_date)
        task2 = Task(title="Future due", due_date=future_date)
        db.add_all([task1, task2])
        db.commit()

        response = client.get(f"/tasks?due_after={past_date.isoformat()}")
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 2

    def test_filter_overdue(self, client, db):
        from app.models import Task

        past_date = datetime.now() - timedelta(days=5)
        future_date = datetime.now() + timedelta(days=5)

        task1 = Task(title="Overdue", due_date=past_date, completed=False)
        task2 = Task(title="Future", due_date=future_date, completed=False)
        task3 = Task(title="Completed overdue", due_date=past_date, completed=True)
        db.add_all([task1, task2, task3])
        db.commit()

        response = client.get("/tasks?overdue=true")
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 1
        assert data[0]["title"] == "Overdue"

    def test_filter_no_due_date(self, client, db):
        from app.models import Task

        task1 = Task(title="No due date")
        task2 = Task(title="With due date", due_date=datetime.now())
        db.add_all([task1, task2])
        db.commit()

        response = client.get("/tasks?no_due_date=true")
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 1
        assert data[0]["title"] == "No due date"


class TestTaskSorting:
    def test_sort_by_position_asc(self, client, db):
        from app.models import Task

        task1 = Task(title="Task 1", position=3.0)
        task2 = Task(title="Task 2", position=1.0)
        task3 = Task(title="Task 3", position=2.0)
        db.add_all([task1, task2, task3])
        db.commit()

        response = client.get("/tasks?sort_by=position&sort_order=asc")
        assert response.status_code == 200
        data = response.json()
        assert data[0]["title"] == "Task 2"
        assert data[1]["title"] == "Task 3"
        assert data[2]["title"] == "Task 1"

    def test_sort_by_position_desc(self, client, db):
        from app.models import Task

        task1 = Task(title="Task 1", position=1.0)
        task2 = Task(title="Task 2", position=2.0)
        db.add_all([task1, task2])
        db.commit()

        response = client.get("/tasks?sort_by=position&sort_order=desc")
        assert response.status_code == 200
        data = response.json()
        assert data[0]["title"] == "Task 2"
        assert data[1]["title"] == "Task 1"

    def test_sort_by_created_at(self, client, db):
        from app.models import Task
        import time

        task1 = Task(title="Task 1")
        db.add(task1)
        db.commit()
        time.sleep(0.1)
        task2 = Task(title="Task 2")
        db.add(task2)
        db.commit()

        response = client.get("/tasks?sort_by=created_at&sort_order=asc")
        assert response.status_code == 200
        data = response.json()
        assert data[0]["title"] == "Task 1"
        assert data[1]["title"] == "Task 2"

    def test_sort_by_priority_desc(self, client, db):
        from app.models import Task

        task1 = Task(title="Low", priority=1)
        task2 = Task(title="High", priority=5)
        task3 = Task(title="Medium", priority=3)
        db.add_all([task1, task2, task3])
        db.commit()

        response = client.get("/tasks?sort_by=priority&sort_order=desc")
        assert response.status_code == 200
        data = response.json()
        assert data[0]["title"] == "High"
        assert data[1]["title"] == "Medium"
        assert data[2]["title"] == "Low"
