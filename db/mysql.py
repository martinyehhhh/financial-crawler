import pymysql
from config import DB_CONFIG

def get_connection():
    return pymysql.connect(
        host=DB_CONFIG['host'],
        user=DB_CONFIG['user'],
        password=DB_CONFIG['password'],
        database=DB_CONFIG['database'],
        port=DB_CONFIG['port'],
        charset='utf8mb4',
        cursorclass=pymysql.cursors.DictCursor
    )