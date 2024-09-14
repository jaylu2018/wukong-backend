import time

from app.api.v1.utils import refresh_api_list
from app.core.config import TORTOISE_ORM
from app.core.exceptions import SettingNotFound
from app.core.init_app import init_users, init_menus

try:
    from app.core.config import APP_SETTINGS
except ImportError:
    raise SettingNotFound("Can not import settings")

from tortoise import Tortoise, run_async
from loguru import logger


async def init():
    await Tortoise.init(
        config=TORTOISE_ORM,
    )
    await Tortoise.generate_schemas()

    conn = Tortoise.get_connection("conn_system")
    # 获取所有表名
    total, tables = await conn.execute_query('SELECT name FROM sqlite_master WHERE type="table";') # 删除所有表
    for table in tables:
        table_name = table[0]
        if table_name != "aerich":
            await conn.execute_query(f'DELETE FROM "{table_name}";')

    # 使用 SQL 文件初始化数据
    sql_files = [
        "sql/roles.sql",
        "sql/menus.sql",
        "sql/buttons.sql",
        "sql/users.sql",
        "sql/roles_menus.sql",
        "sql/roles_buttons.sql",
        "sql/users_roles.sql",
        "sql/apis.sql"
    ]
    for sql_file in sql_files:
        with open(sql_file, "r") as f:
            sql_commands = f.read()
            await conn.execute_script(sql_commands)  # 使用 execute_script 执行 SQL 文件

    await refresh_api_list()

    await Tortoise.close_connections()


while True:
    run_async(init())
    logger.info("Reset all tables")
    time.sleep(60 * 10)
