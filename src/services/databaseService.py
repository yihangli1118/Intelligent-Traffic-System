# src/services/databaseService.py
import sqlite3
from datetime import datetime
from typing import Optional
import cv2
import numpy as np
import os
import time
import random

from models.vehicle import Vehicle
from models.person import Person
from models.bicycle import Bicycle
from models.motorcycle import Motorcycle
from models.road import Road
from models.flow import Flow


class DatabaseService:
    """
    数据库服务类，用于将检测到的交通对象信息存入数据库
    """

    def __init__(self, db_path: str = "utils/traffic.db"):
        """
        初始化数据库服务
        :param db_path: 数据库文件路径
        """
        self.db_path = db_path
        print(f"数据库路径: {os.path.abspath(self.db_path)}")  # 添加这行来查看实际路径
        self.init_database()

    def _execute_with_retry(self, func, max_retries=3):
        """
        带重试机制的数据库执行函数
        :param func: 要执行的函数
        :param max_retries: 最大重试次数
        :return: 函数执行结果
        """
        for attempt in range(max_retries):
            try:
                return func()
            except sqlite3.OperationalError as e:
                if "database is locked" in str(e) and attempt < max_retries - 1:
                    # 等待随机时间后重试
                    wait_time = 0.1 + random.uniform(0, 0.2)
                    print(f"数据库被锁定，{wait_time:.2f}秒后重试 (尝试 {attempt + 1}/{max_retries})")
                    time.sleep(wait_time)
                else:
                    raise e
            except Exception as e:
                raise e

    def init_database(self):
        """
        初始化数据库表结构
        """
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        # 创建roads表
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS roads (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                roadId TEXT UNIQUE,
                roadName TEXT
            )
        ''')

        # 创建vehicles表
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS vehicles (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                vehicleId TEXT,
                vehicleType TEXT,
                plateNumber TEXT,
                plateColor TEXT,
                bodyColor TEXT,
                speed REAL,
                entryTime TIMESTAMP,
                departureTime TIMESTAMP,
                drivingDirection TEXT,
                roadId TEXT,
                photo BLOB
            )
        ''')

        # 创建persons表
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS persons (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                personId TEXT,
                entryTime TIMESTAMP,
                departureTime TIMESTAMP,
                drivingDirection TEXT,
                roadId TEXT,
                photo BLOB
            )
        ''')

        # 创建bicycles表
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS bicycles (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                bicycleId TEXT,
                entryTime TIMESTAMP,
                departureTime TIMESTAMP,
                drivingDirection TEXT,
                roadId TEXT,
                photo BLOB
            )
        ''')

        # 创建motorcycles表
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS motorcycles (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                motorcycleId TEXT,
                entryTime TIMESTAMP,
                departureTime TIMESTAMP,
                drivingDirection TEXT,
                roadId TEXT,
                photo BLOB
            )
        ''')

        # 创建trafficFlows表
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS trafficFlows (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                roadId TEXT,
                vehicleCount INTEGER,
                entryCount INTEGER,
                departureCount INTEGER,
                startTime TIMESTAMP,
                endTime TIMESTAMP
            )
        ''')

        # 添加检查表是否创建成功
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
        tables = cursor.fetchall()
        print("数据库中的表:", tables)

        conn.commit()
        conn.close()

    def save_road(self, road: Road) -> bool:
        """
        保存道路信息到数据库
        :param road: Road对象
        :return: 是否保存成功
        """

        def _save_road_impl():
            conn = None
            try:
                conn = sqlite3.connect(self.db_path)
                cursor = conn.cursor()

                cursor.execute('''
                                INSERT OR REPLACE INTO roads (roadId, roadName)
                                VALUES (?, ?)
                            ''', (road.get_road_id(), road.get_road_name()))

                conn.commit()
                conn.close()
                return True
            except Exception as e:
                print(f"保存道路信息时出错: {e}")
                return False
            finally:
                if conn:
                    conn.close()

        return self._execute_with_retry(_save_road_impl)


    def save_vehicle(self, vehicle: Vehicle) -> bool:
        """
        保存车辆信息到数据库
        :param vehicle: Vehicle对象
        :return: 是否保存成功
        """

        def _save_vehicle_impl():
            conn = None
            try:
                print(f"尝试保存车辆: {vehicle.get_vehicle_id()}")  # 添加调试信息
                conn = sqlite3.connect(self.db_path)
                cursor = conn.cursor()

                cursor.execute('''
                            INSERT INTO vehicles 
                            (vehicleId, vehicleType, plateNumber, plateColor, bodyColor, speed, 
                             entryTime, departureTime, drivingDirection, roadId, photo)
                            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                        ''', (
                    vehicle.get_vehicle_id(),
                    vehicle.get_vehicle_type(),
                    vehicle.get_plate_number(),
                    vehicle.get_plate_color(),
                    vehicle.get_body_color(),
                    vehicle.get_speed(),
                    vehicle.get_entry_time(),
                    vehicle.get_departure_time(),
                    vehicle.get_driving_direction(),
                    vehicle.get_road_id(),
                    vehicle.get_photo()
                ))

                print(f"SQL执行结果: {cursor.rowcount} 行受影响")  # 查看影响行数
                conn.commit()
                conn.close()
                print(f"车辆 {vehicle.get_vehicle_id()} 保存成功")
                return True
            except Exception as e:
                print(f"保存车辆信息时出错: {e}")
                import traceback
                traceback.print_exc()  # 打印详细错误信息
                return False
            finally:

                if conn:
                    conn.close()

        return self._execute_with_retry(_save_vehicle_impl)

    def save_person(self, person: Person) -> bool:
        """
        保存人员信息到数据库
        :param person: Person对象
        :return: 是否保存成功
        """

        def _save_person_impl():
            conn = None
            try:
                conn = sqlite3.connect(self.db_path)
                cursor = conn.cursor()

                cursor.execute('''
                           INSERT INTO persons 
                           (personId, entryTime, departureTime, drivingDirection, roadId, photo)
                           VALUES (?, ?, ?, ?, ?, ?)
                       ''', (
                    person.get_person_id(),
                    person.get_entry_time(),
                    person.get_departure_time(),
                    person.get_driving_direction(),
                    person.get_road_id(),
                    person.get_photo()
                ))

                conn.commit()
                conn.close()
                return True
            except Exception as e:
                print(f"保存人员信息时出错: {e}")
                return False
            finally:
                if conn:
                    conn.close()

        return self._execute_with_retry(_save_person_impl)


    def save_bicycle(self, bicycle: Bicycle) -> bool:
        """
        保存自行车信息到数据库
        :param bicycle: Bicycle对象
        :return: 是否保存成功
        """

        def _save_bicycle_impl():
            conn = None
            try:
                conn = sqlite3.connect(self.db_path)
                cursor = conn.cursor()

                cursor.execute('''
                                        INSERT INTO bicycles 
                                        (bicycleId, entryTime, departureTime, drivingDirection, roadId, photo)
                                        VALUES (?, ?, ?, ?, ?, ?)
                                    ''', (
                    bicycle.get_bicycle_id(),
                    bicycle.get_entry_time(),
                    bicycle.get_departure_time(),
                    bicycle.get_driving_direction(),
                    bicycle.get_road_id(),
                    bicycle.get_photo()
                ))

                conn.commit()
                conn.close()
                return True
            except Exception as e:
                print(f"保存自行车信息时出错: {e}")
                return False
            finally:
                if conn:
                    conn.close()

        return self._execute_with_retry(_save_bicycle_impl)



    def save_motorcycle(self, motorcycle: Motorcycle) -> bool:
        """
        保存摩托车信息到数据库
        :param motorcycle: Motorcycle对象
        :return: 是否保存成功
        """

        def _save_motorcycle_impl():
            conn = None
            try:
                conn = sqlite3.connect(self.db_path)
                cursor = conn.cursor()

                cursor.execute('''
                    INSERT INTO motorcycles 
                    (motorcycleId, entryTime, departureTime, drivingDirection, roadId, photo)
                    VALUES (?, ?, ?, ?, ?, ?)
                ''', (
                    motorcycle.get_motorcycle_id(),
                    motorcycle.get_entry_time(),
                    motorcycle.get_departure_time(),
                    motorcycle.get_driving_direction(),
                    motorcycle.get_road_id(),
                    motorcycle.get_photo()
                ))

                conn.commit()
                conn.close()
                return True
            except Exception as e:
                print(f"保存摩托车信息时出错: {e}")
                return False
            finally:
                if conn:
                    conn.close()

        return self._execute_with_retry(_save_motorcycle_impl)


    def save_traffic_flow(self, flow: Flow) -> bool:
        """
        保存交通流量信息到数据库
        :param flow: Flow对象
        :return: 是否保存成功
        """

        def _save_traffic_flow_impl():
            conn=None
            try:
                conn = sqlite3.connect(self.db_path)
                cursor = conn.cursor()

                cursor.execute('''
                    INSERT INTO trafficFlows 
                    (roadId, vehicleCount, entryCount, departureCount, startTime, endTime)
                    VALUES (?, ?, ?, ?, ?, ?)
                ''', (
                    flow.get_road_id(),
                    flow.get_vehicle_count(),
                    flow.get_entry_count(),
                    flow.get_departure_count(),
                    flow.get_stat_time(),
                    flow.get_end_time()
                ))

                conn.commit()
                conn.close()
                return True
            except Exception as e:
                print(f"保存交通流量信息时出错: {e}")
                return False
            finally:
                if conn:
                    conn.close()

        return self._execute_with_retry(_save_traffic_flow_impl)


    def update_vehicle_departure(self, vehicle_id: str, departure_time: datetime) -> bool:
        """
        更新车辆离开时间
        :param vehicle_id: 车辆ID
        :param departure_time: 离开时间
        :return: 是否更新成功
        """
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()

            cursor.execute('''
                UPDATE vehicles 
                SET departureTime = ? 
                WHERE vehicleId = ?
            ''', (departure_time, vehicle_id))

            conn.commit()
            conn.close()
            return True
        except Exception as e:
            print(f"更新车辆离开时间时出错: {e}")
            return False

    def update_person_departure(self, person_id: str, departure_time: datetime) -> bool:
        """
        更新人员离开时间
        :param person_id: 人员ID
        :param departure_time: 离开时间
        :return: 是否更新成功
        """
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()

            cursor.execute('''
                UPDATE persons 
                SET departureTime = ? 
                WHERE personId = ?
            ''', (departure_time, person_id))

            conn.commit()
            conn.close()
            return True
        except Exception as e:
            print(f"更新人员离开时间时出错: {e}")
            return False

    def update_bicycle_departure(self, bicycle_id: str, departure_time: datetime) -> bool:
        """
        更新自行车离开时间
        :param bicycle_id: 自行车ID
        :param departure_time: 离开时间
        :return: 是否更新成功
        """
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()

            cursor.execute('''
                UPDATE bicycles 
                SET departureTime = ? 
                WHERE bicycleId = ?
            ''', (departure_time, bicycle_id))

            conn.commit()
            conn.close()
            return True
        except Exception as e:
            print(f"更新自行车离开时间时出错: {e}")
            return False

    def update_motorcycle_departure(self, motorcycle_id: str, departure_time: datetime) -> bool:
        """
        更新摩托车离开时间
        :param motorcycle_id: 摩托车ID
        :param departure_time: 离开时间
        :return: 是否更新成功
        """
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()

            cursor.execute('''
                UPDATE motorcycles 
                SET departureTime = ? 
                WHERE motorcycleId = ?
            ''', (departure_time, motorcycle_id))

            conn.commit()
            conn.close()
            return True
        except Exception as e:
            print(f"更新摩托车离开时间时出错: {e}")
            return False

    def get_latest_traffic_flows(self, limit=10):
        """
        获取最新的流量记录
        :param limit: 获取记录的数量限制
        :return: 流量记录列表
        """
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()

            # 查询最新的流量记录，按时间倒序排列并限制数量
            query = """
            SELECT 
                tf.roadId,
                r.roadName,
                tf.startTime,
                tf.endTime,
                tf.vehicleCount,
                tf.entryCount,
                tf.departureCount
            FROM trafficFlows tf
            LEFT JOIN roads r ON tf.roadId = r.roadId
            ORDER BY tf.startTime DESC
            LIMIT ?
            """

            cursor.execute(query, (limit,))
            rows = cursor.fetchall()

            # 将结果转换为字典列表
            flows = []
            for row in rows:
                flow = {
                    'road_id': row[0] if row[0] else '001',
                    'road_name': row[1] if row[1] else '新街口',
                    'start_time': row[2],
                    'end_time': row[3],
                    'vehicle_count': row[4] if row[4] else 0,
                    'entry_count': row[5] if row[5] else 0,
                    'departure_count': row[6] if row[6] else 0
                }
                flows.append(flow)

            # 按时间正序排列（最早的在前）
            flows.reverse()

            conn.close()
            return flows

        except Exception as e:
            print(f"获取流量记录时出错: {e}")
            return []
