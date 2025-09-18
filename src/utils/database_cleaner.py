# src/utils/database_cleaner.py
import sqlite3
import os
from typing import Optional

class DatabaseCleaner:
    """
    数据库清理工具类，用于清除数据库中的所有记录
    """

    def __init__(self, db_path: str = "utils/traffic.db"):
        """
        初始化数据库清理器
        :param db_path: 数据库文件路径
        """
        # 获取项目根目录
        current_dir = os.path.dirname(os.path.abspath(__file__))
        project_root = os.path.dirname(os.path.dirname(current_dir))
        self.db_path = os.path.join(project_root, "src", db_path)
        print(f"DatabaseCleaner - 数据库路径: {self.db_path}")

    def clear_database(self) -> bool:
        """
        清除数据库中的所有记录，包括重置自增序列
        :return: 是否清除成功
        """
        try:
            print(f"开始清除数据库，检查文件是否存在: {os.path.exists(self.db_path)}")
            if not os.path.exists(self.db_path):
                print(f"数据库文件不存在: {self.db_path}")
                return True

            print("连接到数据库...")
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()

            # 开始事务
            cursor.execute('BEGIN TRANSACTION')
            print("开始事务")

            # 显示清除前的数据
            print("清除前的表数据:")
            tables = ['vehicles', 'persons', 'bicycles', 'motorcycles', 'trafficFlows', 'roads']
            for table in tables:
                try:
                    cursor.execute(f'SELECT COUNT(*) FROM {table}')
                    count = cursor.fetchone()[0]
                    print(f"  {table}: {count} 条记录")
                except sqlite3.Error as e:
                    print(f"  {table}: 查询失败 - {e}")

            # 清除所有业务表中的数据
            for table in tables:
                try:
                    cursor.execute(f'DELETE FROM {table}')
                    print(f"已清除表 {table} 中的 {cursor.rowcount} 条记录")
                except sqlite3.Error as e:
                    print(f"清除表 {table} 时出错: {e}")
                    conn.rollback()
                    conn.close()
                    return False

            # 重置 sqlite_sequence 表中的自增计数器
            try:
                cursor.execute("DELETE FROM sqlite_sequence WHERE name IN ('vehicles', 'persons', 'bicycles', 'motorcycles', 'trafficFlows', 'roads')")
                print("已重置 sqlite_sequence 表中的自增计数器")
            except sqlite3.Error as e:
                print(f"重置 sqlite_sequence 表时出错: {e}")
                # 不过这个不是致命错误，继续执行

            # 提交事务
            conn.commit()
            print("事务提交成功")

            # 验证清除后的数据
            print("清除后的表数据:")
            for table in tables:
                try:
                    cursor.execute(f'SELECT COUNT(*) FROM {table}')
                    count = cursor.fetchone()[0]
                    print(f"  {table}: {count} 条记录")
                except sqlite3.Error as e:
                    print(f"  {table}: 查询失败 - {e}")

            conn.close()
            print("数据库清理完成")
            return True

        except Exception as e:
            print(f"清理数据库时出错: {e}")
            import traceback
            traceback.print_exc()
            return False

    def check_database_exists(self) -> bool:
        """
        检查数据库文件是否存在
        :return: 数据库文件是否存在
        """
        exists = os.path.exists(self.db_path)
        print(f"数据库文件存在: {exists}, 路径: {self.db_path}")
        return exists

if __name__ == "__main__":
    # 创建 DatabaseCleaner 实例
    cleaner = DatabaseCleaner()

    # 检查数据库是否存在
    if cleaner.check_database_exists():
        # 执行数据库清理
        success = cleaner.clear_database()
        if success:
            print("✅ 数据库清理成功完成")
        else:
            print("❌ 数据库清理过程中出现错误")
    else:
        print("⚠️ 数据库文件不存在，无需清理")
