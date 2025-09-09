# file: src/views/main_window.py
import sys
from PyQt5.QtWidgets import QApplication, QWidget
from PyQt5.QtCore import Qt
from views.stats import Ui_Form
from views.navigation_manager import NavigationManager
from views.vehicle_table_manager import VehicleTableManager
from views.violation_table import ViolationTableManager
from views.weather_time_display import WeatherTimeDisplayManager
from views.flow_table import FlowTableManager
from views.about_manager import AboutManager
from views.videoView import VideoView
from utils.session_manager import SessionManager
import views.resource


class MainWindow(QWidget, Ui_Form):
    def __init__(self):
        super().__init__()
        self.setupUi(self)

        # 获取当前登录用户并显示在界面上
        self.session_manager = SessionManager()
        current_user = self.session_manager.get_current_user()
        if current_user:
            self.user_name.setText(current_user)

        # 设置窗口属性
        self.setWindowFlags(Qt.FramelessWindowHint)  # 无边框窗口
        self.setMinimumSize(1331, 831)  # 设置最小尺寸

        # 添加关闭回调属性
        self.close_callback = None

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

        # 连接顶部按钮功能
        self.setup_top_buttons()

        # 可以在这里添加其他初始化代码
        self.setWindowTitle("智能交通管理系统")

    def setup_top_buttons(self):
        """
        设置顶部按钮功能
        """
        # 连接关闭按钮 - 关闭主窗口并返回登录界面
        self.closeAppBtn.clicked.connect(self.close)  # 这里保持不变

        # 连接最大化/恢复按钮
        self.maximizeRestoreAppBtn.clicked.connect(self.toggle_maximize)

        # 连接最小化按钮
        self.minimizeAppBtn.clicked.connect(self.showMinimized)

    def toggle_maximize(self):
        """
        切换窗口最大化/恢复状态
        """
        if self.isMaximized():
            self.showNormal()
        else:
            self.showMaximized()

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
        窗口关闭事件，停止定时器并返回登录界面
        """
        # 停止所有定时器
        self.weather_time_manager.stop_timers()

        # 调用关闭回调（如果存在）
        if self.close_callback:
            self.close_callback()

        event.accept()