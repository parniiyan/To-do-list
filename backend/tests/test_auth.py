import pytest


class TestAuthRegistration:
    def test_register_new_user(self, client):
        response = client.post(
            "/auth/register",
            json={"email": "newuser@example.com", "password": "password123"}
        )
        assert response.status_code == 201
        data = response.json()
        assert data["email"] == "newuser@example.com"
        assert "id" in data
        assert "created_at" in data
        assert "password" not in data

    def test_register_duplicate_email(self, client, user):
        response = client.post(
            "/auth/register",
            json={"email": user[0]["email"], "password": "password123"}
        )
        assert response.status_code == 400
        assert "already registered" in response.json()["detail"]

    def test_register_invalid_email(self, client):
        response = client.post(
            "/auth/register",
            json={"email": "not-an-email", "password": "password123"}
        )
        assert response.status_code == 201


class TestAuthLogin:
    def test_login_success(self, client, user):
        response = client.post(
            "/auth/login",
            data={"username": user[0]["email"], "password": user[0]["password"]}
        )
        assert response.status_code == 200
        data = response.json()
        assert "access_token" in data
        assert data["token_type"] == "bearer"

    def test_login_wrong_password(self, client, user):
        response = client.post(
            "/auth/login",
            data={"username": user[0]["email"], "password": "wrongpassword"}
        )
        assert response.status_code == 401
        assert "Incorrect email or password" in response.json()["detail"]

    def test_login_nonexistent_user(self, client):
        response = client.post(
            "/auth/login",
            data={"username": "nonexistent@example.com", "password": "password123"}
        )
        assert response.status_code == 401

    def test_login_missing_fields(self, client):
        response = client.post(
            "/auth/login",
            data={"username": "test@example.com"}
        )
        assert response.status_code == 422


class TestAuthMe:
    def test_get_current_user(self, client, auth_headers):
        response = client.get("/auth/me", headers=auth_headers)
        assert response.status_code == 200
        data = response.json()
        assert data["email"] == "test@example.com"

    def test_get_current_user_no_token(self, client):
        response = client.get("/auth/me")
        assert response.status_code == 401

    def test_get_current_user_invalid_token(self, client):
        response = client.get(
            "/auth/me",
            headers={"Authorization": "Bearer invalid_token"}
        )
        assert response.status_code == 401
