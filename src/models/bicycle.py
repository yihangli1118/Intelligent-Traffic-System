# src/models/bicycle.py
from datetime import datetime
from typing import Optional
from .object import Object

class Bicycle(Object):
    """
    自行车实体类，继承自Object类
    """

    def __init__(self, bicycle_id: str = "",
                 entry_time: Optional[datetime] = None,
                 departure_time: Optional[datetime] = None,
                 driving_direction: str = "",
                 road_id: str = "",
                 photo: Optional[bytes] = None):
        # 初始化父类Object的属性
        super().__init__(entry_time, departure_time, driving_direction, road_id, photo)

        # Bicycle特有属性
        self.bicycle_id = bicycle_id

    # Getter 方法
    def get_bicycle_id(self) -> str:
        return self.bicycle_id

    # Setter 方法
    def set_bicycle_id(self, bicycle_id: str):
        self.bicycle_id = bicycle_id

    def __str__(self):
        base_str = super().__str__()
        return f"Bicycle({base_str}, id='{self.bicycle_id}')"
