# flow.py# src/models/flow.py
from datetime import datetime
from typing import List, Optional

class Flow:
    """
    流量实体类，用于记录交通流量信息
    """

    def __init__(self, vehicle_count: int = 0, entry_count: int = 0,
                 departure_count: int = 0, stat_time: Optional[datetime] = None,
                 end_time: Optional[datetime] = None, road_id: str = ""):
        self.vehicle_count = vehicle_count
        self.entry_count = entry_count
        self.departure_count = departure_count
        self.stat_time = stat_time
        self.end_time = end_time
        self.road_id = road_id

    # Getter 方法
    def get_vehicle_count(self) -> int:
        return self.vehicle_count

    def get_entry_count(self) -> int:
        return self.entry_count

    def get_departure_count(self) -> int:
        return self.departure_count

    def get_stat_time(self) -> Optional[datetime]:
        return self.stat_time

    def get_end_time(self) -> Optional[datetime]:
        return self.end_time

    def get_road_id(self) -> str:
        return self.road_id

    # Setter 方法
    def set_vehicle_count(self, vehicle_count: int):
        self.vehicle_count = vehicle_count

    def set_entry_count(self, entry_count: int):
        self.entry_count = entry_count

    def set_departure_count(self, departure_count: int):
        self.departure_count = departure_count

    def set_stat_time(self, stat_time: datetime):
        self.stat_time = stat_time

    def set_end_time(self, end_time: datetime):
        self.end_time = end_time

    def set_road_id(self, road_id: str):
        self.road_id = road_id

    @staticmethod
    def get_traffic_flow_by_time(road_id: str, time: datetime) -> Optional['Flow']:
        """
        根据时间和路段ID获取交通流量信息
        注意：此方法需要数据库支持，这里仅提供接口定义
        :param road_id: 路段ID
        :param time: 查询时间
        :return: 流量信息对象
        """
        # 这里应该实现从数据库查询流量信息的逻辑
        # 由于没有数据库实现，暂时返回None
        # 实际实现时应该查询数据库并返回对应的Flow对象
        pass

    def __str__(self):
        return (f"Flow(road_id='{self.road_id}', vehicle_count={self.vehicle_count}, "
                f"entry_count={self.entry_count}, departure_count={self.departure_count}, "
                f"stat_time={self.stat_time}, end_time={self.end_time})")
