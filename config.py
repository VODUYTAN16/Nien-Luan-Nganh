# config.py
import os
from sqlalchemy.engine import URL

MYSQL_USER = "root"
MYSQL_PASSWORD = "Admin@123"   # đúng mật khẩu MySQL của bạn
MYSQL_HOST = "localhost"
MYSQL_PORT = 3306
MYSQL_DB = "crochet_db"

DB_URL = URL.create(
    drivername="mysql+pymysql",
    username=MYSQL_USER,
    password=MYSQL_PASSWORD,
    host=MYSQL_HOST,
    port=MYSQL_PORT,
    database=MYSQL_DB,
    query={"charset": "utf8mb4"},
)

JWT_SECRET = "supersecret_change_me"
JWT_ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60 * 24

STATIC_TOP_DIR = "static/top"
STATIC_BOT_DIR = "static/bot"
