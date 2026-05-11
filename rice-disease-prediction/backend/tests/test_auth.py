"""
Tests for authentication endpoints.
"""


class TestRegister:
    def test_register_success(self, client):
        response = client.post("/api/auth/register", json={
            "email": "new@example.com",
            "password": "password123",
            "name": "New User",
        })
        assert response.status_code == 201
        data = response.json()
        assert "access_token" in data
        assert data["token_type"] == "bearer"

    def test_register_duplicate_email(self, client):
        # Register first user
        client.post("/api/auth/register", json={
            "email": "dup@example.com",
            "password": "password123",
            "name": "User One",
        })
        # Try duplicate
        response = client.post("/api/auth/register", json={
            "email": "dup@example.com",
            "password": "password456",
            "name": "User Two",
        })
        assert response.status_code == 409

    def test_register_invalid_email(self, client):
        response = client.post("/api/auth/register", json={
            "email": "ab",
            "password": "password123",
            "name": "Bad Email",
        })
        assert response.status_code == 422

    def test_register_short_password(self, client):
        response = client.post("/api/auth/register", json={
            "email": "short@example.com",
            "password": "12345",
            "name": "Short Pass",
        })
        assert response.status_code == 422


class TestLogin:
    def test_login_success(self, client):
        # Register
        client.post("/api/auth/register", json={
            "email": "login@example.com",
            "password": "password123",
            "name": "Login User",
        })
        # Login
        response = client.post("/api/auth/login", json={
            "email": "login@example.com",
            "password": "password123",
        })
        assert response.status_code == 200
        assert "access_token" in response.json()

    def test_login_wrong_password(self, client):
        client.post("/api/auth/register", json={
            "email": "wrong@example.com",
            "password": "password123",
            "name": "Wrong Pass",
        })
        response = client.post("/api/auth/login", json={
            "email": "wrong@example.com",
            "password": "wrongpassword",
        })
        assert response.status_code == 401

    def test_login_nonexistent_email(self, client):
        response = client.post("/api/auth/login", json={
            "email": "nobody@example.com",
            "password": "password123",
        })
        assert response.status_code == 401


class TestProfile:
    def test_get_profile(self, client, auth_headers):
        response = client.get("/api/auth/me", headers=auth_headers)
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "success"
        assert data["data"]["email"] == "test@example.com"
        assert data["data"]["name"] == "Test User"

    def test_get_profile_unauthorized(self, client):
        response = client.get("/api/auth/me")
        assert response.status_code == 403

    def test_get_profile_invalid_token(self, client):
        response = client.get("/api/auth/me", headers={
            "Authorization": "Bearer invalid-token-here"
        })
        assert response.status_code == 401
