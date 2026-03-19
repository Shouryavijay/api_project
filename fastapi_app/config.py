import os

MYSQL_DATABASE = os.environ.get("MYSQL_DATABASE", "notes_api")
MYSQL_USER = os.environ.get("MYSQL_USER", "notes_user")
MYSQL_PASSWORD = os.environ.get("MYSQL_PASSWORD", "notes_pass_123")
MYSQL_HOST = os.environ.get("MYSQL_HOST", "localhost")
MYSQL_PORT = os.environ.get("MYSQL_PORT", "3306")

DATABASE_URL = os.environ.get(
    "FASTAPI_DATABASE_URL",
    f"mysql+pymysql://{MYSQL_USER}:{MYSQL_PASSWORD}@{MYSQL_HOST}:{MYSQL_PORT}/{MYSQL_DATABASE}",
)

JWT_SECRET_KEY = os.environ.get("FASTAPI_JWT_SECRET_KEY", "change-this-fastapi-secret")
JWT_ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.environ.get("FASTAPI_ACCESS_TOKEN_EXPIRE_MINUTES", "30"))
