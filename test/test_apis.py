import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_get_apis(async_client: AsyncClient, auth_headers):
    response = await async_client.get("/api/v1/system/apis", headers=auth_headers)
    assert response.status_code == 200
    # json_data = response.json()
    # assert "records" in json_data["data"]


@pytest.mark.asyncio
async def test_get_api(async_client: AsyncClient, auth_headers):
    response = await async_client.get(f"/api/v1/system/apis/1", headers=auth_headers)
    assert response.status_code == 200
    # json_data = response.json()
    # assert "data" in json_data


@pytest.mark.asyncio
async def test_create_api(async_client: AsyncClient, auth_headers):
    api_data = {
        "path": "/api/v1/test-api",
        "method": "get",
        "summary": "测试API",
        "tags": ["测试"],
        "status": "1"
    }
    response = await async_client.post("/api/v1/system/apis", json=api_data, headers=auth_headers)
    assert response.status_code == 200
    # json_data = response.json()
    # assert "created_id" in json_data["data"]


@pytest.mark.asyncio
async def test_update_api(async_client: AsyncClient, auth_headers):
    api_update_data = {
        "summary": "更新后的测试API"
    }
    response = await async_client.patch(f"/api/v1/system/apis/1", json=api_update_data, headers=auth_headers)
    assert response.status_code == 200
    # json_data = response.json()
    # assert json_data["data"]["updated_id"] == 1


@pytest.mark.asyncio
async def test_batch_delete_apis(async_client: AsyncClient, auth_headers):
    ids = "1,2,3"
    response = await async_client.delete(f"/api/v1/system/apis?ids={ids}", headers=auth_headers)
    assert response.status_code == 200
    # json_data = response.json()
    # assert "deleted_ids" in json_data["data"]


@pytest.mark.asyncio
async def test_get_api_tree(async_client: AsyncClient, auth_headers):
    response = await async_client.get("/api/v1/system/apis/tree/", headers=auth_headers)
    assert response.status_code == 200
    json_data = response.json()
    assert isinstance(json_data["data"], list)
