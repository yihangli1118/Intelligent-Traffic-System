# src/models/motorcycle.py
from datetime import datetime
from typing import Optional
from .object import Object

class Motorcycle(Object):
    """
    摩托车实体类，继承自Object类
    """

    def __init__(self, motorcycle_id: str = "",
                 entry_time: Optional[datetime] = None,
                 departure_time: Optional[datetime] = None,
                 driving_direction: str = "",
                 road_id: str = "",
                 photo: Optional[bytes] = None):
        # 初始化父类Object的属性
        super().__init__(entry_time, departure_time, driving_direction, road_id, photo)

        # Motorcycle特有属性
        self.motorcycle_id = motorcycle_id

    # Getter 方法
    def get_motorcycle_id(self) -> str:
        return self.motorcycle_id

    # Setter 方法
    def set_motorcycle_id(self, motorcycle_id: str):
        self.motorcycle_id = motorcycle_id

    def __str__(self):
        base_str = super().__str__()
        return f"Motorcycle({base_str}, id='{self.motorcycle_id}')"
