import pytest

from app.models.user import User
from app.services.auth import hash_password

TEST_EMAIL = "test@example.com"
TEST_PASSWORD = "securepassword123"
TEST_NAME = "Test User"


async def _create_user(db_session) -> User:
    user = User(
        email=TEST_EMAIL,
        hashed_password=hash_password(TEST_PASSWORD),
        full_name=TEST_NAME,
    )
    db_session.add(user)
    await db_session.commit()
    await db_session.refresh(user)
    return user


@pytest.mark.asyncio
class TestLogin:
    async def test_login_success(self, client, db_session):
        await _create_user(db_session)
        response = await client.post(
            "/api/v1/auth/login",
            json={"email": TEST_EMAIL, "password": TEST_PASSWORD},
        )
        assert response.status_code == 200
        data = response.json()
        assert "access_token" in data
        assert "refresh_token" in data
        assert data["token_type"] == "bearer"
        assert "expires_at" in data

    async def test_login_wrong_password(self, client, db_session):
        await _create_user(db_session)
        response = await client.post(
            "/api/v1/auth/login",
            json={"email": TEST_EMAIL, "password": "wrongpassword"},
        )
        assert response.status_code == 401

    async def test_login_nonexistent_user(self, client):
        response = await client.post(
            "/api/v1/auth/login",
            json={"email": "nobody@example.com", "password": TEST_PASSWORD},
        )
        assert response.status_code == 401


@pytest.mark.asyncio
class TestMe:
    async def test_me_with_valid_token(self, client, db_session):
        await _create_user(db_session)
        login_resp = await client.post(
            "/api/v1/auth/login",
            json={"email": TEST_EMAIL, "password": TEST_PASSWORD},
        )
        token = login_resp.json()["access_token"]

        response = await client.get(
            "/api/v1/auth/me",
            headers={"Authorization": f"Bearer {token}"},
        )
        assert response.status_code == 200
        data = response.json()
        assert data["email"] == TEST_EMAIL

    async def test_me_without_token(self, client):
        response = await client.get("/api/v1/auth/me")
        assert response.status_code == 401

    async def test_me_with_invalid_token(self, client):
        response = await client.get(
            "/api/v1/auth/me",
            headers={"Authorization": "Bearer invalidtoken123"},
        )
        assert response.status_code == 401

    async def test_me_with_refresh_token_rejected(self, client, db_session):
        await _create_user(db_session)
        login_resp = await client.post(
            "/api/v1/auth/login",
            json={"email": TEST_EMAIL, "password": TEST_PASSWORD},
        )
        refresh_token = login_resp.json()["refresh_token"]

        response = await client.get(
            "/api/v1/auth/me",
            headers={"Authorization": f"Bearer {refresh_token}"},
        )
        assert response.status_code == 401


@pytest.mark.asyncio
class TestRefresh:
    async def test_refresh_success(self, client, db_session):
        await _create_user(db_session)
        login_resp = await client.post(
            "/api/v1/auth/login",
            json={"email": TEST_EMAIL, "password": TEST_PASSWORD},
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

    async def test_refresh_with_access_token_rejected(self, client, db_session):
        await _create_user(db_session)
        login_resp = await client.post(
            "/api/v1/auth/login",
            json={"email": TEST_EMAIL, "password": TEST_PASSWORD},
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
