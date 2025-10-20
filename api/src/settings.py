import sys
import os
from decouple import config, Csv

# Set the search path to the 'config' directory
config.search_path = str(os.path.realpath(os.path.join(os.path.dirname(__file__), "config")))


DEBUG_MODE = config("DEBUG", cast=bool, default=False)

DB_URI = config("DB_URI", cast=str)

CORS_ORIGINS = config("CORS_ORIGINS", cast=Csv(cast=str), default='')

GOOGLE_CLIENT_ID = config("GOOGLE_CLIENT_ID", cast=str)

JWT_ACCESS_SECRET_KEY = config("JWT_ACCESS_SECRET_KEY", cast=str)
JWT_REFRESH_SECRET_KEY = config("JWT_REFRESH_SECRET_KEY", cast=str)
JWT_ACCESS_TOKEN_EXPIRE_MINUTES = config("JWT_ACCESS_TOKEN_EXPIRE_MINUTES", cast=int, default=30)
JWT_REFRESH_TOKEN_EXPIRE_MINUTES = config("JWT_REFRESH_TOKEN_EXPIRE_MINUTES", cast=int, default=1440)  # 1 day
