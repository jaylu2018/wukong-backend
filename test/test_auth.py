import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_login_for_access_token(async_client: AsyncClient):
    data = {
        "username": "Super",
        "password": "123456"
    }
    response = await async_client.post("/api/v1/auth/token", data=data)
    assert response.status_code == 200
    json_data = response.json()
    assert "access_token" in json_data
    assert json_data["token_type"] == "bearer"


@pytest.mark.asyncio
async def test_login(async_client: AsyncClient):
    credentials = {
        "userName": "Super",
        "password": "123456"
    }
    response = await async_client.post("/api/v1/auth/login", json=credentials)
    assert response.status_code == 200
    json_data = response.json()
    assert "access_token" in json_data
    assert json_data["token_type"] == "bearer"


@pytest.mark.asyncio
async def test_logout(async_client: AsyncClient, auth_headers):
    response = await async_client.post("/api/v1/auth/logout", headers=auth_headers)
    assert response.status_code == 200
    json_data = response.json()
    assert json_data["msg"] == "Logged out successfully"


@pytest.mark.asyncio
async def test_read_users_me(async_client: AsyncClient, auth_headers):
    response = await async_client.get("/api/v1/auth/me", headers=auth_headers)
    assert response.status_code == 200
    json_data = response.json()
    assert "username" in json_data
    assert "email" in json_data
