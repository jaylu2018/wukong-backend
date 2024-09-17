import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_get_roles(async_client: AsyncClient, auth_headers):
    response = await async_client.get("/api/v1/system/roles", headers=auth_headers)
    assert response.status_code == 200
    json_data = response.json()
    assert "records" in json_data["data"]


@pytest.mark.asyncio
async def test_get_role(async_client: AsyncClient, auth_headers):
    response = await async_client.get(f"/api/v1/system/roles/1", headers=auth_headers)
    assert response.status_code == 200
    json_data = response.json()
    assert "data" in json_data


@pytest.mark.asyncio
async def test_create_role(async_client: AsyncClient, auth_headers):
    role_data = {
        "roleName": "测试角色",
        "roleCode": "TEST_ROLE"
    }
    response = await async_client.post("/api/v1/system/roles", json=role_data, headers=auth_headers)
    assert response.status_code == 200
    # json_data = response.json()
    # assert "created_id" in json_data["data"]


@pytest.mark.asyncio
async def test_update_role(async_client: AsyncClient, auth_headers):
    role_update_data = {
        "roleName": "更新后的测试角色"
    }
    response = await async_client.patch(f"/api/v1/system/roles/1", json=role_update_data, headers=auth_headers)
    assert response.status_code == 200
    # json_data = response.json()
    # assert json_data["data"]["updated_id"] == 1


@pytest.mark.asyncio
async def test_delete_role(async_client: AsyncClient, auth_headers):
    response = await async_client.delete(f"/api/v1/system/roles/1", headers=auth_headers)
    assert response.status_code == 200
    # json_data = response.json()
    # assert json_data["data"]["deleted_id"] == 1


@pytest.mark.asyncio
async def test_batch_delete_roles(async_client: AsyncClient, auth_headers):
    ids = "1,2,3"
    response = await async_client.delete(f"/api/v1/system/roles?ids={ids}", headers=auth_headers)
    assert response.status_code == 200
    # json_data = response.json()
    # assert "deleted_ids" in json_data["data"]


@pytest.mark.asyncio
async def test_get_role_menus(async_client: AsyncClient, auth_headers):
    response = await async_client.get(f"/api/v1/system/roles/1/menus", headers=auth_headers)
    assert response.status_code == 200
    json_data = response.json()
    assert "menuIds" in json_data["data"]


@pytest.mark.asyncio
async def test_update_role_menus(async_client: AsyncClient, auth_headers):
    role_menu_data = {
        "menuIds": [1, 2, 3],
        "roleHome": "home"
    }
    response = await async_client.patch(f"/api/v1/system/roles/1/menus", json=role_menu_data, headers=auth_headers)
    assert response.status_code == 200
    # json_data = response.json()
    # assert "updated_menu_ids" in json_data["data"]
