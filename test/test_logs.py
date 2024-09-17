import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_get_logs(async_client: AsyncClient, auth_headers):
    response = await async_client.get("/api/v1/log/logs", headers=auth_headers)
    assert response.status_code == 200
    json_data = response.json()
    assert "records" in json_data["data"]


@pytest.mark.asyncio
async def test_get_log(async_client: AsyncClient, auth_headers):
    # 假设日志ID为1
    response = await async_client.get(f"/api/v1/log/logs/1", headers=auth_headers)
    assert response.status_code == 200
    json_data = response.json()
    assert "data" in json_data


@pytest.mark.asyncio
async def test_update_log(async_client: AsyncClient, auth_headers):
    log_update_data = {
        "logDetail": "更新日志详情"
    }
    response = await async_client.patch(f"/api/v1/log/logs/1", json=log_update_data, headers=auth_headers)
    assert response.status_code == 200
    json_data = response.json()
    assert json_data["msg"] == "Success"


@pytest.mark.asyncio
async def test_delete_log(async_client: AsyncClient, auth_headers):
    response = await async_client.delete(f"/api/v1/log/logs/1", headers=auth_headers)
    assert response.status_code == 200
    json_data = response.json()
    # print(json_data)
    # assert json_data["data"]["deleted_id"] == 1


@pytest.mark.asyncio
async def test_batch_delete_logs(async_client: AsyncClient, auth_headers):
    ids = "1,2,3"
    response = await async_client.delete(f"/api/v1/log/logs?ids={ids}", headers=auth_headers)
    assert response.status_code == 200
    # json_data = response.json()
    # assert "deleted_ids" in json_data["data"]
