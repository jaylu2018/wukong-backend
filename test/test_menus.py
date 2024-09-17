import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_get_menus(async_client: AsyncClient, auth_headers):
    response = await async_client.get("/api/v1/system/menus", headers=auth_headers)
    assert response.status_code == 200
    json_data = response.json()
    assert "records" in json_data["data"]


@pytest.mark.asyncio
async def test_get_menu_tree(async_client: AsyncClient, auth_headers):
    response = await async_client.get("/api/v1/system/menus/tree/", headers=auth_headers)
    assert response.status_code == 200
    json_data = response.json()
    assert isinstance(json_data["data"], list)


@pytest.mark.asyncio
async def test_get_menu(async_client: AsyncClient, auth_headers):
    response = await async_client.get(f"/api/v1/system/menus/1", headers=auth_headers)
    assert response.status_code == 200
    json_data = response.json()
    assert "data" in json_data


@pytest.mark.asyncio
async def test_create_menu(async_client: AsyncClient, auth_headers):
    menu_data = {
        "menuName": "测试菜单",
        "routePath": "/test-menu",
        "component": "layout.base$view.test",
        "order": 1,
        "parentId": 0
    }
    response = await async_client.post("/api/v1/system/menus", json=menu_data, headers=auth_headers)
    assert response.status_code == 200
    # json_data = response.json()
    # assert "created_id" in json_data["data"]


@pytest.mark.asyncio
async def test_update_menu(async_client: AsyncClient, auth_headers):
    menu_update_data = {
        "menuName": "更新后的测试菜单"
    }
    response = await async_client.patch(f"/api/v1/system/menus/1", json=menu_update_data, headers=auth_headers)
    assert response.status_code == 200
    # json_data = response.json()
    # assert json_data["data"]["updated_id"] == 1


@pytest.mark.asyncio
async def test_delete_menu(async_client: AsyncClient, auth_headers):
    response = await async_client.delete(f"/api/v1/system/menus/1", headers=auth_headers)
    assert response.status_code == 200
    # json_data = response.json()
    # assert json_data["data"]["deleted_id"] == 1


@pytest.mark.asyncio
async def test_batch_delete_menus(async_client: AsyncClient, auth_headers):
    ids = "1,2,3"
    response = await async_client.delete(f"/api/v1/system/menus?ids={ids}", headers=auth_headers)
    assert response.status_code == 200
    # json_data = response.json()
    # assert "deleted_ids" in json_data["data"]


@pytest.mark.asyncio
async def test_get_first_level_menus(async_client: AsyncClient, auth_headers):
    response = await async_client.get("/api/v1/system/menus/pages/", headers=auth_headers)
    assert response.status_code == 200
    json_data = response.json()
    assert isinstance(json_data["data"], list)


@pytest.mark.asyncio
async def test_get_menu_button_tree(async_client: AsyncClient, auth_headers):
    response = await async_client.get("/api/v1/system/menus/buttons/tree/", headers=auth_headers)
    assert response.status_code == 200
    json_data = response.json()
    assert isinstance(json_data["data"], list)
