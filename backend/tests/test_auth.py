import pytest


@pytest.mark.asyncio
class TestRegister:
    async def test_register_success(self, client):
        response = await client.post(
            "/api/v1/auth/register",
            json={
                "email": "test@example.com",
                "password": "securepassword123",
                "full_name": "Test User",
            },
        )
        assert response.status_code == 201
        data = response.json()
        assert data["email"] == "test@example.com"
        assert data["full_name"] == "Test User"
        assert data["is_active"] is True
        assert "id" in data

    async def test_register_duplicate_email(self, client):
        payload = {
            "email": "dup@example.com",
            "password": "securepassword123",
            "full_name": "Dup User",
        }
        await client.post("/api/v1/auth/register", json=payload)
        response = await client.post("/api/v1/auth/register", json=payload)
        assert response.status_code == 409

    async def test_register_short_password(self, client):
        response = await client.post(
            "/api/v1/auth/register",
            json={
                "email": "short@example.com",
                "password": "short",
                "full_name": "Short",
            },
        )
        assert response.status_code == 422

    async def test_register_invalid_email(self, client):
        response = await client.post(
            "/api/v1/auth/register",
            json={
                "email": "not-an-email",
                "password": "securepassword123",
                "full_name": "Bad Email",
            },
        )
        assert response.status_code == 422


@pytest.mark.asyncio
class TestLogin:
    async def test_login_success(self, client):
        await client.post(
            "/api/v1/auth/register",
            json={
                "email": "login@example.com",
                "password": "securepassword123",
                "full_name": "Login User",
            },
        )
        response = await client.post(
            "/api/v1/auth/login",
            json={
                "email": "login@example.com",
                "password": "securepassword123",
            },
        )
        assert response.status_code == 200
        data = response.json()
        assert "access_token" in data
        assert "refresh_token" in data
        assert data["token_type"] == "bearer"
        assert "expires_at" in data

    async def test_login_wrong_password(self, client):
        await client.post(
            "/api/v1/auth/register",
            json={
                "email": "wrong@example.com",
                "password": "securepassword123",
                "full_name": "Wrong User",
            },
        )
        response = await client.post(
            "/api/v1/auth/login",
            json={
                "email": "wrong@example.com",
                "password": "wrongpassword",
            },
        )
        assert response.status_code == 401

    async def test_login_nonexistent_user(self, client):
        response = await client.post(
            "/api/v1/auth/login",
            json={
                "email": "nobody@example.com",
                "password": "securepassword123",
            },
        )
        assert response.status_code == 401


@pytest.mark.asyncio
class TestMe:
    async def test_me_with_valid_token(self, client):
        await client.post(
            "/api/v1/auth/register",
            json={
                "email": "me@example.com",
                "password": "securepassword123",
                "full_name": "Me User",
            },
        )
        login_resp = await client.post(
            "/api/v1/auth/login",
            json={"email": "me@example.com", "password": "securepassword123"},
        )
        token = login_resp.json()["access_token"]

        response = await client.get(
            "/api/v1/auth/me",
            headers={"Authorization": f"Bearer {token}"},
        )
        assert response.status_code == 200
        data = response.json()
        assert data["email"] == "me@example.com"

    async def test_me_without_token(self, client):
        response = await client.get("/api/v1/auth/me")
        assert response.status_code == 401

    async def test_me_with_invalid_token(self, client):
        response = await client.get(
            "/api/v1/auth/me",
            headers={"Authorization": "Bearer invalidtoken123"},
        )
        assert response.status_code == 401

    async def test_me_with_refresh_token_rejected(self, client):
        await client.post(
            "/api/v1/auth/register",
            json={
                "email": "refresh@example.com",
                "password": "securepassword123",
                "full_name": "Refresh User",
            },
        )
        login_resp = await client.post(
            "/api/v1/auth/login",
            json={"email": "refresh@example.com", "password": "securepassword123"},
        )
        refresh_token = login_resp.json()["refresh_token"]

        response = await client.get(
            "/api/v1/auth/me",
            headers={"Authorization": f"Bearer {refresh_token}"},
        )
        assert response.status_code == 401


@pytest.mark.asyncio
class TestRefresh:
    async def test_refresh_success(self, client):
        await client.post(
            "/api/v1/auth/register",
            json={
                "email": "refresh2@example.com",
                "password": "securepassword123",
                "full_name": "Refresh2 User",
            },
        )
        login_resp = await client.post(
            "/api/v1/auth/login",
            json={"email": "refresh2@example.com", "password": "securepassword123"},
        )
        refresh_token = login_resp.json()["refresh_token"]

        response = await client.post(
            "/api/v1/auth/refresh",
            json={"refresh_token": refresh_token},
        )
        assert response.status_code == 200
        data = response.json()
        assert "access_token" in data
        assert "refresh_token" in data

    async def test_refresh_with_access_token_rejected(self, client):
        await client.post(
            "/api/v1/auth/register",
            json={
                "email": "access@example.com",
                "password": "securepassword123",
                "full_name": "Access User",
            },
        )
        login_resp = await client.post(
            "/api/v1/auth/login",
            json={"email": "access@example.com", "password": "securepassword123"},
        )
        access_token = login_resp.json()["access_token"]

        response = await client.post(
            "/api/v1/auth/refresh",
            json={"refresh_token": access_token},
        )
        assert response.status_code == 401

    async def test_refresh_with_invalid_token(self, client):
        response = await client.post(
            "/api/v1/auth/refresh",
            json={"refresh_token": "invalidtoken"},
        )
        assert response.status_code == 401
