# src/models/vehicle.py
from typing import Dict, Any
from datetime import datetime
from typing import Optional
from .object import Object

class Vehicle(Object):
    """
    车辆实体类，继承自Object类
    """

    def __init__(self, vehicle_id: str = "", vehicle_type: str = "",
                 plate_number: str = "", plate_color: str = "",
                 body_color: str = "", speed: float = 60.0,
                 entry_time: Optional[datetime] = None,
                 departure_time: Optional[datetime] = None,
                 driving_direction: str = "",
                 road_id: str = "",
                 photo: Optional[bytes] = None):
        # 初始化父类Object的属性
        super().__init__(entry_time, departure_time, driving_direction, road_id, photo)

        # Vehicle特有属性
        self.vehicle_id = vehicle_id
        self.vehicle_type = vehicle_type  # car, bus, truck
        self.plate_number = plate_number
        self.plate_color = plate_color
        self.body_color = body_color
        self.speed = speed  # 默认60km/h

    # Getter 方法
    def get_vehicle_id(self) -> str:
        return self.vehicle_id

    def get_vehicle_type(self) -> str:
        return self.vehicle_type

    def get_plate_number(self) -> str:
        return self.plate_number

    def get_plate_color(self) -> str:
        return self.plate_color

    def get_body_color(self) -> str:
        return self.body_color

    def get_speed(self) -> float:
        return self.speed

    # Setter 方法
    def set_vehicle_id(self, vehicle_id: str):
        self.vehicle_id = vehicle_id

    def set_vehicle_type(self, vehicle_type: str):
        self.vehicle_type = vehicle_type

    def set_plate_number(self, plate_number: str):
        self.plate_number = plate_number

    def set_plate_color(self, plate_color: str):
        self.plate_color = plate_color

    def set_body_color(self, body_color: str):
        self.body_color = body_color

    def set_speed(self, speed: float):
        self.speed = speed

    def update_vehicle_info(self, vehicle_id: str, info: Dict[str, Any]) -> bool:
        """
        更新车辆信息
        :param vehicle_id: 车辆ID
        :param info: 包含车辆信息的字典
        :return: 更新是否成功
        """
        if self.vehicle_id != vehicle_id:
            return False

        if "vehicle_type" in info:
            self.vehicle_type = info["vehicle_type"]
        if "plate_number" in info:
            self.plate_number = info["plate_number"]
        if "plate_color" in info:
            self.plate_color = info["plate_color"]
        if "body_color" in info:
            self.body_color = info["body_color"]
        if "speed" in info:
            self.speed = info["speed"]

        return True

    def __str__(self):
        base_str = super().__str__()
        return (f"Vehicle({base_str}, id='{self.vehicle_id}', type='{self.vehicle_type}', "
                f"plate='{self.plate_number}', speed={self.speed}km/h)")
