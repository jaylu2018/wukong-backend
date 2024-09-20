from pathlib import Path

from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    VERSION: str = "0.1.0"
    APP_TITLE: str = "FastSoyAdmin"
    PROJECT_NAME: str = "FastSoyAdmin"
    APP_DESCRIPTION: str = "Description"

    CORS_ORIGINS: list = ["*"]
    CORS_ALLOW_CREDENTIALS: bool = True
    CORS_ALLOW_METHODS: list = ["*"]
    CORS_ALLOW_HEADERS: list = ["*"]

    ADD_LOG_ORIGINS_INCLUDE: list = ["*"]  # APILoggerMiddleware and APILoggerAddResponseMiddleware
    ADD_LOG_ORIGINS_DECLUDE: list = ["/system-manage", "/redoc", "/doc", "/openapi.json"]

    DEBUG: bool = True

    PROJECT_ROOT: Path = Path(__file__).resolve().parent.parent
    BASE_DIR: Path = PROJECT_ROOT.parent
    LOGS_ROOT: Path = BASE_DIR / "app/logs"
    SECRET_KEY: str = "015a42020f023ac2c3eda3d45fe5ca3fef8921ce63589f6d4fcdef9814cd7fa7"  # python -c "from passlib import pwd; print(pwd.genword(length=64, charset='hex'))"
    JWT_ALGORITHM: str = "HS256"
    JWT_ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 12  # 12 hours
    JWT_REFRESH_TOKEN_EXPIRE_MINUTES: int = 60 * 24 * 7  # 7 days
    TORTOISE_ORM: dict = {
        "connections": {
            "conn_system": {
                "engine": "tortoise.backends.sqlite",
                "credentials": {"file_path": f"{BASE_DIR}/db_system.sqlite3"},
            },
        },
        "apps": {
            "app_system": {"models": [
                "app.models.user",
                "app.models.role",
                "app.models.menu",
                "app.models.api",
                "app.models.button",
                "app.models.log",
                "aerich.models"
            ], "default_connection": "conn_system"},
        },
        "use_tz": False,
        "timezone": "Asia/Shanghai",
    }
    DATETIME_FORMAT: str = "%Y-%m-%d %H:%M:%S"


APP_SETTINGS = Settings()
TORTOISE_ORM = APP_SETTINGS.TORTOISE_ORM
