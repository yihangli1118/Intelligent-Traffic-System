# user.py
import sqlite3
import os
from typing import List, Optional

# 获取数据库路径，相对于当前文件位置
DB_PATH = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'utils', 'traffic.db')


class User:
    """
    用户实体类，对应数据库中的 users 表
    """

    def __init__(self, id: Optional[int] = None, username: str = "", password: str = ""):
        self.id = id
        self.username = username
        self.password = password

    def __str__(self):
        return f"User(id={self.id}, username='{self.username}')"

    def __repr__(self):
        return self.__str__()


class UserManager:
    """
    用户管理类，提供对用户数据的增删改查操作
    """

    @staticmethod
    def get_connection():
        """获取数据库连接"""
        conn = sqlite3.connect(DB_PATH)
        return conn

    @staticmethod
    def create_table():
        """创建用户表"""
        try:
            conn = UserManager.get_connection()
            cursor = conn.cursor()
            cursor.execute('''CREATE TABLE IF NOT EXISTS users
                            (id INTEGER PRIMARY KEY, username TEXT UNIQUE, password TEXT)''')
            conn.commit()
            conn.close()
        except sqlite3.Error as e:
            print(f"创建表时出错: {e}")

    @staticmethod
    def insert_user(user: User) -> bool:
        """插入新用户"""
        try:
            conn = UserManager.get_connection()
            cursor = conn.cursor()
            cursor.execute("INSERT INTO users (username, password) VALUES (?, ?)",
                          (user.username, user.password))
            conn.commit()
            conn.close()
            return True
        except sqlite3.Error as e:
            print(f"插入用户时出错: {e}")
            return False

    @staticmethod
    def update_user(user: User) -> bool:
        """更新用户信息"""
        try:
            conn = UserManager.get_connection()
            cursor = conn.cursor()
            cursor.execute("UPDATE users SET username = ?, password = ? WHERE id = ?",
                          (user.username, user.password, user.id))
            conn.commit()
            conn.close()
            return True
        except sqlite3.Error as e:
            print(f"更新用户时出错: {e}")
            return False

    @staticmethod
    def delete_user(user_id: int) -> bool:
        """根据ID删除用户"""
        try:
            conn = UserManager.get_connection()
            cursor = conn.cursor()
            cursor.execute("DELETE FROM users WHERE id = ?", (user_id,))
            conn.commit()
            conn.close()
            return True
        except sqlite3.Error as e:
            print(f"删除用户时出错: {e}")
            return False

    @staticmethod
    def get_user_by_id(user_id: int) -> Optional[User]:
        """根据ID查询用户"""
        try:
            conn = UserManager.get_connection()
            cursor = conn.cursor()
            cursor.execute("SELECT id, username, password FROM users WHERE id = ?", (user_id,))
            row = cursor.fetchone()
            conn.close()

            if row:
                return User(row[0], row[1], row[2])
            return None
        except sqlite3.Error as e:
            print(f"查询用户时出错: {e}")
            return None

    @staticmethod
    def get_user_by_username(username: str) -> Optional[User]:
        """根据用户名查询用户"""
        try:
            conn = UserManager.get_connection()
            cursor = conn.cursor()
            cursor.execute("SELECT id, username, password FROM users WHERE username = ?", (username,))
            row = cursor.fetchone()
            conn.close()

            if row:
                return User(row[0], row[1], row[2])
            return None
        except sqlite3.Error as e:
            print(f"根据用户名查询用户时出错: {e}")
            return None

    @staticmethod
    def get_all_users() -> List[User]:
        """查询所有用户"""
        try:
            conn = UserManager.get_connection()
            cursor = conn.cursor()
            cursor.execute("SELECT id, username, password FROM users")
            rows = cursor.fetchall()
            conn.close()

            users = []
            for row in rows:
                users.append(User(row[0], row[1], row[2]))
            return users
        except sqlite3.Error as e:
            print(f"查询所有用户时出错: {e}")
            return []

    @staticmethod
    def authenticate_user(username: str, password: str) -> Optional[User]:
        """验证用户登录"""
        try:
            conn = UserManager.get_connection()
            cursor = conn.cursor()
            cursor.execute("SELECT id, username, password FROM users WHERE username = ? AND password = ?",
                          (username, password))
            row = cursor.fetchone()
            conn.close()

            if row:
                return User(row[0], row[1], row[2])
            return None
        except sqlite3.Error as e:
            print(f"验证用户时出错: {e}")
            return None
