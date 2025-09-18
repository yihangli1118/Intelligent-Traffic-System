# sqlite_example.py
import sqlite3


def create_connection(db_file):
    """ 创建数据库连接 """
    conn = None
    try:
        conn = sqlite3.connect(db_file)
        return conn
    except sqlite3.Error as e:
        print(e)
    return conn


def create_table(conn):
    """ 创建表 """
    try:
        cursor = conn.cursor()
        cursor.execute('''CREATE TABLE IF NOT EXISTS users
                        (id INTEGER PRIMARY KEY, name TEXT, age INTEGER)''')
    except sqlite3.Error as e:
        print(e)


def insert_user(conn, user):
    """ 插入新用户 """
    try:
        cursor = conn.cursor()
        cursor.execute("INSERT INTO users (name, age) VALUES (?, ?)", user)
        conn.commit()
    except sqlite3.Error as e:
        print(e)


def update_user(conn, user):
    """ 更新用户信息 """
    try:
        cursor = conn.cursor()
        cursor.execute("UPDATE users SET age = ? WHERE name = ?", user)
        conn.commit()
    except sqlite3.Error as e:
        print(e)


def delete_user(conn, name):
    """ 删除用户 """
    try:
        cursor = conn.cursor()
        cursor.execute("DELETE FROM users WHERE name = ?", (name,))
        conn.commit()
    except sqlite3.Error as e:
        print(e)


def select_all_users(conn):
    """ 查询所有用户 """
    try:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM users")
        rows = cursor.fetchall()
        for row in rows:
            print(row)
    except sqlite3.Error as e:
        print(e)

def main():
    database = "traffic.db"

    # 创建数据库连接
    conn = create_connection(database)

    # 创建表
    if conn is not None:
        create_table(conn)

        # 插入数据
        insert_user(conn, ('Alice', 30))
        insert_user(conn, ('Bob', 25))

        # 更新数据
        update_user(conn, (35, 'Alice'))

        # 查询数据
        print("查询到的所有用户:")
        select_all_users(conn)

        # 删除数据
        delete_user(conn, 'Bob')

        # 再次查询数据
        print("\n删除后的用户数据:")
        select_all_users(conn)

        # 关闭数据库连接
        conn.close()
    else:
        print("Error! 无法创建数据库连接。")


if __name__ == '__main__':
    main()

"""
控制台输出结果：
查询到的所有用户:
(1, 'Alice', 35)
(2, 'Alice', 35)
(3, 'Bob', 25)

删除后的用户数据:
(1, 'Alice', 35)
(2, 'Alice', 35)
"""
