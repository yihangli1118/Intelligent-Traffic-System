# src/models/bicycle.py
from datetime import datetime
from typing import Optional

class Bicycle:
    """
    自行车实体类，独立类不继承自Object类
    """

    def __init__(self, bicycle_id: str = "",
                 entry_time: Optional[datetime] = None,
                 departure_time: Optional[datetime] = None,
                 driving_direction: str = "",
                 road_id: str = "",
                 photo: Optional[bytes] = None):
        # Bicycle特有属性
        self.bicycle_id = bicycle_id

        # 原Object类的属性
        self.entry_time = entry_time
        self.departure_time = departure_time
        self.driving_direction = driving_direction  # 上行 or 下行
        self.road_id = road_id
        self.photo = photo

    # Getter 方法
    def get_bicycle_id(self) -> str:
        return self.bicycle_id

    def get_entry_time(self) -> Optional[datetime]:
        return self.entry_time

    def get_departure_time(self) -> Optional[datetime]:
        return self.departure_time

    def get_driving_direction(self) -> str:
        return self.driving_direction

    def get_road_id(self) -> str:
        return self.road_id

    def get_photo(self) -> Optional[bytes]:
        return self.photo

    # Setter 方法
    def set_bicycle_id(self, bicycle_id: str):
        self.bicycle_id = bicycle_id

    def set_entry_time(self, entry_time: datetime):
        self.entry_time = entry_time

    def set_departure_time(self, departure_time: datetime):
        self.departure_time = departure_time

    def set_driving_direction(self, driving_direction: str):
        self.driving_direction = driving_direction

    def set_road_id(self, road_id: str):
        self.road_id = road_id

    def set_photo(self, photo: bytes):
        self.photo = photo

    def __str__(self):
        return (f"Bicycle(entry_time={self.entry_time}, departure_time={self.departure_time}, "
                f"driving_direction='{self.driving_direction}', road_id='{self.road_id}', "
                f"id='{self.bicycle_id}')")
