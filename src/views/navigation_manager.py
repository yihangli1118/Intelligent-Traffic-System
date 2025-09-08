# navigation_manager.py
from PyQt5.QtWidgets import QWidget
from views.stats import Ui_Form


class NavigationManager:
    """
    管理界面中所有导航按钮与对应页面的关联
    """

    def __init__(self, ui: Ui_Form):
        self.ui = ui
        self.setup_connections()
        self.setup_initial_state()

    def setup_connections(self):
        """
        连接所有导航按钮的点击信号到对应的页面切换槽函数
        """
        self.ui.icon.clicked.connect(self.switch_to_home_page)
        # 连接主页面切换按钮
        self.ui.monitor.clicked.connect(self.switch_to_monitor_page)
        self.ui.infoQuery.clicked.connect(self.switch_to_info_query_page)
        self.ui.settingUp.clicked.connect(self.switch_to_settings_page)

        # 连接子页面切换按钮
        self.ui.violations.clicked.connect(self.switch_to_violations_page)
        self.ui.flow.clicked.connect(self.switch_to_flow_page)

    def setup_initial_state(self):
        """
        设置初始状态：不选择任何按钮
        """
        # 清除所有按钮的选中状态
        self.ui.monitor.setChecked(False)
        self.ui.infoQuery.setChecked(False)
        self.ui.settingUp.setChecked(False)
        self.ui.violations.setChecked(False)
        self.ui.flow.setChecked(False)

        # 默认显示第0页（主页）
        self.ui.stackedWidget.setCurrentIndex(0)
        # 子页面默认显示0号页面
        self.ui.stackedWidget_2.setCurrentIndex(0)

    # 主页面切换方法
    def switch_to_home_page(self):
        """
        切换到主页页面 (stackedWidget索引0)
        """
        self.ui.stackedWidget.setCurrentIndex(0)
        # 当切换到主页时，重置所有按钮状态
        self.reset_all_buttons()

    def switch_to_monitor_page(self):
        """
        切换到实时监控页面 (stackedWidget索引1)
        """
        # 取消其他主页面按钮的选中状态
        self.ui.infoQuery.setChecked(False)
        self.ui.settingUp.setChecked(False)

        # 设置当前按钮为选中状态
        self.ui.monitor.setChecked(True)

        self.ui.stackedWidget.setCurrentIndex(1)
        # 当切换到监控页面时，重置信息查询的子按钮状态
        self.reset_info_query_sub_buttons()

    def switch_to_info_query_page(self):
        """
        切换到信息查询页面 (stackedWidget索引2)
        并确保子按钮都处于未点击状态
        """
        # 取消其他主页面按钮的选中状态
        self.ui.monitor.setChecked(False)
        self.ui.settingUp.setChecked(False)

        # 设置当前按钮为选中状态
        self.ui.infoQuery.setChecked(True)

        self.ui.stackedWidget.setCurrentIndex(2)
        self.ui.stackedWidget_2.setCurrentIndex(0)
        # 重置子按钮状态并确保样式正确
        self.reset_info_query_sub_buttons()

    def switch_to_settings_page(self):
        """
        切换到设置页面 (stackedWidget索引3)
        """
        # 取消其他主页面按钮的选中状态
        self.ui.monitor.setChecked(False)
        self.ui.infoQuery.setChecked(False)

        # 设置当前按钮为选中状态
        self.ui.settingUp.setChecked(True)

        self.ui.stackedWidget.setCurrentIndex(3)
        # 当切换到设置页面时，重置信息查询的子按钮状态
        self.reset_info_query_sub_buttons()

    # 子页面切换方法
    def switch_to_violations_page(self):
        """
        切换到违规查询页面 (stackedWidget_2索引0)
        """
        # 取消flow按钮的选中状态
        self.ui.flow.setChecked(False)

        # 设置当前按钮为选中状态
        self.ui.violations.setChecked(True)

        self.ui.stackedWidget_2.setCurrentIndex(1)

    def switch_to_flow_page(self):
        """
        切换到流量查询页面 (stackedWidget_2索引1)
        """
        # 取消violations按钮的选中状态
        self.ui.violations.setChecked(False)

        # 设置当前按钮为选中状态
        self.ui.flow.setChecked(True)

        self.ui.stackedWidget_2.setCurrentIndex(2)

    def reset_info_query_sub_buttons(self):
        """
        重置信息查询子页面按钮状态为未选中
        """
        self.ui.violations.setChecked(False)
        self.ui.flow.setChecked(False)

    def reset_all_buttons(self):
        """
        重置所有导航按钮状态为未选中
        """
        self.ui.monitor.setChecked(False)
        self.ui.infoQuery.setChecked(False)
        self.ui.settingUp.setChecked(False)
        self.ui.violations.setChecked(False)
        self.ui.flow.setChecked(False)
