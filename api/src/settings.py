import sys
import os
from decouple import config, Csv

# Set the search path to the 'config' directory
config.search_path = str(os.path.realpath(os.path.join(os.path.dirname(__file__), "config")))


DEBUG_MODE = config("DEBUG", cast=bool, default=False)

AT_LEAST_ONE_ADMIN_USER = config("AT_LEAST_ONE_ADMIN_USER", cast=bool)
FIRST_USER_IS_ADMIN = config("FIRST_USER_IS_ADMIN", cast=bool)
API_ROOT_PATH = config("API_ROOT_PATH", cast=str, default="")

SYNC_DB_URI = config("SYNC_DB_URI", cast=str)
ASYNC_DB_URI = config("ASYNC_DB_URI", cast=str)
AUTO_CREATE_TABLES = config("AUTO_CREATE_TABLES", cast=bool, default=False)

CORS_ORIGINS = config("CORS_ORIGINS", cast=Csv(cast=str, strip=' '), default='')

GOOGLE_CLIENT_ID = config("GOOGLE_CLIENT_ID", cast=str)

JWT_ACCESS_SECRET_KEY = config("JWT_ACCESS_SECRET_KEY", cast=str)
JWT_REFRESH_SECRET_KEY = config("JWT_REFRESH_SECRET_KEY", cast=str)
JWT_ACCESS_TOKEN_EXPIRE_MINUTES = config("JWT_ACCESS_TOKEN_EXPIRE_MINUTES", cast=int, default=30)
JWT_REFRESH_TOKEN_EXPIRE_MINUTES = config("JWT_REFRESH_TOKEN_EXPIRE_MINUTES", cast=int, default=1440)  # 1 day
