# flow_table.py
from PyQt5.QtWidgets import QTableWidget, QTableWidgetItem, QHeaderView, QVBoxLayout, QWidget, QPushButton, QHBoxLayout, \
    QFrame, QLabel, QDialog, QGridLayout
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QColor, QFont
from PyQt5 import QtGui
import os
import sqlite3
# 新增导入
import matplotlib.pyplot as plt
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
import matplotlib
matplotlib.use('Qt5Agg')

# 设置matplotlib支持中文显示
plt.rcParams['font.sans-serif'] = ['SimHei', 'Microsoft YaHei', 'DejaVu Sans']
plt.rcParams['axes.unicode_minus'] = False  # 解决负号'-'显示为方块的问题

class FlowTableManager:
    """
    流量信息表格管理器
    """

    def __init__(self, ui_form):
        self.ui = ui_form
        self.table = None
        self.db_path = "utils/traffic.db"  # 数据库路径

    def create_flow_table(self):
        """
        创建流量信息表格
        表格有9列，表头按顺序为路口序号、路口名称、开始时间、结束时间、车流总数、驶入总数、驶出总数、拥堵等级、查看详情
        """
        # 创建表格控件
        self.table = QTableWidget()

        # 设置表格行列
        self.table.setColumnCount(9)
        self.table.setRowCount(0)

        # 设置表头
        self.table.setHorizontalHeaderLabels(
            ['路口序号', '路口名称', '开始时间', '结束时间', '车流总数', '驶入总数', '驶出总数', '拥堵等级',
             '查看详情'])

        # 设置表格属性
        self.table.setEditTriggers(QTableWidget.NoEditTriggers)  # 只读
        self.table.setSelectionBehavior(QTableWidget.SelectRows)  # 整行选择
        self.table.verticalHeader().setVisible(False)  # 隐藏行号

        # 增大行高
        self.table.verticalHeader().setDefaultSectionSize(40)

        # 设置列宽自适应策略
        header = self.table.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.ResizeToContents)  # 路口序号列自适应内容
        header.setSectionResizeMode(1, QHeaderView.ResizeToContents)  # 路口名称列自适应内容
        header.setSectionResizeMode(2, QHeaderView.ResizeToContents)  # 开始时间列自适应内容
        header.setSectionResizeMode(3, QHeaderView.ResizeToContents)  # 结束时间列自适应内容
        header.setSectionResizeMode(4, QHeaderView.ResizeToContents)  # 车流总数列自适应内容
        header.setSectionResizeMode(5, QHeaderView.ResizeToContents)  # 驶入总数列自适应内容
        header.setSectionResizeMode(6, QHeaderView.ResizeToContents)  # 驶出总数列自适应内容
        header.setSectionResizeMode(7, QHeaderView.ResizeToContents)  # 拥堵等级列自适应内容
        header.setSectionResizeMode(8, QHeaderView.Fixed)  # 查看详情列固定宽度

        # 设置查看详情列的宽度
        # self.table.setColumnWidth(4, 100)
        self.table.setColumnWidth(8, 100)

        # 设置表格样式，与 violation_table 中一致
        self.table.setStyleSheet("""
            QTableWidget {
                background-color: rgb(33, 37, 43);
                alternate-background-color: rgb(40, 44, 52);
                gridline-color: rgb(60, 64, 72);
                color: white;
                border: none;
                selection-background-color: rgb(0, 170, 255);
                selection-color: white;
            }
            QTableWidget::item {
                padding: 8px;
                border-bottom: 1px solid rgb(60, 64, 72);
            }
            QHeaderView::section {
                background-color: rgb(30, 34, 40);
                color: rgb(0, 170, 255);
                padding: 10px;
                border: none;
                font-weight: bold;
                font-size: 10pt;
            }
            QTableCornerButton::section {
                background-color: rgb(30, 34, 40);
                border: none;
            }

            /* 垂直滚动条 */
            QScrollBar:vertical {
                border: none;
                background-color: rgb(30, 34, 40);
                width: 15px;
                border-radius: 7px;
                margin: 0px 0px 0px 0px;
            }

            /* 滚动条滑块 */
            QScrollBar::handle:vertical {
                background-color: rgb(0, 170, 255);
                border-radius: 7px;
                min-height: 20px;
            }

            /* 滚动条滑块悬停状态 */
            QScrollBar::handle:vertical:hover {
                background-color: rgb(0, 150, 230);
            }

            /* 滚动条滑块按下状态 */
            QScrollBar::handle:vertical:pressed {
                background-color: rgb(0, 130, 210);
            }

            /* 向上按钮 */
            QScrollBar::sub-line:vertical {
                border: none;
                background-color: rgb(30, 34, 40);
                height: 15px;
                border-top-left-radius: 7px;
                border-top-right-radius: 7px;
                subcontrol-position: top;
                subcontrol-origin: margin;
            }

            /* 向下按钮 */
            QScrollBar::add-line:vertical {
                border: none;
                background-color: rgb(30, 34, 40);
                height: 15px;
                border-bottom-left-radius: 7px;
                border-bottom-right-radius: 7px;
                subcontrol-position: bottom;
                subcontrol-origin: margin;
            }

            /* 向上箭头 */
            QScrollBar::sub-line:vertical:hover {
                background-color: rgb(40, 44, 52);
            }

            /* 向下箭头 */
            QScrollBar::add-line:vertical:hover {
                background-color: rgb(40, 44, 52);
            }

            /* 设置箭头图标 */
            QScrollBar::up-arrow:vertical, QScrollBar::down-arrow:vertical {
                width: 0px;
                height: 0px;
                background: none;
            }

            /* 滚动条空白区域 */
            QScrollBar::add-page:vertical, QScrollBar::sub-page:vertical {
                background: none;
            }

            /* 水平滚动条 */
            QScrollBar:horizontal {
                border: none;
                background-color: rgb(30, 34, 40);
                height: 15px;
                border-radius: 7px;
                margin: 0px 0px 0px 0px;
            }

            /* 水平滚动条滑块 */
            QScrollBar::handle:horizontal {
                background-color: rgb(0, 170, 255);
                border-radius: 7px;
                min-width: 20px;
            }

            /* 水平滚动条滑块悬停状态 */
            QScrollBar::handle:horizontal:hover {
                background-color: rgb(0, 150, 230);
            }

            /* 水平滚动条滑块按下状态 */
            QScrollBar::handle:horizontal:pressed {
                background-color: rgb(0, 130, 210);
            }

            /* 左按钮 */
            QScrollBar::sub-line:horizontal {
                border: none;
                background-color: rgb(30, 34, 40);
                width: 15px;
                border-top-left-radius: 7px;
                border-bottom-left-radius: 7px;
                subcontrol-position: left;
                subcontrol-origin: margin;
            }

            /* 右按钮 */
            QScrollBar::add-line:horizontal {
                border: none;
                background-color: rgb(30, 34, 40);
                width: 15px;
                border-top-right-radius: 7px;
                border-bottom-right-radius: 7px;
                subcontrol-position: right;
                subcontrol-origin: margin;
            }

            /* 左右按钮悬停状态 */
            QScrollBar::sub-line:horizontal:hover, QScrollBar::add-line:horizontal:hover {
                background-color: rgb(40, 44, 52);
            }

            /* 设置箭头图标 */
            QScrollBar::left-arrow:horizontal, QScrollBar::right-arrow:horizontal {
                width: 0px;
                height: 0px;
                background: none;
            }

            /* 水平滚动条空白区域 */
            QScrollBar::add-page:horizontal, QScrollBar::sub-page:horizontal {
                background: none;
            }
        """)

        # 设置表格尺寸
        self.table.setMinimumSize(1030, 900)  # 调整尺寸以适应新布局

        # 设置最小行数，确保空表格也有相同的外观
        self.table.setRowCount(30)  # 设置15行空行
        self.table.clearContents()  # 清除内容但保持行数

        # # 添加示例数据
        # self.add_sample_data()

        return self.table

    def add_sample_data(self):
        """
        添加示例数据到表格
        """
        if not self.table:
            return

        # 示例数据
        sample_data = [
            ("2023-10-01 08:00", "中山路与解放路交叉口", "120", "畅通", ""),
            ("2023-10-01 09:00", "南京东路", "280", "轻度拥堵", ""),
            ("2023-10-01 10:00", "人民广场", "450", "中度拥堵", ""),
            ("2023-10-01 11:00", "淮海中路", "320", "轻度拥堵", ""),
            ("2023-10-01 12:00", "徐家汇路口", "380", "中度拥堵", ""),
            ("2023-10-01 13:00", "外滩隧道", "150", "畅通", "")
        ]

        # 清除现有内容
        self.table.clearContents()

        # 添加数据
        for row, (time, location, flow, congestion, _) in enumerate(sample_data):
            # 添加数据
            self.table.setItem(row, 0, QTableWidgetItem(time))
            self.table.setItem(row, 1, QTableWidgetItem(location))
            self.table.setItem(row, 2, QTableWidgetItem(flow))
            self.table.setItem(row, 3, QTableWidgetItem(congestion))

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
            # detail_button.clicked.connect(lambda: self.show_flow_details(time, location, flow, congestion))

            # 将按钮添加到表格中
            self.table.setCellWidget(row, 4, detail_button)

            # 设置居中对齐
            for col in range(4):  # 前4列
                item = self.table.item(row, col)
                if item:
                    item.setTextAlignment(Qt.AlignCenter)
                    item.setForeground(QColor(255, 255, 255))

            # 设置拥堵等级列的颜色
            congestion_item = self.table.item(row, 3)
            if congestion_item:
                if congestion == "畅通":
                    congestion_item.setForeground(QColor(0, 255, 0))  # 绿色
                elif congestion == "轻度拥堵":
                    congestion_item.setForeground(QColor(255, 215, 0))  # 金色
                elif congestion == "中度拥堵":
                    congestion_item.setForeground(QColor(255, 140, 0))  # 橙色
                elif congestion == "严重拥堵":
                    congestion_item.setForeground(QColor(255, 0, 0))  # 红色

    def setup_flow_layout(self):
        """
        设置流量查询页面的布局
        在 flow_query 下方插入表格，并与 flow_query 垂直分布
        """
        # 创建垂直布局容器，添加到 frame_query_flow 中
        layout_container = QWidget(self.ui.frame_query_flow)
        layout_container.setGeometry(0, 0, 1071, 1141)  # 与 frame_query_flow 大小一致
        layout_container.setStyleSheet("background-color: rgb(40, 44, 52);")

        # 创建垂直布局
        main_layout = QVBoxLayout(layout_container)
        main_layout.setContentsMargins(20, 20, 10, 10)  # 保持适当的边距
        main_layout.setSpacing(15)

        # 添加 flow_query 到布局中（保持原有位置和大小）
        main_layout.addWidget(self.ui.flow_query)

        # 创建并添加流量信息表格
        self.create_flow_table()
        main_layout.addWidget(self.table)

        # 添加弹性空间
        main_layout.addStretch()

        # 连接查询按钮点击事件
        self.ui.pBtn_vio_query_2.clicked.connect(self.perform_query)

        # 连接流量数据分析按钮点击事件
        self.ui.pBtn_flow_statistics.clicked.connect(self.create_congestion_pie_chart)

        # 安全地加载初始数据
        self.load_initial_data_safely()

        return layout_container

    def clear_table_data(self):
        """
        清空表格数据
        """
        if self.table:
            # 清除内容但保持行数，确保表格外观一致
            self.table.clearContents()
            self.table.setRowCount(15)  # 保持15行

    def show_flow_details(self, flow_data):
        """
        显示流量详细信息对话框
        :param flow_data: 流量数据字典
        """
        try:
            # 创建并显示详细信息对话框
            dialog = FlowDetailDialog(flow_data, self.ui)
            dialog.exec_()
        except Exception as e:
            print(f"显示流量详细信息时出错: {e}")

    def get_traffic_level(self, vehicle_count):
        """
        根据车流总量获取拥堵等级
        :param vehicle_count: 车流总量
        :return: 拥堵等级
        """
        try:
            vehicle_count = int(vehicle_count)
        except (ValueError, TypeError):
            return "未知"

        if vehicle_count <= 10:
            return "1级畅通"
        elif vehicle_count <= 20:
            return "2级基本畅通"
        elif vehicle_count <= 25:
            return "3级轻度拥堵"
        elif vehicle_count <= 30:
            return "4级中度拥堵"
        elif vehicle_count <= 35:
            return "5级较严重拥堵"
        elif vehicle_count <= 40:
            return "6级严重拥堵"
        elif vehicle_count <= 45:
            return "7级非常严重拥堵"
        elif vehicle_count <= 50:
            return "8级极度拥堵"
        elif vehicle_count <= 55:
            return "9级超严重拥堵"
        else:
            return "10级瘫痪"

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
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()

            # 构建查询语句，使用正确的列名
            query = """
                SELECT tf.roadId, r.roadName, tf.startTime, tf.endTime, 
                       tf.vehicleCount, tf.entryCount, tf.departureCount
                FROM trafficFlows tf
                LEFT JOIN roads r ON tf.roadId = r.roadId
                WHERE 1=1
            """
            params = []

            # 添加时间筛选条件
            if start_time:
                query += " AND tf.startTime >= ?"
                params.append(start_time)

            if end_time:
                query += " AND tf.endTime <= ?"
                params.append(end_time)

            # 添加路口序号筛选条件
            if road_id:
                query += " AND tf.roadId = ?"
                params.append(road_id)

            # 按时间排序
            query += " ORDER BY tf.startTime DESC"

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
                self.table.setItem(row_idx, 0, QTableWidgetItem(str(road_id) or ""))
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

                # 准备传递给详情窗口的数据
                flow_data = {
                    'road_id': str(road_id) or "",
                    'road_name': road_name or "未知路口",
                    'start_time': stat_time_str,
                    'end_time': end_time_str,
                    'vehicle_count': vehicle_count,
                    'entry_count': entry_count,
                    'departure_count': departure_count,
                    'congestion_level': congestion_level
                }

                # 连接按钮点击事件
                detail_button.clicked.connect(lambda checked, data=flow_data: self.show_flow_details(data))

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

    def perform_query(self):
        """
        执行查询操作
        """
        """
            执行查询操作
            """
        # 获取查询条件
        start_time = self.ui.time_start_5.dateTime().toString(
            "yyyy-MM-dd hh:mm:ss") if not self.ui.time_start_5.dateTime().isNull() else None
        end_time = self.ui.time_end_4.dateTime().toString(
            "yyyy-MM-dd hh:mm:ss") if not self.ui.time_end_4.dateTime().isNull() else None
        road_id = self.ui.lineEdit_2.text().strip() if self.ui.lineEdit_2.text().strip() else None

        # 加载数据
        self.load_flow_data(start_time, end_time, road_id)

    def load_initial_data_safely(self):
        """
        安全地加载初始数据，检查数据库是否锁定
        """
        try:
            # 检查数据库文件是否存在
            if not os.path.exists(self.db_path):
                print("数据库文件不存在")
                # 填充空表格以保持界面一致性
                self.clear_table_data()
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
                # 即使数据库被锁定，也要确保表格有适当的行数
                self.clear_table_data()
            else:
                print(f"数据库连接错误: {e}")
                self.clear_table_data()
        except Exception as e:
            print(f"加载初始数据时出错: {e}")
            self.clear_table_data()

    def get_congestion_statistics(self):
        """
        从数据库获取拥堵等级统计数据
        :return: 各等级区间占比的字典
        """
        if not os.path.exists(self.db_path):
            print("数据库文件不存在")
            return {}

        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()

            # 查询所有流量数据
            query = """
                SELECT tf.vehicleCount
                FROM trafficFlows tf
            """
            cursor.execute(query)
            rows = cursor.fetchall()
            conn.close()

            # 初始化各等级计数器
            level_counts = {
                '1-2级': 0,
                '3-4级': 0,
                '5-6级': 0,
                '7-8级': 0,
                '9-10级': 0
            }

            # 统计各等级数量
            for row in rows:
                vehicle_count = row[0]
                level = self.get_traffic_congestion_level(vehicle_count)

                if level in [1, 2]:
                    level_counts['1-2级'] += 1
                elif level in [3, 4]:
                    level_counts['3-4级'] += 1
                elif level in [5, 6]:
                    level_counts['5-6级'] += 1
                elif level in [7, 8]:
                    level_counts['7-8级'] += 1
                elif level in [9, 10]:
                    level_counts['9-10级'] += 1

            # 计算总数量
            total = sum(level_counts.values())

            # 计算占比
            if total > 0:
                level_percentages = {
                    level: (count / total) * 100
                    for level, count in level_counts.items()
                }
            else:
                level_percentages = level_counts  # 全为0

            return level_percentages

        except sqlite3.OperationalError as e:
            if "database is locked" in str(e):
                print("数据库被锁定，无法获取统计数据")
            else:
                print(f"数据库操作错误: {e}")
            return {}
        except Exception as e:
            print(f"获取统计数据时出错: {e}")
            import traceback
            traceback.print_exc()
            return {}

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

    def create_congestion_pie_chart(self):
        """
        创建拥堵等级占比饼状图并显示在 widget_flow_statistics 中
        """
        # 获取统计数据
        stats = self.get_congestion_statistics()

        # 过滤掉占比为0的数据
        labels = []
        sizes = []
        colors = []

        # 定义颜色方案
        color_map = {
            '1-2级': '#4CAF50',  # 绿色
            '3-4级': '#8BC34A',  # 浅绿
            '5-6级': '#FFC107',  # 黄色
            '7-8级': '#FF9800',  # 橙色
            '9-10级': '#F44336'  # 红色
        }

        for level, percentage in stats.items():
            if percentage > 0:  # 只显示占比大于0的部分
                labels.append(f"{level}\n{percentage:.1f}%")
                sizes.append(percentage)
                colors.append(color_map[level])

        # 如果没有数据，显示提示信息
        if not sizes:
            # 清除widget_flow_statistics中的内容
            for i in reversed(
                    range(self.ui.widget_flow_statistics.layout().count())) if self.ui.widget_flow_statistics.layout() else []:
                self.ui.widget_flow_statistics.layout().itemAt(i).widget().setParent(None)

            # 添加提示标签
            layout = QVBoxLayout(self.ui.widget_flow_statistics)
            label = QLabel("暂无数据可显示")
            label.setAlignment(Qt.AlignCenter)
            label.setStyleSheet("color: white; font-size: 18px;")
            layout.addWidget(label)
            return

        # 创建图表
        fig, ax = plt.subplots(figsize=(8, 6), subplot_kw=dict(aspect="equal"))
        fig.patch.set_facecolor('#21252B')  # 设置背景色与界面一致

        # 绘制饼状图
        wedges, texts = ax.pie(sizes, colors=colors, startangle=90,
                               wedgeprops=dict(width=0.5, edgecolor='#21252B', linewidth=2))

        # 设置文本颜色为白色
        for text in texts:
            text.set_color('white')
            text.set_fontsize(10)

        # 添加图例 - 这里是需要修改的部分
        legend = ax.legend(wedges, [f"{label.split()[0]}: {size:.1f}%" for label, size in zip(labels, sizes)],
                           title="等级",
                           loc="center left",
                           bbox_to_anchor=(0.8, -0.3, 0.5, 1),
                           facecolor='#21252B',
                           edgecolor='#21252B')

        # 设置图例文本颜色
        for text in legend.get_texts():
            text.set_color('white')

        # 设置图例标题颜色为白色（新增）
        legend.get_title().set_color('white')

        # 设置标题
        ax.set_title('交通拥堵等级占比分析', color='white', fontsize=16, pad=20)

        # 在 widget_flow_statistics 中显示图表
        # 清除之前的内容
        if self.ui.widget_flow_statistics.layout():
            for i in reversed(range(self.ui.widget_flow_statistics.layout().count())):
                self.ui.widget_flow_statistics.layout().itemAt(i).widget().setParent(None)
        else:
            layout = QVBoxLayout(self.ui.widget_flow_statistics)
            layout.setContentsMargins(20, 20, 20, 20)

        # 创建画布并添加到布局
        canvas = FigureCanvas(fig)
        self.ui.widget_flow_statistics.layout().addWidget(canvas)

        # 刷新画布
        canvas.draw()


from PyQt5.QtWidgets import QDialog, QLabel, QGridLayout, QFrame
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont


class FlowDetailDialog(QDialog):
    """
    流量详细信息对话框
    """

    def __init__(self, flow_data, parent=None):
        super().__init__(parent)
        self.flow_data = flow_data
        self.init_ui()

    def init_ui(self):
        """
        初始化UI界面
        """
        # 设置窗口属性
        self.setWindowTitle("流量详细信息")
        self.setWindowFlags(Qt.Dialog | Qt.WindowCloseButtonHint)
        self.setModal(True)
        self.resize(600, 500)  # 增大窗口尺寸
        self.setStyleSheet("""
            QDialog {
                background-color: rgb(40, 44, 52);
                color: white;
            }
        """)

        # 创建主布局
        layout = QGridLayout(self)
        layout.setSpacing(20)  # 增大间距
        layout.setContentsMargins(40, 40, 40, 40)  # 增大边距

        # 设置标题
        title_label = QLabel("流量详细信息")
        title_font = QFont()
        title_font.setPointSize(18)  # 增大标题字体
        title_font.setBold(True)
        title_label.setFont(title_font)
        title_label.setStyleSheet("color: rgb(0, 170, 255);")
        title_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(title_label, 0, 0, 1, 2)

        # 创建分隔线
        line = QFrame()
        line.setFrameShape(QFrame.HLine)
        line.setFrameShadow(QFrame.Sunken)
        line.setStyleSheet("color: rgb(60, 64, 72);")
        layout.addWidget(line, 1, 0, 1, 2)

        # 显示详细信息
        labels = ['路口序号', '路口名称', '开始时间', '结束时间', '车流总数', '驶入总数', '驶出总数', '拥堵等级']
        values = [
            self.flow_data.get('road_id', ''),
            self.flow_data.get('road_name', ''),
            self.flow_data.get('start_time', ''),
            self.flow_data.get('end_time', ''),
            str(self.flow_data.get('vehicle_count', '')),
            str(self.flow_data.get('entry_count', '')),
            str(self.flow_data.get('departure_count', '')),
            self.flow_data.get('congestion_level', '')
        ]

        # 添加信息标签和值
        for i, (label, value) in enumerate(zip(labels, values)):
            # 创建标签
            label_widget = QLabel(f"{label}:")
            label_font = QFont()
            label_font.setPointSize(12)  # 增大标签字体
            label_font.setBold(True)
            label_widget.setFont(label_font)
            label_widget.setStyleSheet("color: white;")
            layout.addWidget(label_widget, i + 2, 0, Qt.AlignLeft)

            # 创建值
            value_widget = QLabel(str(value))
            value_font = QFont()
            value_font.setPointSize(12)  # 增大值字体
            value_widget.setFont(value_font)
            value_widget.setStyleSheet("""
                color: white; 
                background-color: rgba(33, 37, 43, 150);
                padding: 8px;
                border-radius: 4px;
            """)
            value_widget.setWordWrap(True)
            value_widget.setMinimumHeight(40)  # 设置最小高度
            layout.addWidget(value_widget, i + 2, 1, Qt.AlignLeft)

        # 设置列的拉伸策略
        layout.setColumnStretch(0, 1)
        layout.setColumnStretch(1, 3)
