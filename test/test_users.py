import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_get_users(async_client: AsyncClient, auth_headers):
    response = await async_client.get("/api/v1/system/users", headers=auth_headers)
    assert response.status_code == 200
    # json_data = response.json()
    # assert "records" in json_data["data"]


@pytest.mark.asyncio
async def test_get_user(async_client: AsyncClient, auth_headers):
    user_id = 1
    response = await async_client.get(f"/api/v1/system/users/{user_id}", headers=auth_headers)
    assert response.status_code == 200
    json_data = response.json()
    assert "data" in json_data


@pytest.mark.asyncio
async def test_create_user(async_client: AsyncClient, auth_headers):
    user_data = {
        "userName": "TestUser",
        "password": "TestPassword123",
        "userEmail": "testuser@example.com"
    }
    response = await async_client.post("/api/v1/system/users", json=user_data, headers=auth_headers)
    assert response.status_code == 200
    # json_data = response.json()
    # assert "created_id" in json_data["data"]


@pytest.mark.asyncio
async def test_update_user(async_client: AsyncClient, auth_headers):
    user_id = 1
    user_update_data = {
        "nickName": "更新后的昵称"
    }
    response = await async_client.patch(f"/api/v1/system/users/{user_id}", json=user_update_data, headers=auth_headers)
    assert response.status_code == 200
    # json_data = response.json()
    # assert json_data["data"]["updated_id"] == user_id


@pytest.mark.asyncio
async def test_delete_user(async_client: AsyncClient, auth_headers):
    user_id = 1
    response = await async_client.delete(f"/api/v1/system/users/{user_id}", headers=auth_headers)
    assert response.status_code == 200
    # json_data = response.json()
    # assert json_data["data"]["deleted_id"] == user_id


@pytest.mark.asyncio
async def test_batch_delete_users(async_client: AsyncClient, auth_headers):
    ids = "1"
    response = await async_client.delete(f"/api/v1/system/users/?ids={ids}", headers=auth_headers)
    assert response.status_code == 200
    # json_data = response.json()
    # assert "deleted_ids" in json_data["data"]
