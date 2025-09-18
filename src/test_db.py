# test_db.py
import sqlite3
import os

def check_database():
    # 根据你的实际数据库路径调整
    db_path = "utils/traffic.db"

    print("=== 数据库检查 ===")

    # 检查数据库文件是否存在
    if os.path.exists(db_path):
        print(f"✓ 数据库文件存在: {os.path.abspath(db_path)}")
    else:
        print(f"✗ 数据库文件不存在: {os.path.abspath(db_path)}")
        return

    try:
        # 连接数据库
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()

        # 检查有哪些表
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
        tables = cursor.fetchall()
        print(f"\n数据库中的表:")
        for table in tables:
            print(f"  - {table[0]}")

        # 检查每个表的数据量
        for table in tables:
            table_name = table[0]
            cursor.execute(f"SELECT COUNT(*) FROM {table_name}")
            count = cursor.fetchone()[0]
            print(f"\n{table_name} 表记录数: {count}")

            # 如果表中有数据，显示前几条记录
            if count > 0:
                cursor.execute(f"SELECT * FROM {table_name} LIMIT 3")
                rows = cursor.fetchall()
                print(f"{table_name} 表前3条记录:")
                for i, row in enumerate(rows):
                    print(f"  {i+1}. {row}")

        conn.close()

    except Exception as e:
        print(f"检查数据库时出错: {e}")

if __name__ == "__main__":
    check_database()
