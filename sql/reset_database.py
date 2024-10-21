import os

from app.utils.public import refresh_api_list
from app.core.settings import TORTOISE_ORM

from tortoise import Tortoise, run_async
from loguru import logger


async def init():
    await Tortoise.init(
        config=TORTOISE_ORM,
    )
    await Tortoise.generate_schemas()

    conn = Tortoise.get_connection("conn_system")
    # 获取所有表名
    total, tables = await conn.execute_query('SELECT name FROM sqlite_master WHERE type="table";')  # 删除所有表
    for table in tables:
        table_name = table[0]
        if table_name != "aerich":
            await conn.execute_query(f'DELETE FROM "{table_name}";')

    # 获取当前脚本所在目录
    current_dir = os.path.dirname(os.path.abspath(__file__))

    # 使用 SQL 文件初始化数据
    sql_files = [
        "roles.sql",
        "menus.sql",
        "departments.sql",
        "users.sql",
        "users_departments.sql",
        "roles_menus.sql",
        "users_roles.sql",
        "apis.sql"
    ]
    for sql_file in sql_files:
        sql_file_path = os.path.join(current_dir, sql_file)
        with open(sql_file_path, "r") as f:
            print(f"Reset table {sql_file}")
            sql_commands = f.read()
            await conn.execute_script(sql_commands)  # 使用 execute_script 执行 SQL 文件

    await refresh_api_list()

    await Tortoise.close_connections()


if __name__ == "__main__":
    run_async(init())
    logger.info("Reset all tables")
