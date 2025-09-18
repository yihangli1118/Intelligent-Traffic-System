# file: src/views/main_window.py
import sys
from PyQt5.QtWidgets import QApplication, QWidget
from PyQt5.QtCore import Qt, QTimer, QCoreApplication
from views.stats import Ui_Form
from views.navigation_manager import NavigationManager
from views.vehicle_table_manager import VehicleTableManager
from views.violation_table import ViolationTableManager
from views.weather_time_display import WeatherTimeDisplayManager
from views.flow_table import FlowTableManager
from views.about_manager import AboutManager
from views.videoView import VideoView
from utils.session_manager import SessionManager
from views.car_violation_view import CarViolationView
from views.person_violation_view import PersonViolationView
import views.resource
import csv
from PyQt5.QtWidgets import QFileDialog, QMessageBox

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

        # 初始化车辆违规检测视频播放视图
        self.car_violation_view = CarViolationView(self)

        # 初始化行人违规检测视频播放视图
        self.person_violation_view = PersonViolationView(self)

        # 初始化视频播放
        self.video_view = VideoView(self)
        from controllers.videoController import VideoController
        self.video_controller = VideoController(self)
        self.video_view.set_controller(self.video_controller)

        # 添加交通流量统计更新定时器
        self.traffic_stats_timer = QTimer()
        self.traffic_stats_timer.timeout.connect(self.update_traffic_stats)
        self.traffic_stats_timer.start(5000)  # 每5秒更新一次

        # 添加车辆信息更新定时器
        self.vehicle_update_timer = QTimer()
        self.vehicle_update_timer.timeout.connect(self.update_vehicle_info)
        self.vehicle_update_timer.start(1000)  # 每秒更新一次

        # 添加流量信息显示定时器
        self.flow_display_timer = QTimer()
        self.flow_display_timer.timeout.connect(self.update_traffic_flow_display)
        self.flow_display_timer.start(5000)  # 每5秒更新一次

        # 禁用 plainTextEdit 自身的滚动条
        self.plainTextEdit.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.plainTextEdit.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.plainTextEdit_7.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.plainTextEdit_7.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)

        # 设置流量信息显示区域的字体大小和颜色
        # font = self.plainTextEdit.font()
        # font.setPointSize(12)  # 设置字体大小
        # self.plainTextEdit.setFont(font)
        # self.plainTextEdit.setStyleSheet("""
        #     QPlainTextEdit {
        #         background-color: rgb(33, 37, 43);
        #         color: white;
        #         font-size: 12pt;
        #         selection-background-color: rgb(92, 0, 138);
        #     }
        # """)

        # 添加交通疏导策略提示定时器
        self.advice_display_timer = QTimer()
        self.advice_display_timer.timeout.connect(self.update_traffic_advice_display)
        self.advice_display_timer.start(5000)  # 每5秒更新一次

        # 添加交通拥堵等级更新定时器
        self.congestion_update_timer = QTimer()
        self.congestion_update_timer.timeout.connect(self.update_congestion_progress_realtime)
        self.congestion_update_timer.start(5000)  # 每5秒更新一次，与流量信息同步

        # 设置 left_content 布局
        self.setup_left_content_layout()

        # 设置 right_content 布局
        self.setup_right_content_layout()

        # 设置违规查询页面布局
        self.setup_violation_layout()

        # 连接违规查询按钮点击事件
        self.pBtn_vio_query.clicked.connect(self.violation_table_manager.perform_query)

        # 连接违规统计按钮点击事件
        self.pBtn_vio_statistics.clicked.connect(self.violation_table_manager.create_violation_pie_chart)

        self.setup_export_buttons()

        # 设置流量查询页面布局
        self.setup_flow_layout()

        # 连接顶部按钮功能
        self.setup_top_buttons()

        # 可以在这里添加其他初始化代码
        self.setWindowTitle("智能交通管理系统")

        self.video_controller.set_video_switched_callback(self.on_video_switched)

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

    # main_detect.py (另一种方式)
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



    # def closeEvent(self, event):
    #     """
    #     窗口关闭事件，停止定时器并返回登录界面
    #     """
    #     # 停止所有定时器
    #     self.weather_time_manager.stop_timers()
    #
    #     # 调用关闭回调（如果存在）
    #     if self.close_callback:
    #         self.close_callback()
    #
    #     event.accept()

    def closeEvent(self, event):
        """
        窗口关闭事件，停止定时器并返回登录界面
        """
        # 停止所有定时器
        self.weather_time_manager.stop_timers()

        # 停止流量显示定时器
        if hasattr(self, 'flow_display_timer'):
            self.flow_display_timer.stop()

        # 停止交通疏导策略提示定时器
        if hasattr(self, 'advice_display_timer'):
            self.advice_display_timer.stop()

        # 停止拥堵程度更新定时器
        if hasattr(self, 'congestion_update_timer'):
            self.congestion_update_timer.stop()

        # 停止视频播放并关闭数据库连接
        if hasattr(self, 'video_controller') and self.video_controller:
            self.video_controller.stop_video()
            # 如果你的 VideoService 有 close_database_connection 方法，也调用它
            if hasattr(self.video_controller.video_service, 'close_database_connection'):
                self.video_controller.video_service.close_database_connection()

        # 调用关闭回调（如果存在）
        if self.close_callback:
            self.close_callback()

        # 停止车辆违规检测视频
        if hasattr(self, 'car_violation_view') and self.car_violation_view:
            self.car_violation_view.stop_videos()

        # 停止行人违规检测视频
        if hasattr(self, 'person_violation_view') and self.person_violation_view:
            self.person_violation_view.stop_videos()

        event.accept()

    def update_traffic_stats(self):
        """
        更新交通流量统计显示
        """
        try:
            # 检查视频服务是否存在且正在播放
            if (hasattr(self, 'video_controller') and
                    self.video_controller and
                    hasattr(self.video_controller, 'video_service') and
                    self.video_controller.video_service and
                    self.video_controller.video_service.is_playing):

                # 获取统计数据
                video_service = self.video_controller.video_service
                if hasattr(video_service, 'get_traffic_stats_for_ui'):
                    stats = video_service.get_traffic_stats_for_ui()
                else:
                    # 如果VideoService中没有这个方法，使用下面的实现
                    stats = self.get_traffic_stats_from_service(video_service)

                # 更新UI显示
                self.totalNumber.setText(stats['total_flow'])
                self.inNumber.setText(stats['entry_count'])
                self.outNumber.setText(stats['departure_count'])

                self.lineEdit_totalUp.setText(stats['total_flow_growth'])
                self.lineEdit_inUp.setText(stats['entry_growth'])
                self.lineEdit_outUp.setText(stats['departure_growth'])

        except Exception as e:
            print(f"更新交通流量统计时出错: {e}")

    def get_traffic_stats_from_service(self, video_service):
        """
        从视频服务中获取交通统计数据
        """

        # 格式化增长率显示
        def format_growth_rate(rate):
            if rate == float('inf'):
                return "^∞%"
            elif rate > 0:
                return f"^{rate:.1f}%".replace('.', '.')
            else:
                return f"{rate:.1f}%".replace('.', '.')

        stats = {
            'total_flow': str(video_service.last_vehicle_count_data) if hasattr(video_service,
                                                                                'last_vehicle_count_data') else "0",
            'entry_count': str(video_service.last_entry_count_data) if hasattr(video_service,
                                                                               'last_entry_count_data') else "0",
            'departure_count': str(video_service.last_departure_count_data) if hasattr(video_service,
                                                                                       'last_departure_count_data') else "0",
            'total_flow_growth': format_growth_rate(video_service.last_flow_growth_rate) if hasattr(video_service,
                                                                                                    'last_flow_growth_rate') else "00.0%",
            'entry_growth': format_growth_rate(video_service.last_entry_growth_rate) if hasattr(video_service,
                                                                                                'last_entry_growth_rate') else "00.0%",
            'departure_growth': format_growth_rate(video_service.last_departure_growth_rate) if hasattr(video_service,
                                                                                                        'last_departure_growth_rate') else "00.0%"
        }

        return stats

    def update_vehicle_info(self):
        """
        更新车辆信息显示
        """
        try:
            # 检查视频服务是否存在且正在播放
            if (hasattr(self, 'video_controller') and
                self.video_controller and
                hasattr(self.video_controller, 'video_service') and
                self.video_controller.video_service and
                self.video_controller.video_service.is_playing):

                # # 获取新识别到的车辆信息
                # video_service = self.video_controller.video_service
                # if hasattr(video_service, 'database_service'):
                #     latest_vehicles = video_service.database_service.get_latest_vehicles(20)

                # 从数据库获取最新车辆信息
                latest_vehicles = self.vehicle_table_manager.get_latest_vehicles(20)

                # 清空现有表格内容
                table = self.vehicle_table_manager.table
                table.clearContents()
                from PyQt5.QtWidgets import QTableWidgetItem  # 添加导入
                from PyQt5.QtCore import Qt
                from PyQt5.QtGui import QColor
                for i, vehicle in enumerate(latest_vehicles):
                    # 添加数据
                    table.setItem(i, 0, QTableWidgetItem(vehicle['plate_number']))
                    table.setItem(i, 1, QTableWidgetItem(vehicle['entry_time']))
                    table.setItem(i, 2, QTableWidgetItem(vehicle['departure_time']))

                    # 设置居中对齐
                    for col in range(3):
                        item = table.item(i, col)
                        if item:
                            item.setTextAlignment(Qt.AlignCenter)
                            item.setForeground(QColor(255, 255, 255))

        except Exception as e:
            print(f"更新车辆信息时出错: {e}")
            import traceback
            traceback.print_exc()

        #         if hasattr(video_service, 'tracked_objects'):
        #             # 遍历跟踪对象，查找有车牌号的新车辆
        #             for track_id, obj_info in video_service.tracked_objects.items():
        #                 # 检查是否是车辆类型且有车牌号
        #                 if (obj_info['type'] in ['car', 'bus', 'truck'] and
        #                     'plate_number' in obj_info and
        #                     obj_info['plate_number'] and
        #                     obj_info['plate_number'] != "对向来车"):
        #
        #                     # 检查该车辆是否已经显示在表格中
        #                     is_already_displayed = False
        #                     for row in range(self.vehicle_table_manager.table.rowCount()):
        #                         item = self.vehicle_table_manager.table.item(row, 0)
        #                         if item and item.text() == obj_info['plate_number']:
        #                             is_already_displayed = True
        #                             row_index=row
        #                             break
        #
        #                     entry_time = obj_info.get('entry_time', '未知')
        #                     if hasattr(entry_time, 'strftime'):
        #                         entry_time_str = entry_time.strftime("%Y-%m-%d %H:%M:%S")
        #                     else:
        #                         entry_time_str = str(entry_time)
        #
        #                     # 获取离开时间（如果存在）
        #                     exit_time_str = "未离开"
        #                     if track_id in video_service.temporarily_missing_vehicles:
        #                         exit_time = video_service.temporarily_missing_vehicles[track_id]
        #                         if hasattr(exit_time, 'strftime'):
        #                             exit_time_str = exit_time.strftime("%Y-%m-%d %H:%M:%S")
        #                         else:
        #                             exit_time_str = str(exit_time)
        #
        #                         # 如果未显示，则添加到表格中
        #                         if not is_already_displayed:
        #                             self.vehicle_table_manager.add_vehicle_record(
        #                                 obj_info['plate_number'],
        #                                 entry_time_str,
        #                                 exit_time_str  # 使用正确的驶出时间
        #                             )
        #                         else:
        #                             # 如果已经在表格中，更新驶出时间
        #                             exit_item = self.vehicle_table_manager.table.item(row_index, 2)
        #                             if exit_item:
        #                                 exit_item.setText(exit_time_str)
        #                                 exit_item.setTextAlignment(Qt.AlignCenter)
        #                                 exit_item.setForeground(QColor(255, 255, 255))
        # except Exception as e:
        #     print(f"更新车辆信息时出错: {e}")

    def update_traffic_flow_display(self):
        """
        更新流量信息显示到 plainTextEdit
        """
        try:
            # 获取最新的10条流量记录
            flow_records = self.get_latest_flow_records(10)
            print(f"获取到 {len(flow_records)} 条流量记录用于显示")

            if flow_records:
                # 清空当前文本
                self.plainTextEdit.clear()

                # 添加记录到文本框
                for i,record in enumerate(flow_records):
                    print(f"处理记录 {i}: {record}")  # 添加调试信息
                    # 格式化记录
                    formatted_record = self.format_flow_record(record)
                    self.plainTextEdit.appendPlainText(formatted_record)

                    # 如果不是最后一条记录，添加分割线
                    if i < len(flow_records) - 1:
                        self.plainTextEdit.appendPlainText("-" * 40)  # 添加分割线

        except Exception as e:
            print(f"更新流量信息显示时出错: {e}")

    def get_latest_flow_records(self, limit=10):
        """
        从数据库获取最新的流量记录
        :param limit: 获取记录的数量限制
        :return: 流量记录列表
        """
        try:
            # 通过视频控制器访问数据库服务
            if (hasattr(self, 'video_controller') and
                    self.video_controller and
                    hasattr(self.video_controller, 'video_service') and
                    self.video_controller.video_service and
                    hasattr(self.video_controller.video_service, 'database_service') and
                    self.video_controller.video_service.database_service):
                # 获取数据库服务
                db_service = self.video_controller.video_service.database_service

                # 获取最新的流量记录
                db_service = self.video_controller.video_service.database_service
                latest_flows = db_service.get_latest_traffic_flows(limit)
                return latest_flows

            return []
        except Exception as e:
            print(f"获取流量记录时出错: {e}")
            return []

    def format_flow_record(self, record):
        """
        格式化流量记录
        :param record: 数据库中的流量记录
        :return: 格式化后的字符串
        """
        try:
            # 从记录中提取信息
            road_id = record.get('road_id', '001')
            road_name = record.get('road_name', '新街口')

            # 格式化时间
            start_time = record.get('start_time', '')
            end_time = record.get('end_time', '')

            # if start_time:
            #     if isinstance(start_time, str):
            #         start_time_str = start_time.split(' ')[1][:8] if ' ' in start_time else start_time[:8]
            #     else:
            #         start_time_str = start_time.strftime("%H:%M:%S")
            # else:
            #     start_time_str = "00:00:00"
            #
            # if end_time:
            #     if isinstance(end_time, str):
            #         end_time_str = end_time.split(' ')[1][:8] if ' ' in end_time else end_time[:8]
            #     else:
            #         end_time_str = end_time.strftime("%H:%M:%S")
            # else:
            #     end_time_str = "00:00:00"

            if start_time:
                if isinstance(start_time, str):
                    # 如果是字符串格式，尝试解析完整的日期时间
                    if len(start_time) > 10:  # 包含时间信息
                        start_time_str = start_time.replace('T', ' ') if 'T' in start_time else start_time
                        # 将-替换为/以符合要求
                        if '-' in start_time_str:
                            parts = start_time_str.split(' ')
                            date_part = parts[0].replace('-', '/')
                            start_time_str = date_part + ' ' + parts[1] if len(parts) > 1 else date_part
                    else:
                        start_time_str = start_time
                else:
                    start_time_str = start_time.strftime("%Y/%m/%d %H:%M:%S")
            else:
                start_time_str = "0000/00/00 00:00:00"

            if end_time:
                if isinstance(end_time, str):
                    # 如果是字符串格式，尝试解析完整的日期时间
                    if len(end_time) > 10:  # 包含时间信息
                        end_time_str = end_time.replace('T', ' ') if 'T' in end_time else end_time
                        # 将-替换为/以符合要求
                        if '-' in end_time_str:
                            parts = end_time_str.split(' ')
                            date_part = parts[0].replace('-', '/')
                            end_time_str = date_part + ' ' + parts[1] if len(parts) > 1 else date_part
                    else:
                        end_time_str = end_time
                else:
                    end_time_str = end_time.strftime("%Y/%m/%d %H:%M:%S")
            else:
                end_time_str = "0000/00/00 00:00:00"

            # 获取统计数据
            vehicle_count = record.get('vehicle_count', 0)
            entry_count = record.get('entry_count', 0)
            departure_count = record.get('departure_count', 0)

            # # 构造格式化字符串
            # formatted = f"{road_id}-{road_name}-{start_time_str}-{end_time_str} 车流总量：{vehicle_count} 驶入总数：{entry_count} 驶出总数：{departure_count}"
            # return formatted

            # 构造新的三行格式
            # formatted = f"{road_id} {road_name}\n时间：{start_time_str}-{end_time_str}\n车流总量：{vehicle_count} 驶入总数：{entry_count} 驶出总数：{departure_count}"
            # return formatted

            # 构造新的三行格式，时间部分按要求格式化
            formatted = f"{road_id} {road_name}\n时间：{start_time_str}\n    - {end_time_str}\n车流总量：{vehicle_count} 驶入总数：{entry_count} 驶出总数：{departure_count}"
            return formatted


        except Exception as e:
            print(f"格式化流量记录时出错: {e}")
            return "格式化错误的记录"

    def get_traffic_level_and_advice(self, vehicle_count):
        """
        根据车流总量获取拥堵等级和交通疏导建议
        :param vehicle_count: 车流总量
        :return: (等级, 建议)
        """
        if vehicle_count <= 10:
            return 1, "建议维持常规交通管控模式，无需额外疏导措施，重点关注行人过街安全，保障道路通行顺畅。"
        elif vehicle_count <= 20:
            return 2, "建议加强路口信号灯基础调控，确保车辆有序通行，同时安排巡逻人员留意是否存在临时停车等影响车流的情况。"
        elif vehicle_count <= 25:
            return 3, "建议适当延长主路绿灯时长，引导支路车辆有序避让，避免车流在路口小幅积压。"
        elif vehicle_count <= 30:
            return 4, "建议在关键路口部署疏导人员，现场引导车辆快速通过，同时通过交通广播提示驾驶员选择备选路线。"
        elif vehicle_count <= 35:
            return 5, "建议启动区域交通协调机制，调整相邻路口信号灯配时，形成绿波带，减少车辆停车等待次数。"
        elif vehicle_count <= 40:
            return 6, "建议开放应急车道供社会车辆临时通行（非应急情况），并通过电子屏实时播报拥堵节点，引导车流分流。"
        elif vehicle_count <= 45:
            return 7, "建议临时增派警力在拥堵路段分段疏导，强制规范车辆并线秩序，避免加塞导致车流停滞。"
        elif vehicle_count <= 50:
            return 8, "建议实施临时交通管制，限制部分非必要车辆进入核心拥堵区域，同时协调公交加密班次分流客流。"
        elif vehicle_count <= 55:
            return 9, "建议启动高等级疏导预案，打通周边微循环道路，组织车辆绕行，同步联系交管指挥中心调配远端车流。"
        else:
            return 10, "建议全面启动应急疏导机制，封闭部分拥堵严重路段进行交通重构，通过多平台发布管制信息，引导市民错峰出行。"

    def update_traffic_advice_display(self):
        """
        更新交通疏导策略提示显示到 plainTextEdit_7
        """
        try:
            # 获取最新的10条流量记录
            flow_records = self.get_latest_flow_records(10)

            if flow_records:
                # 清空当前文本
                self.plainTextEdit_7.clear()

                # 添加记录到文本框
                for i, record in enumerate(flow_records):
                    # 格式化记录
                    formatted_record = self.format_advice_record(record)
                    self.plainTextEdit_7.appendPlainText(formatted_record)

                    # 如果不是最后一条记录，添加分割线
                    if i < len(flow_records) - 1:
                        self.plainTextEdit_7.appendPlainText("-" * 40)  # 添加分割线

        except Exception as e:
            print(f"更新交通疏导策略提示显示时出错: {e}")

    def format_advice_record(self, record):
        """
        格式化交通疏导建议记录
        :param record: 数据库中的流量记录
        :return: 格式化后的字符串
        """
        try:
            # 从记录中提取信息
            road_id = record.get('road_id', '001')
            road_name = record.get('road_name', '新街口')

            # 格式化时间
            start_time = record.get('start_time', '')
            end_time = record.get('end_time', '')

            # if start_time:
            #     if isinstance(start_time, str):
            #         start_time_str = start_time.split(' ')[1][:8] if ' ' in start_time else start_time[:8]
            #     else:
            #         start_time_str = start_time.strftime("%H:%M:%S")
            # else:
            #     start_time_str = "00:00:00"
            #
            # if end_time:
            #     if isinstance(end_time, str):
            #         end_time_str = end_time.split(' ')[1][:8] if ' ' in end_time else end_time[:8]
            #     else:
            #         end_time_str = end_time.strftime("%H:%M:%S")
            # else:
            #     end_time_str = "00:00:00"

            if start_time:
                if isinstance(start_time, str):
                    # 如果是字符串格式，尝试解析完整的日期时间
                    if len(start_time) > 10:  # 包含时间信息
                        start_time_str = start_time.replace('T', ' ') if 'T' in start_time else start_time
                        # 将-替换为/以符合要求
                        if '-' in start_time_str:
                            parts = start_time_str.split(' ')
                            date_part = parts[0].replace('-', '/')
                            start_time_str = date_part + ' ' + parts[1] if len(parts) > 1 else date_part
                    else:
                        start_time_str = start_time
                else:
                    start_time_str = start_time.strftime("%Y/%m/%d %H:%M:%S")
            else:
                start_time_str = "0000/00/00 00:00:00"

            if end_time:
                if isinstance(end_time, str):
                    # 如果是字符串格式，尝试解析完整的日期时间
                    if len(end_time) > 10:  # 包含时间信息
                        end_time_str = end_time.replace('T', ' ') if 'T' in end_time else end_time
                        # 将-替换为/以符合要求
                        if '-' in end_time_str:
                            parts = end_time_str.split(' ')
                            date_part = parts[0].replace('-', '/')
                            end_time_str = date_part + ' ' + parts[1] if len(parts) > 1 else date_part
                    else:
                        end_time_str = end_time
                else:
                    end_time_str = end_time.strftime("%Y/%m/%d %H:%M:%S")
            else:
                end_time_str = "0000/00/00 00:00:00"

            # 获取车流总量
            vehicle_count = record.get('vehicle_count', 0)

            # 获取拥堵等级和建议
            level, advice = self.get_traffic_level_and_advice(vehicle_count)

            # # 构造格式化字符串
            # formatted = f"{road_id}-{road_name}-{start_time_str}-{end_time_str} 拥堵等级：{level}级 交通疏导建议：{advice}"
            # return formatted

            # 构造新的四行格式
            # formatted = f"{road_id} {road_name}\n时间：{start_time_str}-{end_time_str}\n拥堵等级：{level}级\n交通疏导建议：{advice}"
            # return formatted

            # 构造新的四行格式，时间部分按要求格式化
            formatted = f"{road_id} {road_name}\n时间：{start_time_str}\n    - {end_time_str}\n拥堵等级：{level}级\n交通疏导建议：{advice}"
            return formatted



        except Exception as e:
            print(f"格式化交通疏导建议记录时出错: {e}")
            return "格式化错误的记录"

    def load_initial_data_safely(self):
        """
        安全地加载初始数据，检查数据库是否锁定
        """
        try:
            # 尝试检查数据库是否被锁定
            if not os.path.exists(self.db_path):
                print("数据库文件不存在")
                return

            # 尝试连接数据库并执行一个简单的查询来检查是否被锁定
            conn = sqlite3.connect(self.db_path, timeout=1.0)  # 设置1秒超时
            cursor = conn.cursor()

            # 执行一个简单的查询来测试数据库是否可用
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table' LIMIT 1")
            conn.close()

            # 如果没有异常，说明数据库可用，加载数据
            self.load_flow_data()
        except sqlite3.OperationalError as e:
            if "database is locked" in str(e):
                print("数据库被锁定，跳过初始数据加载")
            else:
                print(f"数据库连接错误: {e}")
        except Exception as e:
            print(f"加载初始数据时出错: {e}")

    def load_flow_data(self, start_time=None, end_time=None, road_id=None):
        """
        从数据库加载流量数据
        :param start_time: 开始时间
        :param end_time: 结束时间
        :param road_id: 路口序号
        """
        if not os.path.exists(self.db_path):
            print("数据库文件不存在")
            return

        try:
            # 设置较短的超时时间，避免长时间等待
            conn = sqlite3.connect(self.db_path, timeout=2.0)
            cursor = conn.cursor()

            # 构建查询语句
            query = """
                SELECT tf.road_id, r.road_name, tf.start_time, tf.end_time, 
                       tf.vehicle_count, tf.entry_count, tf.departure_count
                FROM trafficFlows tf
                LEFT JOIN roads r ON tf.road_id = r.road_id
                WHERE 1=1
            """
            params = []

            # 添加时间筛选条件
            if start_time:
                query += " AND tf.start_time >= ?"
                params.append(start_time)

            if end_time:
                query += " AND tf.end_time <= ?"
                params.append(end_time)

            # 添加路口序号筛选条件
            if road_id:
                query += " AND tf.road_id = ?"
                params.append(road_id)

            # 按时间排序
            query += " ORDER BY tf.start_time DESC"

            cursor.execute(query, params)
            rows = cursor.fetchall()
            conn.close()

            # 清空现有内容
            self.table.clearContents()
            self.table.setRowCount(len(rows) if len(rows) > 15 else 15)  # 确保至少有15行

            # 填充表格
            for row_idx, row in enumerate(rows):
                road_id, road_name, stat_time, end_time, vehicle_count, entry_count, departure_count = row

                # 格式化时间
                if isinstance(stat_time, str):
                    stat_time_str = stat_time
                else:
                    stat_time_str = stat_time.strftime("%Y-%m-%d %H:%M:%S") if stat_time else ""

                if isinstance(end_time, str):
                    end_time_str = end_time
                else:
                    end_time_str = end_time.strftime("%Y-%m-%d %H:%M:%S") if end_time else ""

                # 获取拥堵等级
                congestion_level = self.get_traffic_level(vehicle_count)

                # 添加数据
                self.table.setItem(row_idx, 0, QTableWidgetItem(road_id or ""))
                self.table.setItem(row_idx, 1, QTableWidgetItem(road_name or "未知路口"))
                self.table.setItem(row_idx, 2, QTableWidgetItem(stat_time_str))
                self.table.setItem(row_idx, 3, QTableWidgetItem(end_time_str))
                self.table.setItem(row_idx, 4, QTableWidgetItem(str(vehicle_count)))
                self.table.setItem(row_idx, 5, QTableWidgetItem(str(entry_count)))
                self.table.setItem(row_idx, 6, QTableWidgetItem(str(departure_count)))
                self.table.setItem(row_idx, 7, QTableWidgetItem(congestion_level))

                # 创建查看详情按钮
                detail_button = QPushButton("查看")
                detail_button.setStyleSheet("""
                    QPushButton {
                        background-color: rgb(0, 170, 255);
                        color: white;
                        border: none;
                        border-radius: 4px;
                        padding: 5px 10px;
                        font-weight: bold;
                    }
                    QPushButton:hover {
                        background-color: rgb(0, 150, 230);
                    }
                    QPushButton:pressed {
                        background-color: rgb(0, 130, 210);
                    }
                """)
                detail_button.setCursor(Qt.PointingHandCursor)
                detail_button.setFixedHeight(30)
                # 连接按钮点击事件（可选）
                # detail_button.clicked.connect(lambda: self.show_flow_details(road_id, road_name, stat_time_str, end_time_str, vehicle_count, entry_count, departure_count, congestion_level))

                # 将按钮添加到表格中
                self.table.setCellWidget(row_idx, 8, detail_button)

                # 设置居中对齐
                for col in range(8):  # 前8列
                    item = self.table.item(row_idx, col)
                    if item:
                        item.setTextAlignment(Qt.AlignCenter)
                        item.setForeground(QColor(255, 255, 255))

                # 设置拥堵等级列的颜色
                congestion_item = self.table.item(row_idx, 7)
                if congestion_item:
                    level_text = congestion_item.text()
                    # 根据拥堵等级1-10设置不同颜色
                    if level_text.startswith("1级"):
                        congestion_item.setForeground(QColor(0, 255, 0))  # 1级：绿色
                    elif level_text.startswith("2级"):
                        congestion_item.setForeground(QColor(127, 255, 0))  # 2级：黄绿色
                    elif level_text.startswith("3级"):
                        congestion_item.setForeground(QColor(255, 255, 0))  # 3级：黄色
                    elif level_text.startswith("4级"):
                        congestion_item.setForeground(QColor(255, 215, 0))  # 4级：金黄色
                    elif level_text.startswith("5级"):
                        congestion_item.setForeground(QColor(255, 165, 0))  # 5级：橙色
                    elif level_text.startswith("6级"):
                        congestion_item.setForeground(QColor(255, 140, 0))  # 6级：深橙色
                    elif level_text.startswith("7级"):
                        congestion_item.setForeground(QColor(255, 69, 0))  # 7级：红橙色
                    elif level_text.startswith("8级"):
                        congestion_item.setForeground(QColor(255, 0, 0))  # 8级：红色
                    elif level_text.startswith("9级"):
                        congestion_item.setForeground(QColor(139, 0, 0))  # 9级：深红色
                    elif level_text.startswith("10级"):
                        congestion_item.setForeground(QColor(128, 0, 0))  # 10级：暗红色
                    else:
                        congestion_item.setForeground(QColor(255, 255, 255))  # 默认：白色

        except sqlite3.OperationalError as e:
            if "database is locked" in str(e):
                print("数据库被锁定，无法加载流量数据")
            else:
                print(f"数据库操作错误: {e}")
        except Exception as e:
            print(f"加载流量数据时出错: {e}")
            import traceback
            traceback.print_exc()

    def update_congestion_progress_realtime(self):
        """
        实时更新拥堵程度进度条
        从数据库获取当前车流总量，并根据分类规则更新进度条
        """
        try:
            # 检查视频服务是否存在且正在播放
            if (hasattr(self, 'video_controller') and
                    self.video_controller and
                    hasattr(self.video_controller, 'video_service') and
                    self.video_controller.video_service and
                    self.video_controller.video_service.is_playing):

                # 获取当前车流总量
                video_service = self.video_controller.video_service

                # 从视频服务获取当前车流总量
                if hasattr(video_service, 'last_vehicle_count_data'):
                    vehicle_count = video_service.last_vehicle_count_data
                else:
                    vehicle_count = 0

                # 确保 vehicle_count 是数字类型
                try:
                    vehicle_count = int(vehicle_count)
                except (ValueError, TypeError):
                    vehicle_count = 0

                # 根据车流总量获取拥堵等级
                congestion_level = self.get_traffic_congestion_level(vehicle_count)

                # 更新进度条显示
                if hasattr(self.weather_time_manager, 'update_congestion_progress'):
                    self.weather_time_manager.update_congestion_progress(congestion_level)

        except Exception as e:
            print(f"更新拥堵程度进度条时出错: {e}")

    def get_traffic_congestion_level(self, vehicle_count):
        """
        根据车流总量获取拥堵等级 (1-10级)
        :param vehicle_count: 车流总量
        :return: 拥堵等级 (1-10)
        """
        try:
            vehicle_count = int(vehicle_count)
        except (ValueError, TypeError):
            return 1

        if vehicle_count <= 10:
            return 1  # 1级畅通
        elif vehicle_count <= 20:
            return 2  # 2级基本畅通
        elif vehicle_count <= 25:
            return 3  # 3级轻度拥堵
        elif vehicle_count <= 30:
            return 4  # 4级中度拥堵
        elif vehicle_count <= 35:
            return 5  # 5级较严重拥堵
        elif vehicle_count <= 40:
            return 6  # 6级严重拥堵
        elif vehicle_count <= 45:
            return 7  # 7级非常严重拥堵
        elif vehicle_count <= 50:
            return 8  # 8级极度拥堵
        elif vehicle_count <= 55:
            return 9  # 9级超严重拥堵
        else:
            return 10  # 10级瘫痪

    def on_video_switched(self):
        """
        视频切换后的回调处理
        """
        # 重启定时器以确保获取新的数据源
        self.restart_timers()

    def restart_timers(self):
        """
        重启所有相关定时器
        """
        # 重启流量显示定时器
        if hasattr(self, 'flow_display_timer'):
            self.flow_display_timer.stop()
            self.flow_display_timer.start(5000)

        # 重启交通疏导策略提示定时器
        if hasattr(self, 'advice_display_timer'):
            self.advice_display_timer.stop()
            self.advice_display_timer.start(5000)

        # 重启交通统计定时器
        if hasattr(self, 'traffic_stats_timer'):
            self.traffic_stats_timer.stop()
            self.traffic_stats_timer.start(5000)

        # 重启车辆信息更新定时器
        if hasattr(self, 'vehicle_update_timer'):
            self.vehicle_update_timer.stop()
            self.vehicle_update_timer.start(1000)

        # 重启拥堵等级更新定时器
        if hasattr(self, 'congestion_update_timer'):
            self.congestion_update_timer.stop()
            self.congestion_update_timer.start(5000)

    # 在 main_window.py 的 MainWindow 类中添加以下方法

    def setup_export_buttons(self):
        """
        设置导出按钮功能
        """
        # 连接车辆信息导出按钮
        self.output_vio.clicked.connect(self.export_vehicle_data)

        # 连接流量信息导出按钮
        self.output_vio_2.clicked.connect(self.export_flow_data)

    def export_vehicle_data(self):
        """
        导出车辆信息到CSV文件
        """
        try:
            # 打开文件保存对话框
            file_path, _ = QFileDialog.getSaveFileName(
                self,
                "导出车辆信息",
                "车辆信息.csv",
                "CSV文件 (*.csv)"
            )

            if not file_path:
                return

            # 从数据库获取最新的车辆信息
            latest_vehicles = self.vehicle_table_manager.get_latest_vehicles(1000)  # 获取最多1000条记录

            if not latest_vehicles:
                QMessageBox.information(self, "提示", "没有可导出的车辆数据")
                return

            # 写入CSV文件
            with open(file_path, 'w', newline='', encoding='utf-8-sig') as csvfile:
                fieldnames = ['车牌号', '进入时间', '离开时间']
                writer = csv.DictWriter(csvfile, fieldnames=fieldnames)

                # 写入表头
                writer.writeheader()

                # 写入数据
                for vehicle in latest_vehicles:
                    writer.writerow({
                        '车牌号': vehicle['plate_number'],
                        '进入时间': vehicle['entry_time'],
                        '离开时间': vehicle['departure_time']
                    })

            QMessageBox.information(self, "成功", f"车辆信息已成功导出到:\n{file_path}")

        except Exception as e:
            QMessageBox.critical(self, "错误", f"导出车辆信息时出错:\n{str(e)}")
            print(f"导出车辆信息时出错: {e}")

    def export_flow_data(self):
        """
        导出流量信息到CSV文件
        """
        try:
            # 打开文件保存对话框
            file_path, _ = QFileDialog.getSaveFileName(
                self,
                "导出流量信息",
                "流量信息.csv",
                "CSV文件 (*.csv)"
            )

            if not file_path:
                return

            # 从数据库获取最新的流量记录
            flow_records = self.get_latest_flow_records(1000)  # 获取最多1000条记录

            if not flow_records:
                QMessageBox.information(self, "提示", "没有可导出的流量数据")
                return

            # 写入CSV文件
            with open(file_path, 'w', newline='', encoding='utf-8-sig') as csvfile:
                fieldnames = ['路口序号', '路口名称', '开始时间', '结束时间', '车流总量', '驶入总数', '驶出总数']
                writer = csv.DictWriter(csvfile, fieldnames=fieldnames)

                # 写入表头
                writer.writeheader()

                # 写入数据
                for record in flow_records:
                    writer.writerow({
                        '路口序号': record.get('road_id', ''),
                        '路口名称': record.get('road_name', ''),
                        '开始时间': record.get('start_time', ''),
                        '结束时间': record.get('end_time', ''),
                        '车流总量': record.get('vehicle_count', 0),
                        '驶入总数': record.get('entry_count', 0),
                        '驶出总数': record.get('departure_count', 0)
                    })

            QMessageBox.information(self, "成功", f"流量信息已成功导出到:\n{file_path}")

        except Exception as e:
            QMessageBox.critical(self, "错误", f"导出流量信息时出错:\n{str(e)}")
            print(f"导出流量信息时出错: {e}")
