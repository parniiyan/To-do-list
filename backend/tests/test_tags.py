import pytest


class TestTagCreate:
    def test_create_tag_without_auth(self, client):
        response = client.post(
            "/tags",
            json={"name": "work", "color": "#ff0000"}
        )
        assert response.status_code == 401

    def test_create_tag_with_auth(self, client, auth_headers):
        response = client.post(
            "/tags",
            headers=auth_headers,
            json={"name": "personal", "color": "#00ff00"}
        )
        assert response.status_code == 201
        data = response.json()
        assert data["name"] == "personal"
        assert data["user_id"] == 1

    def test_create_tag_default_color(self, client, auth_headers):
        response = client.post(
            "/tags",
            headers=auth_headers,
            json={"name": "tag"}
        )
        assert response.status_code == 201
        assert response.json()["color"] == "#6b7280"

    def test_create_tag_missing_name(self, client, auth_headers):
        response = client.post(
            "/tags",
            headers=auth_headers,
            json={"color": "#ff0000"}
        )
        assert response.status_code == 422


class TestTagRead:
    def test_get_all_tags_without_auth(self, client):
        response = client.get("/tags")
        assert response.status_code == 401

    def test_get_all_tags_with_auth(self, client, auth_headers, db):
        from app.models import Tag
        tag = Tag(name="work", user_id=1)
        db.add(tag)
        db.commit()

        response = client.get("/tags", headers=auth_headers)
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 1
        assert data[0]["name"] == "work"


class TestTagDelete:
    def test_delete_tag(self, client, auth_headers, db):
        from app.models import Tag
        tag = Tag(name="work", user_id=1)
        db.add(tag)
        db.commit()
        db.refresh(tag)

        response = client.delete(f"/tags/{tag.id}", headers=auth_headers)
        assert response.status_code == 204

        tag = db.query(Tag).filter(Tag.id == tag.id).first()
        assert tag is None

    def test_delete_tag_not_found(self, client, auth_headers):
        response = client.delete("/tags/9999", headers=auth_headers)
        assert response.status_code == 404

    def test_delete_tag_with_tasks(self, client, auth_headers, db):
        from app.models import Tag, Task
        tag = Tag(name="work", user_id=1)
        db.add(tag)
        db.commit()
        db.refresh(tag)

        task = Task(title="Task with tag", user_id=1)
        task.tags.append(tag)
        db.add(task)
        db.commit()

        response = client.delete(f"/tags/{tag.id}", headers=auth_headers)
        assert response.status_code == 204

    def test_user_cannot_delete_others_tag(self, client, auth_headers_user2, db):
        from app.models import Tag
        tag = Tag(name="work", user_id=1)
        db.add(tag)
        db.commit()
        db.refresh(tag)

        response = client.delete(f"/tags/{tag.id}", headers=auth_headers_user2)
        assert response.status_code == 404
