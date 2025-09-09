# src/models/person.py
from datetime import datetime
from typing import Optional
from .object import Object

class Person(Object):
    """
    人员实体类，继承自Object类
    """

    def __init__(self, person_id: str = "",
                 entry_time: Optional[datetime] = None,
                 departure_time: Optional[datetime] = None,
                 driving_direction: str = "",
                 road_id: str = "",
                 photo: Optional[bytes] = None):
        # 初始化父类Object的属性
        super().__init__(entry_time, departure_time, driving_direction, road_id, photo)

        # Person特有属性
        self.person_id = person_id

    # Getter 方法
    def get_person_id(self) -> str:
        return self.person_id

    # Setter 方法
    def set_person_id(self, person_id: str):
        self.person_id = person_id

    def __str__(self):
        base_str = super().__str__()
        return f"Person({base_str}, id='{self.person_id}')"
