import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_route_exists(async_client: AsyncClient, auth_headers):
    route_name = "关于"
    response = await async_client.get(f"/api/v1/routes/{route_name}/exists", headers=auth_headers)
    assert response.status_code == 200
    json_data = response.json()
    assert isinstance(json_data["data"], bool)


@pytest.mark.asyncio
async def test_get_routes(async_client: AsyncClient, auth_headers):
    response = await async_client.get("/api/v1/routes", headers=auth_headers)
    assert response.status_code == 200
    json_data = response.json()
    assert "data" in json_data


@pytest.mark.asyncio
async def test_get_route(async_client: AsyncClient, auth_headers):
    route_id = 1
    response = await async_client.get(f"/api/v1/routes/{route_id}", headers=auth_headers)
    assert response.status_code == 200
    json_data = response.json()
    assert "data" in json_data


@pytest.mark.asyncio
async def test_create_route(async_client: AsyncClient, auth_headers):
    route_data = {
        "menuName": "测试路由",
        "routePath": "/test-route",
        "component": "component_path",
        "order": 1,
        "parentId": 0
    }
    response = await async_client.post("/api/v1/routes", json=route_data, headers=auth_headers)
    assert response.status_code == 200


@pytest.mark.asyncio
async def test_update_route(async_client: AsyncClient, auth_headers):
    route_id = 1  # 假设路由ID为1
    route_update_data = {
        "menuName": "更新后的测试路由"
    }
    response = await async_client.patch(f"/api/v1/routes/{route_id}", json=route_update_data, headers=auth_headers)
    assert response.status_code == 200
    json_data = response.json()
    assert json_data["data"]["menuId"] == route_id


@pytest.mark.asyncio
async def test_delete_route(async_client: AsyncClient, auth_headers):
    route_id = 1  # 假设路由ID为1
    response = await async_client.delete(f"/api/v1/routes/{route_id}", headers=auth_headers)
    assert response.status_code == 200
    json_data = response.json()
    assert json_data["data"]["menuId"] == route_id


@pytest.mark.asyncio
async def test_batch_delete_routes(async_client: AsyncClient, auth_headers):
    ids = "1"
    response = await async_client.delete(f"/api/v1/routes/?ids={ids}", headers=auth_headers)
    assert response.status_code == 200
    json_data = response.json()
    assert "deleted_ids" in json_data["data"]
