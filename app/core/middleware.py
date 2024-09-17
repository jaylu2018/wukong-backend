from starlette.middleware import Middleware
from starlette.middleware.cors import CORSMiddleware

from app.core.config import APP_SETTINGS


def make_middlewares():
    middleware = [
        Middleware(
            CORSMiddleware,
            allow_origins=APP_SETTINGS.CORS_ORIGINS,
            allow_credentials=APP_SETTINGS.CORS_ALLOW_CREDENTIALS,
            allow_methods=APP_SETTINGS.CORS_ALLOW_METHODS,
            allow_headers=APP_SETTINGS.CORS_ALLOW_HEADERS,
        ),
    ]
    return middleware
