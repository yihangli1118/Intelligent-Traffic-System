# main_window.py
import sys
from PyQt5.QtWidgets import QApplication, QWidget
from views.stats import Ui_Form
from views.navigation_manager import NavigationManager
from views.vehicle_table_manager import VehicleTableManager
from views.violation_table import ViolationTableManager
from views.weather_time_display import WeatherTimeDisplayManager
from views.flow_table import FlowTableManager
from views.about_manager import AboutManager
from views.videoView import VideoView
import views.resource

class MainWindow(QWidget, Ui_Form):
    def __init__(self):
        super().__init__()
        self.setupUi(self)

        # 初始化导航管理器
        self.nav_manager = NavigationManager(self)

        # 初始化车辆表格管理器
        self.vehicle_table_manager = VehicleTableManager(self)

        # 初始化违规表格管理器
        self.violation_table_manager = ViolationTableManager(self)

        # 初始化时间和天气显示管理器
        self.weather_time_manager = WeatherTimeDisplayManager(self)

        # 初始化流量表格管理器
        self.flow_table_manager = FlowTableManager(self)

        # 初始化关于我们页面管理器
        self.about_manager = AboutManager(self)

        # 初始化视频播放
        self.video_view = VideoView(self)

        # 设置 left_content 布局
        self.setup_left_content_layout()

        # 设置 right_content 布局
        self.setup_right_content_layout()

        # 设置违规查询页面布局
        self.setup_violation_layout()

        # 设置流量查询页面布局
        self.setup_flow_layout()

        # 可以在这里添加其他初始化代码
        self.setWindowTitle("智能交通管理系统")

    # main.py (另一种方式)
    def setup_left_content_layout(self):
        """
        设置左侧内容区域布局
        """
        # 调用表格管理器设置布局
        self.vehicle_table_manager.setup_left_content_layout()

        # 单独设置表格最小高度为80像素
        self.vehicle_table_manager.set_table_min_height(150)

    def setup_right_content_layout(self):
        """
        设置右侧内容区域布局
        """
        # 调用时间和天气显示管理器设置布局
        self.weather_time_manager.setup_right_content_layout()

    def setup_violation_layout(self):
        """
        设置违规查询页面布局
        """
        # 调用违规表格管理器设置布局
        self.violation_table_manager.setup_violation_layout()

    def setup_flow_layout(self):
        """
        设置流量查询页面布局
        """
        # 调用流量表格管理器设置布局
        self.flow_table_manager.setup_flow_layout()

    def closeEvent(self, event):
        """
        窗口关闭事件，停止定时器
        """
        # 停止所有定时器
        self.weather_time_manager.stop_timers()
        event.accept()

# 移除了原来的 main() 函数和 if __name__ == "__main__": 部分
