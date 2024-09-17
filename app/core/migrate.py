from aerich import Command

from app.core.config import APP_SETTINGS


async def migrate_db():
    command = Command(tortoise_config=APP_SETTINGS.TORTOISE_ORM, app="app_system")
    try:
        await command.init_db(safe=True)
    except FileExistsError:
        pass

    await command.init()
    await command.migrate()
    await command.upgrade(run_in_transaction=True)
