import os
import sys

import pytest
from httpx import AsyncClient, ASGITransport
from tortoise import Tortoise

from reset_database import init

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app import models
from app.main import app as fastapi_app

sys.modules['app_system'] = models
transport = ASGITransport(app=fastapi_app)


@pytest.fixture(scope="function", autouse=True)
async def initialize_tests():
    await Tortoise.init(
        config={
            'connections': {
                'app_system': 'sqlite://:memory:',
            },
            'apps': {
                'app_system': {
                    'models': ['app.models'],
                    'default_connection': 'app_system',
                },
            },
        }
    )
    await Tortoise.generate_schemas()
    # 插入初始用户数据
    await init()

    yield

    await Tortoise.close_connections()


@pytest.fixture
async def async_client():
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        yield client


@pytest.fixture
async def auth_headers(async_client: AsyncClient):
    login_data = {
        "username": "Super",
        "password": "123456"
    }
    response = await async_client.post("/api/v1/auth/token", data=login_data)
    print(response.url)
    assert response.status_code == 200
    data = response.json()
    token = data["access_token"]
    headers = {"Authorization": f"Bearer {token}"}
    return headers
