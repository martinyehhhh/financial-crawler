from db.mysql import get_connection

def test_connection():
    try:
        conn = get_connection()
        with conn.cursor() as cursor:
            cursor.execute("SELECT DATABASE();")
            db = cursor.fetchone()
            print(f"✅ 連線成功，目前使用資料庫：{db['DATABASE()']}")
    except Exception as e:
        print(f"❌ 連線失敗：{e}")
    finally:
        conn.close()

if __name__ == "__main__":
    test_connection()