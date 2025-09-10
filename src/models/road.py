# src/models/road.py
class Road:
    """
    道路实体类，只包含道路ID和名称
    """

    def __init__(self, road_id: str = "", road_name: str = ""):
        self.road_id = road_id
        self.road_name = road_name

    # Getter 方法
    def get_road_id(self) -> str:
        return self.road_id

    def get_road_name(self) -> str:
        return self.road_name

    # Setter 方法
    def set_road_id(self, road_id: str):
        self.road_id = road_id

    def set_road_name(self, road_name: str):
        self.road_name = road_name

    def __str__(self):
        return f"Road(id='{self.road_id}', name='{self.road_name}')"
