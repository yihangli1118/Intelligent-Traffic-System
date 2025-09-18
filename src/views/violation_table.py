# violation_table.py
from PyQt5.QtWidgets import QTableWidget, QTableWidgetItem, QHeaderView, QVBoxLayout, QWidget, QPushButton, QHBoxLayout, \
    QFrame, QDialog, QLabel, QGridLayout
from PyQt5.QtCore import Qt, QByteArray
from PyQt5.QtGui import QColor, QFont, QPixmap, QImage
import sqlite3
import os

class ViolationTableManager:
    """
    车辆信息表格管理器
    """

    def __init__(self, ui_form):
        self.ui = ui_form
        self.table = None
        self.db_path = "utils/traffic.db"  # 数据库路径
        self.current_row = 0  # 当前已加载的数据行数
        self.page_size = 15  # 每页加载的数据量

    def create_violation_table(self):
        """
        创建车辆信息表格
        """
        # 创建表格控件
        self.table = QTableWidget()

        # 设置表格行列
        self.table.setColumnCount(9)  # 修改为9列
        self.table.setRowCount(0)

        # 设置表头（按新顺序）
        self.table.setHorizontalHeaderLabels([
            '车牌号', '路口序号', '路口名称', '驶入时间', '驶出时间',
            '车身颜色', '车牌颜色', '车辆速度', '查看详情'
        ])

        # 设置表格属性
        self.table.setEditTriggers(QTableWidget.NoEditTriggers)  # 只读
        self.table.setSelectionBehavior(QTableWidget.SelectRows)  # 整行选择
        self.table.verticalHeader().setVisible(False)  # 隐藏行号

        # 增大行高
        self.table.verticalHeader().setDefaultSectionSize(40)

        # 设置列宽自适应策略
        header = self.table.horizontalHeader()
        for i in range(8):  # 前8列自适应内容
            header.setSectionResizeMode(i, QHeaderView.ResizeToContents)
        header.setSectionResizeMode(8, QHeaderView.Fixed)  # 查看详情列固定宽度

        # 设置查看详情列的宽度
        self.table.setColumnWidth(8, 100)

        # 设置表格样式，包括美化滚动条
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
        self.table.setFixedSize(1030, 900)  # 调整尺寸以适应新布局

        # 设置最小行数，确保空表格也有相同的外观
        self.table.setRowCount(30)  # 设置15行空行
        self.table.clearContents()  # 清除内容但保持行数

        # 连接垂直滚动条的信号
        self.table.verticalScrollBar().valueChanged.connect(self.on_vertical_scroll)

        # 添加初始数据
        self.load_initial_data()

        return self.table

    def load_initial_data(self):
        """
        从数据库加载初始数据
        """

        self.current_row = 0
        self.load_data_batch()

    def load_data_batch(self):
        """
        从数据库加载一批数据
        """
        if not os.path.exists(self.db_path):
            print("数据库文件不存在")
            return

        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()

            # 查询车辆信息，关联roads表获取路口名称
            query = """
                SELECT v.plateNumber, v.roadId, r.roadName, v.entryTime, v.departureTime, 
                       v.bodyColor, v.plateColor, v.speed
                FROM vehicles v
                LEFT JOIN roads r ON v.roadId = r.roadId
                ORDER BY v.entryTime DESC
                LIMIT ? OFFSET ?
            """

            cursor.execute(query, (self.page_size, self.current_row))
            rows = cursor.fetchall()

            # 填充表格
            for i, row in enumerate(rows):
                row_index = self.current_row + i

                # 确保有足够的行
                if row_index >= self.table.rowCount():
                    self.table.setRowCount(row_index + 1)

                # 添加数据
                self.table.setItem(row_index, 0, QTableWidgetItem(row[0] or "无车牌"))  # 车牌号
                self.table.setItem(row_index, 1, QTableWidgetItem(row[1] or "未知"))   # 路口序号
                self.table.setItem(row_index, 2, QTableWidgetItem(row[2] or "未知"))   # 路口名称
                self.table.setItem(row_index, 3, QTableWidgetItem(row[3] or "未知"))   # 驶入时间
                self.table.setItem(row_index, 4, QTableWidgetItem(row[4] or "未离开")) # 驶出时间
                self.table.setItem(row_index, 5, QTableWidgetItem(row[5] or "未知"))   # 车身颜色
                self.table.setItem(row_index, 6, QTableWidgetItem(row[6] or "未知"))   # 车牌颜色
                self.table.setItem(row_index, 7, QTableWidgetItem(str(row[7]) if row[7] is not None else "未知"))  # 车辆速度

                from functools import partial
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

                # 正确传递参数
                row_data = list(row)  # 复制当前行数据
                detail_button.clicked.connect(partial(self.show_violation_details, row_data))

                # 将按钮添加到表格中
                self.table.setCellWidget(row_index, 8, detail_button)

                # 设置居中对齐
                for col in range(8):  # 前8列
                    item = self.table.item(row_index, col)
                    if item:
                        item.setTextAlignment(Qt.AlignCenter)
                        item.setForeground(QColor(255, 255, 255))

            self.current_row += len(rows)
            conn.close()

        except Exception as e:
            print(f"加载数据时出错: {e}")

    def on_vertical_scroll(self, value):
        """
        垂直滚动条滚动事件处理
        """
        # 当滚动到接近底部时加载更多数据
        if value >= self.table.verticalScrollBar().maximum() * 0.8:
            self.load_data_batch()

    def setup_violation_layout(self):
        """
        设置违规查询页面的布局
        在 violation_query 下方插入表格，并与 violation_query 垂直布局
        """
        # 创建新的垂直布局容器
        layout_container = QWidget(self.ui.frame_query)
        layout_container.setGeometry(0, 0, 800, 721)
        layout_container.setStyleSheet("background-color: rgb(40, 44, 52);")

        # 创建垂直布局
        main_layout = QVBoxLayout(layout_container)
        main_layout.setContentsMargins(15, 15, 15, 15)
        main_layout.setSpacing(15)

        # 添加 violation_query 到布局中
        main_layout.addWidget(self.ui.violation_query)

        # 创建并添加违规信息表格
        self.create_violation_table()
        main_layout.addWidget(self.table)

        # 添加弹性空间
        main_layout.addStretch()

        # 将容器添加到父级布局中
        parent_layout = QVBoxLayout(self.ui.frame_query)
        parent_layout.setContentsMargins(0, 0, 0, 0)
        parent_layout.addWidget(layout_container)

        # 确保 widget_vio_statistics 有布局
        if not self.ui.widget_vio_statistics.layout():
            stats_layout = QVBoxLayout(self.ui.widget_vio_statistics)
            stats_layout.setContentsMargins(10, 10, 10, 10)

        return layout_container

    def clear_table_data(self):
        """
        清空表格数据
        """
        if self.table:
            # 清除内容但保持行数，确保表格外观一致
            self.table.clearContents()
            # self.table.setRowCount(15)  # 保持15行
            self.table.setRowCount(30)  # 保持30行
            self.current_row = 0

    def show_violation_details(self, vehicle_data):
        """
        显示车辆详细信息对话框
        :param vehicle_data: 车辆数据 [车牌号, 路口序号, 路口名称, 驶入时间, 驶出时间, 车身颜色, 车牌颜色, 车辆速度]
        """
        try:
            dialog = VehicleDetailDialog(vehicle_data, self.db_path, self.ui)
            dialog.exec_()
        except Exception as e:
            print(f"显示车辆详细信息时出错: {e}")


    def query_vehicles(self, plate_number=None, road_id=None, start_time=None, end_time=None):
        """
        根据车牌号、道路序号和时间区间查询车辆信息
        :param plate_number: 车牌号
        :param road_id: 路口序号
        :param start_time: 查询开始时间
        :param end_time: 查询结束时间
        """
        # 清空当前表格内容
        self.table.clearContents()

        if not os.path.exists(self.db_path):
            print("数据库文件不存在")
            return

        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()

            # 构建查询语句
            base_query = """
                SELECT v.plateNumber, v.roadId, r.roadName, v.entryTime, v.departureTime, 
                       v.bodyColor, v.plateColor, v.speed
                FROM vehicles v
                LEFT JOIN roads r ON v.roadId = r.roadId
            """

            conditions = []
            params = []

            # 根据输入参数添加查询条件
            if plate_number:
                conditions.append("v.plateNumber LIKE ?")
                params.append(f"%{plate_number}%")

            if road_id:
                conditions.append("v.roadId = ?")
                params.append(road_id)

            # 添加时间区间查询条件
            if start_time:
                conditions.append("v.entryTime >= ?")
                params.append(start_time)

            if end_time:
                conditions.append("v.entryTime <= ?")
                params.append(end_time)

            # 如果有条件则添加 WHERE 子句
            if conditions:
                base_query += " WHERE " + " AND ".join(conditions)

            # 添加排序
            base_query += " ORDER BY v.entryTime DESC"

            cursor.execute(base_query, params)
            rows = cursor.fetchall()

            # 设置表格行数
            self.table.setRowCount(max(len(rows), 30))

            # 填充表格
            for i, row in enumerate(rows):
                # 添加数据
                self.table.setItem(i, 0, QTableWidgetItem(row[0] or "无车牌"))  # 车牌号
                self.table.setItem(i, 1, QTableWidgetItem(row[1] or "未知"))  # 路口序号
                self.table.setItem(i, 2, QTableWidgetItem(row[2] or "未知"))  # 路口名称
                self.table.setItem(i, 3, QTableWidgetItem(row[3] or "未知"))  # 驶入时间
                self.table.setItem(i, 4, QTableWidgetItem(row[4] or "未离开"))  # 驶出时间
                self.table.setItem(i, 5, QTableWidgetItem(row[5] or "未知"))  # 车身颜色
                self.table.setItem(i, 6, QTableWidgetItem(row[6] or "未知"))  # 车牌颜色
                self.table.setItem(i, 7, QTableWidgetItem(str(row[7]) if row[7] is not None else "未知"))  # 车辆速度

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

                # 正确传递参数
                row_data = list(row)  # 复制当前行数据
                detail_button.clicked.connect(partial(self.show_violation_details, row_data))

                # 将按钮添加到表格中
                self.table.setCellWidget(i, 8, detail_button)

                # 设置居中对齐
                for col in range(8):  # 前8列
                    item = self.table.item(i, col)
                    if item:
                        item.setTextAlignment(Qt.AlignCenter)
                        item.setForeground(QColor(255, 255, 255))

            self.current_row = len(rows)
            conn.close()

        except Exception as e:
            print(f"查询数据时出错: {e}")

    def perform_query(self):
        """
        执行查询操作 - 从UI获取查询条件并执行查询
        """
        # 获取输入的查询条件
        plate_number = self.ui.lineEdit_violation.text().strip()
        road_id = self.ui.lineEdit.text().strip()

        # 获取时间查询条件
        start_time = self.ui.time_start_3.dateTime().toString("yyyy-MM-dd HH:mm:ss") if self.ui.time_start_3 else None
        end_time = self.ui.time_end_2.dateTime().toString("yyyy-MM-dd HH:mm:ss") if self.ui.time_end_2 else None

        # 检查是否有任何查询条件
        has_plate = bool(plate_number)
        has_road = bool(road_id)
        has_time = (self.ui.time_start_3 and self.ui.time_start_3.dateTime().isValid()) or \
                   (self.ui.time_end_2 and self.ui.time_end_2.dateTime().isValid())

        # 如果没有任何查询条件，则显示所有数据
        if not has_plate and not has_road and not has_time:
            self.load_initial_data()
            return

        # 根据输入条件查询
        self.query_vehicles(
            plate_number=plate_number if plate_number else None,
            road_id=road_id if road_id else None,
            start_time=start_time if (self.ui.time_start_3 and self.ui.time_start_3.dateTime().isValid()) else None,
            end_time=end_time if (self.ui.time_end_2 and self.ui.time_end_2.dateTime().isValid()) else None
        )

    def create_violation_pie_chart(self):
        """
        创建违规统计饼状图并在 widget_vio_statistics 中显示
        """
        if not os.path.exists(self.db_path):
            print("数据库文件不存在")
            return

        try:
            import matplotlib.pyplot as plt
            from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
            import numpy as np

            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()

            # 查询各路口车辆数量
            query = """
                SELECT r.roadName, COUNT(v.plateNumber) as vehicle_count
                FROM vehicles v
                LEFT JOIN roads r ON v.roadId = r.roadId
                WHERE r.roadName IS NOT NULL
                GROUP BY r.roadName
                ORDER BY vehicle_count DESC
            """

            cursor.execute(query)
            rows = cursor.fetchall()
            conn.close()

            if not rows:
                print("没有数据可以绘制图表")
                return

            # 提取数据
            road_names = [row[0] for row in rows]
            vehicle_counts = [row[1] for row in rows]

            # 计算占比
            total_vehicles = sum(vehicle_counts)
            if total_vehicles == 0:
                print("没有车辆数据可以绘制图表")
                return

            percentages = [count / total_vehicles * 100 for count in vehicle_counts]

            # 创建颜色列表
            colors = plt.cm.Set3(np.linspace(0, 1, len(road_names)))

            # 创建图表
            fig, ax = plt.subplots(figsize=(10, 8))
            fig.patch.set_facecolor((40 / 255, 44 / 255, 52 / 255))  # 设置背景颜色匹配UI主题

            # 绘制饼图
            wedges, texts, autotexts = ax.pie(
                vehicle_counts,
                labels=road_names,
                autopct=lambda pct: f'{pct:.1f}%',
                colors=colors,
                startangle=90,
                textprops={'color': 'white', 'fontsize': 10}
            )

            # 设置标题
            ax.set_title('各路口车辆占比统计', color='white', fontsize=24, pad=20)

            # 设置图例
            ax.legend(wedges, [f'{name}: {count}辆' for name, count in zip(road_names, vehicle_counts)],
                      title="路口详情",
                      loc="center left",
                      bbox_to_anchor=(0.75, -0.55, 0.5, 1),
                      facecolor=(33 / 255, 37 / 255, 43 / 255),
                      edgecolor='white',
                      labelcolor='white')

            # 设置整个图表背景透明
            ax.set_facecolor('none')

            # 清除 widget_vio_statistics 中的现有内容
            if self.ui.widget_vio_statistics.layout():
                # 清除布局中的所有控件
                while self.ui.widget_vio_statistics.layout().count():
                    child = self.ui.widget_vio_statistics.layout().takeAt(0)
                    if child.widget():
                        child.widget().deleteLater()

            # 创建画布并添加到 widget_vio_statistics
            canvas = FigureCanvas(fig)
            canvas.setStyleSheet("background-color: rgb(40, 44, 52);")

            # 获取 widget_vio_statistics 的布局
            layout = self.ui.widget_vio_statistics.layout()

            # 添加画布到布局
            layout.addWidget(canvas)

            # 刷新画布
            canvas.draw()

        except Exception as e:
            print(f"生成饼状图时出错: {e}")
            import traceback
            traceback.print_exc()

class ViolationTableLayout:
    """
    车辆信息表格布局管理器
    负责将车辆信息表格插入到 violation_query 下方，并与之垂直分布
    """

    def __init__(self, ui_form):
        self.ui = ui_form
        self.table_manager = ViolationTableManager(ui_form)
        self.layout_container = None

    def setup_layout(self):
        """
        设置车辆查询页面的垂直布局
        将 violation_query 和表格垂直排列
        """
        # 清除 violation_query 的父级关系，以便重新布局
        if self.ui.violation_query.parent() == self.ui.frame_query:
            self.ui.violation_query.setParent(None)

        # 创建布局容器
        self.layout_container = QWidget(self.ui.frame_query)
        self.layout_container.setGeometry(0, 0, 800, 721)
        self.layout_container.setStyleSheet("background-color: rgb(40, 44, 52);")

        # 创建垂直布局
        main_layout = QVBoxLayout(self.layout_container)
        main_layout.setContentsMargins(15, 15, 15, 15)
        main_layout.setSpacing(15)

        # 添加 violation_query 到布局中
        main_layout.addWidget(self.ui.violation_query)

        # 创建并添加车辆信息表格
        table = self.table_manager.create_violation_table()
        main_layout.addWidget(table)

        # 添加弹性空间
        main_layout.addStretch()

        return self.layout_container

    def update_table_data(self):
        """
        更新表格数据
        """
        self.table_manager.load_initial_data()

    def clear_table(self):
        """
        清空表格数据
        """
        self.table_manager.clear_table_data()

class VehicleDetailDialog(QDialog):
    """
    车辆详细信息对话框
    """

    def __init__(self, vehicle_data, db_path="utils/traffic.db", parent=None):
        super().__init__(parent)
        self.vehicle_data = vehicle_data
        self.db_path = db_path
        self.init_ui()

    def init_ui(self):
        """
        初始化UI界面
        """
        self.setWindowTitle("车辆详细信息")
        # 增大窗口尺寸以适应更高的文本框
        self.setFixedSize(900, 600)  # 从 800x500 增大到 900x600
        self.setStyleSheet("""
            QDialog {
                background-color: rgb(40, 44, 52);
                border-radius: 12px;
                font-size: 16px;  /* 增大默认字体 */
            }
        """)

        # 创建主布局
        main_layout = QHBoxLayout(self)
        main_layout.setContentsMargins(20, 20, 20, 20)
        main_layout.setSpacing(20)

        # 创建左侧信息区域
        left_frame = QFrame()
        left_frame.setStyleSheet("""
            QFrame {
                background-color: rgba(33, 37, 43, 180);
                border-radius: 10px;
                border: 1px solid rgba(255, 255, 255, 30);
            }
        """)
        left_layout = QVBoxLayout(left_frame)
        left_layout.setContentsMargins(20, 20, 20, 20)
        left_layout.setSpacing(15)

        # 标题
        title_label = QLabel("车辆详细信息")
        title_label.setStyleSheet("""
            QLabel {
                color: #00ccff;
                font-size: 20px;  /* 增大标题字体 */
                font-weight: bold;
                padding: 12px;
                background-color: rgba(0, 0, 0, 30);
                border-radius: 8px;
            }
        """)
        title_label.setAlignment(Qt.AlignCenter)
        left_layout.addWidget(title_label)

        # 车牌号
        plate_label = QLabel(f"车牌号: {self.vehicle_data[0] or '无车牌'}")
        plate_label.setStyleSheet("""
            QLabel {
                color: white;
                font-size: 18px;  /* 增大字体 */
                padding: 15px;  /* 增加内边距 */
                background-color: rgba(0, 0, 0, 30);
                border-radius: 6px;
                font-weight: bold;
            }
        """)
        plate_label.setMinimumHeight(60)  # 设置最小高度
        left_layout.addWidget(plate_label)

        # 路口序号
        road_id_label = QLabel(f"路口序号: {self.vehicle_data[1] or '未知'}")
        road_id_label.setStyleSheet("""
            QLabel {
                color: white;
                font-size: 18px;  /* 增大字体 */
                padding: 15px;  /* 增加内边距 */
                background-color: rgba(0, 0, 0, 30);
                border-radius: 6px;
                font-weight: bold;
            }
        """)
        road_id_label.setMinimumHeight(60)  # 设置最小高度
        left_layout.addWidget(road_id_label)

        # 路口名称
        road_name_label = QLabel(f"路口名称: {self.vehicle_data[2] or '未知'}")
        road_name_label.setStyleSheet("""
            QLabel {
                color: white;
                font-size: 18px;  /* 增大字体 */
                padding: 15px;  /* 增加内边距 */
                background-color: rgba(0, 0, 0, 30);
                border-radius: 6px;
                font-weight: bold;
            }
        """)
        road_name_label.setMinimumHeight(60)  # 设置最小高度
        left_layout.addWidget(road_name_label)

        # 驶入时间
        entry_time_label = QLabel(f"驶入时间: {self.vehicle_data[3] or '未知'}")
        entry_time_label.setStyleSheet("""
            QLabel {
                color: white;
                font-size: 18px;  /* 增大字体 */
                padding: 15px;  /* 增加内边距 */
                background-color: rgba(0, 0, 0, 30);
                border-radius: 6px;
                font-weight: bold;
            }
        """)
        entry_time_label.setMinimumHeight(60)  # 设置最小高度
        left_layout.addWidget(entry_time_label)

        # 驶出时间
        departure_time_label = QLabel(f"驶出时间: {self.vehicle_data[4] or '未离开'}")
        departure_time_label.setStyleSheet("""
            QLabel {
                color: white;
                font-size: 18px;  /* 增大字体 */
                padding: 15px;  /* 增加内边距 */
                background-color: rgba(0, 0, 0, 30);
                border-radius: 6px;
                font-weight: bold;
            }
        """)
        departure_time_label.setMinimumHeight(60)  # 设置最小高度
        left_layout.addWidget(departure_time_label)

        # 车身颜色
        body_color_label = QLabel(f"车身颜色: {self.vehicle_data[5] or '未知'}")
        body_color_label.setStyleSheet("""
            QLabel {
                color: white;
                font-size: 18px;  /* 增大字体 */
                padding: 15px;  /* 增加内边距 */
                background-color: rgba(0, 0, 0, 30);
                border-radius: 6px;
                font-weight: bold;
            }
        """)
        body_color_label.setMinimumHeight(60)  # 设置最小高度
        left_layout.addWidget(body_color_label)

        # 车牌颜色
        plate_color_label = QLabel(f"车牌颜色: {self.vehicle_data[6] or '未知'}")
        plate_color_label.setStyleSheet("""
            QLabel {
                color: white;
                font-size: 18px;  /* 增大字体 */
                padding: 15px;  /* 增加内边距 */
                background-color: rgba(0, 0, 0, 30);
                border-radius: 6px;
                font-weight: bold;
            }
        """)
        plate_color_label.setMinimumHeight(60)  # 设置最小高度
        left_layout.addWidget(plate_color_label)

        # 车辆速度
        speed_label = QLabel(f"车辆速度: {self.vehicle_data[7] or '未知'} km/h")
        speed_label.setStyleSheet("""
            QLabel {
                color: white;
                font-size: 18px;  /* 增大字体 */
                padding: 15px;  /* 增加内边距 */
                background-color: rgba(0, 0, 0, 30);
                border-radius: 6px;
                font-weight: bold;
            }
        """)
        speed_label.setMinimumHeight(60)  # 设置最小高度
        left_layout.addWidget(speed_label)

        # 添加弹性空间
        left_layout.addStretch()

        # 创建右侧图片区域
        right_frame = QFrame()
        right_frame.setStyleSheet("""
            QFrame {
                background-color: rgba(33, 37, 43, 180);
                border-radius: 10px;
                border: 1px solid rgba(255, 255, 255, 30);
            }
        """)
        right_layout = QVBoxLayout(right_frame)
        right_layout.setContentsMargins(15, 15, 15, 15)
        right_layout.setSpacing(15)

        # 图片标题
        image_title = QLabel("车辆图片")
        image_title.setStyleSheet("""
            QLabel {
                color: #00ccff;
                font-size: 20px;  /* 增大字体 */
                font-weight: bold;
                padding: 12px;
                background-color: rgba(0, 0, 0, 30);
                border-radius: 8px;
            }
        """)
        image_title.setAlignment(Qt.AlignCenter)
        right_layout.addWidget(image_title)

        # 图片显示区域
        self.image_label = QLabel()
        self.image_label.setStyleSheet("""
            QLabel {
                background-color: rgba(0, 0, 0, 100);
                border-radius: 10px;
                border: 2px solid rgba(255, 255, 255, 30);
                min-height: 400px;  /* 增加最小高度 */
                font-size: 18px;  /* 增大字体 */
                color: white;
            }
        """)
        self.image_label.setAlignment(Qt.AlignCenter)
        self.image_label.setText("未找到车辆图片")
        right_layout.addWidget(self.image_label)

        # 加载并显示车辆图片
        self.load_vehicle_image()

        # 添加弹性空间
        right_layout.addStretch()

        # 添加到主布局
        main_layout.addWidget(left_frame, 1)
        main_layout.addWidget(right_frame, 1)

    def load_vehicle_image(self):
        """
        从数据库加载车辆图片并显示
        """
        try:
            print(f"尝试加载车辆图片，参数: {self.vehicle_data}")
            if not os.path.exists(self.db_path):
                print("数据库文件不存在")
                self.image_label.setText("数据库文件不存在")
                return

            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()

            # 查询车辆图片 - 使用更准确的查询条件
            query = """
                SELECT photo FROM vehicles 
                WHERE plateNumber = ? AND entryTime = ?
            """
            print(f"查询参数: 车牌号='{self.vehicle_data[0]}', 驶入时间='{self.vehicle_data[3]}'")

            cursor.execute(query, (self.vehicle_data[0], self.vehicle_data[3]))
            result = cursor.fetchone()
            conn.close()

            if result:
                print(f"查询结果: {len(result)} 列")
                photo_data = result[0]
                print(f"图片数据类型: {type(photo_data)}, 大小: {len(photo_data) if photo_data else 0}")

                if photo_data and isinstance(photo_data, bytes) and len(photo_data) > 0:
                    # 创建 QImage 并显示图片
                    image = QImage()
                    if image.loadFromData(QByteArray(photo_data)):  # 使用 QByteArray 包装数据
                        # 缩放图片以适应显示区域
                        pixmap = QPixmap.fromImage(image)
                        pixmap = pixmap.scaled(
                            300, 300,
                            Qt.KeepAspectRatio,
                            Qt.SmoothTransformation
                        )
                        self.image_label.setPixmap(pixmap)
                        self.image_label.setText("")
                        print("图片加载成功")
                    else:
                        print("无法从数据创建图片")
                        self.image_label.setText("图片数据无效")
                elif photo_data is None:
                    print("图片数据为空")
                    self.image_label.setText("未找到车辆图片")
                else:
                    print(f"图片数据异常: {type(photo_data)}")
                    self.image_label.setText("图片数据格式错误")
            else:
                print("未找到匹配的车辆记录")
                self.image_label.setText("未找到车辆图片")

        except Exception as e:
            print(f"加载车辆图片时出错: {e}")
            import traceback
            traceback.print_exc()
            self.image_label.setText("图片加载失败")
