import pytest


class TestTagCreate:
    def test_create_tag_without_auth(self, client):
        response = client.post(
            "/tags",
            json={"name": "work", "color": "#ff0000"}
        )
        assert response.status_code == 201
        data = response.json()
        assert data["name"] == "work"
        assert data["color"] == "#ff0000"
        assert data["user_id"] is None

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

    def test_create_tag_default_color(self, client):
        response = client.post(
            "/tags",
            json={"name": "tag"}
        )
        assert response.status_code == 201
        assert response.json()["color"] == "#6b7280"

    def test_create_tag_missing_name(self, client):
        response = client.post(
            "/tags",
            json={"color": "#ff0000"}
        )
        assert response.status_code == 422


class TestTagRead:
    def test_get_all_tags_without_auth(self, client, public_tag):
        response = client.get("/tags")
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 1
        assert data[0]["name"] == "public"

    def test_get_all_tags_with_auth(self, client, auth_headers, public_tag, tag):
        response = client.get("/tags", headers=auth_headers)
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 2


class TestTagDelete:
    def test_delete_tag(self, client, public_tag, db):
        from app.models import Tag

        response = client.delete(f"/tags/{public_tag.id}")
        assert response.status_code == 204

        tag = db.query(Tag).filter(Tag.id == public_tag.id).first()
        assert tag is None

    def test_delete_tag_not_found(self, client):
        response = client.delete("/tags/9999")
        assert response.status_code == 404

    def test_delete_tag_with_tasks(self, client, db, public_tag):
        from app.models import Task

        task = Task(title="Task with tag")
        task.tags.append(public_tag)
        db.add(task)
        db.commit()

        response = client.delete(f"/tags/{public_tag.id}")
        assert response.status_code == 204

    def test_user_cannot_delete_others_tag(self, client, auth_headers_user2, tag):
        response = client.delete(f"/tags/{tag.id}", headers=auth_headers_user2)
        assert response.status_code == 404
