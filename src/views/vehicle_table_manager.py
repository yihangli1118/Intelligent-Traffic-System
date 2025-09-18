# vehicle_table_manager.py
from PyQt5.QtWidgets import QTableWidget, QTableWidgetItem, QHeaderView, QVBoxLayout, QWidget
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QColor


class VehicleTableManager:
    """
    车辆信息表格管理器
    """

    def __init__(self, ui_form):
        self.ui = ui_form
        self.table = None
        self.db_path = "utils/traffic.db"  # 数据库路径
        self.current_row = 0  # 当前已加载的数据行数
        self.page_size = 20  # 每页加载的数据量

    def create_vehicle_table(self, min_height=120):
        """
        创建车辆信息表格
        :param min_height: 表格最小高度，默认120像素
        """
        # 创建表格控件
        self.table = QTableWidget()

        # 设置表格行列
        self.table.setColumnCount(3)
        self.table.setRowCount(20)

        # 设置表头
        self.table.setHorizontalHeaderLabels(['车牌号', '驶入时间', '驶出时间'])

        # 设置表格属性
        self.table.setEditTriggers(QTableWidget.NoEditTriggers)  # 只读
        self.table.setSelectionBehavior(QTableWidget.SelectRows)  # 整行选择
        self.table.verticalHeader().setVisible(False)  # 隐藏行号

        # 设置垂直滚动条始终显示
        self.table.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOn)

        # 增大行高
        self.table.verticalHeader().setDefaultSectionSize(40)

        # 设置列宽自适应策略
        header = self.table.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.ResizeToContents)  # 车牌号列自适应内容
        header.setSectionResizeMode(1, QHeaderView.ResizeToContents)  # 驶入时间列自适应内容
        header.setSectionResizeMode(2, QHeaderView.ResizeToContents)  # 驶出时间列自适应内容

        # 设置第一列（车牌号）的固定宽度为120像素
        self.table.setColumnWidth(0, 120)

        # 设置列宽自适应策略 - 修改为Stretch模式以充分利用空间
        # header = self.table.horizontalHeader()
        # header.setSectionResizeMode(0, QHeaderView.Stretch)  # 车牌号列拉伸
        # header.setSectionResizeMode(1, QHeaderView.Stretch)  # 驶入时间列拉伸
        # header.setSectionResizeMode(2, QHeaderView.Stretch)  # 驶出时间列拉伸

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
                width: 10px;              /* 宽度减半 (原15px) */
                border-radius: 3px;      /* 圆角调整 */
                margin: 0px 0px 0px 0px;
            }

            /* 滚动条滑块 */
            QScrollBar::handle:vertical {
                background-color: rgb(0, 170, 255);
                border-radius: 3px;      /* 圆角调整 */
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
                height: 10px;             /* 高度减半 (原15px) */
                border-top-left-radius: 3px;
                border-top-right-radius: 3px;
                subcontrol-position: top;
                subcontrol-origin: margin;
            }

            /* 向下按钮 */
            QScrollBar::add-line:vertical {
                border: none;
                background-color: rgb(30, 34, 40);
                height: 10px;             /* 高度减半 (原15px) */
                border-bottom-left-radius: 3px;
                border-bottom-right-radius: 3px;
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
                height: 10px;             /* 高度减半 (原15px) */
                border-radius: 3px;      /* 圆角调整 */
                margin: 0px 0px 0px 0px;
            }

            /* 水平滚动条滑块 */
            QScrollBar::handle:horizontal {
                background-color: rgb(0, 170, 255);
                border-radius: 2px;      /* 圆角调整 */
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
                width: 10px;              /* 宽度减半 (原15px) */
                border-top-left-radius: 3px;
                border-bottom-left-radius: 3px;
                subcontrol-position: left;
                subcontrol-origin: margin;
            }

            /* 右按钮 */
            QScrollBar::add-line:horizontal {
                border: none;
                background-color: rgb(30, 34, 40);
                width: 10px;              /* 宽度减半 (原15px) */
                border-top-right-radius: 3px;
                border-bottom-right-radius: 3px;
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
        # self.table.setFixedSize(410, 760)  # 调整尺寸以适应新布局
        self.table.setFixedSize(550, 800)  # 调整尺寸以适应新布局

        # 添加初始数据
        self.load_initial_data()

        return self.table

        # # 设置最小行数，确保空表格也有相同的外观
        # self.table.setRowCount(20)  # 设置20行空行
        # self.table.clearContents()  # 清除内容但保持行数
        #
        # # 连接垂直滚动条的信号
        # self.table.verticalScrollBar().valueChanged.connect(self.on_vertical_scroll)
        #
        # # 添加初始数据
        # self.load_initial_data()
        #
        # # # 添加示例数据
        # # self.add_sample_data()
        #
        # return self.table

    def add_sample_data(self):
        """
        添加示例数据到表格
        """
        if not self.table:
            return

        sample_data = [
            ("京A12345", "2023-10-01 08:30", "2023-10-01 09:45"),
            ("沪B67890", "2023-10-01 09:15", "2023-10-01 10:30"),
            ("粤C11111", "2023-10-01 10:00", "2023-10-01 11:20"),
            ("川D22222", "2023-10-01 11:30", "2023-10-01 12:45"),
            ("浙E33333", "2023-10-01 12:15", "2023-10-01 13:30")
        ]

        # 清除现有内容
        self.table.clearContents()

        for row, (plate, enter_time, exit_time) in enumerate(sample_data):
            self.table.setItem(row, 0, QTableWidgetItem(plate))
            self.table.setItem(row, 1, QTableWidgetItem(enter_time))
            self.table.setItem(row, 2, QTableWidgetItem(exit_time))

            # 设置居中对齐
            for col in range(3):
                item = self.table.item(row, col)
                if item:
                    item.setTextAlignment(Qt.AlignCenter)
                    item.setForeground(QColor(255, 255, 255))

    def add_vehicle_record(self, plate, enter_time, exit_time):
        """
        添加单条车辆记录
        """
        if not self.table:
            return

        #row = self.table.rowCount()
        # self.table.insertRow(row)
        self.table.insertRow(0)

        # 添加数据
        self.table.setItem(0, 0, QTableWidgetItem(plate))
        self.table.setItem(0, 1, QTableWidgetItem(enter_time))
        self.table.setItem(0, 2, QTableWidgetItem(exit_time))

        # 设置居中对齐
        # for col in range(3):
        #     item = self.table.item(row, col)
        #     if item:
        #         item.setTextAlignment(Qt.AlignCenter)
        for col in range(3):
            item = self.table.item(0, col)
            if item:
                item.setTextAlignment(Qt.AlignCenter)
                item.setForeground(QColor(255, 255, 255))

            # 如果行数超过20行，删除最后一行以保持表格大小
        if self.table.rowCount() > 20:
            self.table.removeRow(self.table.rowCount() - 1)

    def setup_left_content_layout(self, table_min_height=120):
        """
        重新设置 left_content 的布局
        在 left_top 下方插入表格，并与 left_top 进行垂直布局
        :param table_min_height: 表格最小高度，默认120像素
        """
        # 创建新的垂直布局
        main_layout = QVBoxLayout(self.ui.left_content)
        # main_layout.setContentsMargins(10, 10, 10, 10)
        main_layout.setContentsMargins(25, 0, 10, 10)
        main_layout.setSpacing(0)

        # 添加 left_top 到布局中
        main_layout.addWidget(self.ui.left_top)

        # 创建并添加车辆信息表格，设置最小高度
        self.create_vehicle_table(min_height=table_min_height)
        main_layout.addWidget(self.table)

        return main_layout

    def clear_table_data(self):
        """
        清空表格数据
        """
        if self.table:
            # 清除内容但保持行数，确保表格外观一致
            self.table.clearContents()
            self.table.setRowCount(20)  # 保持20行
            # self.current_row = 0

    def set_table_min_height(self, min_height):
        """
        动态设置表格最小高度
        :param min_height: 最小高度值（像素）
        """
        if self.table:
            self.table.setMinimumHeight(min_height)

    # def load_initial_data(self):
    #     """
    #     从数据库加载初始数据
    #     """
    #     self.current_row = 0
    #     self.load_data_batch()

    def load_initial_data(self):
        """
        从数据库加载初始数据
        """
        import sqlite3
        import os

        if not os.path.exists(self.db_path):
            print("数据库文件不存在")
            return

        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()

            # 查询有车牌号的车辆信息，按驶入时间倒序排列，限制20条记录
            query = """
                SELECT plateNumber, entryTime, departureTime
                FROM vehicles
                WHERE plateNumber IS NOT NULL AND plateNumber != '' AND plateNumber != '对向来车'
                ORDER BY entryTime DESC
                LIMIT 20
            """

            cursor.execute(query)
            rows = cursor.fetchall()

            # 清空现有内容
            self.table.clearContents()

            # 填充表格
            for i, row in enumerate(rows):
                # 添加数据
                self.table.setItem(i, 0, QTableWidgetItem(row[0] or "无车牌"))  # 车牌号
                self.table.setItem(i, 1, QTableWidgetItem(row[1] or "未知"))  # 驶入时间
                exit_time_display = row[2] if row[2] else "未离开"
                self.table.setItem(i, 2, QTableWidgetItem(row[2] or "未离开"))  # 驶出时间

                # 设置居中对齐
                for col in range(3):
                    item = self.table.item(i, col)
                    if item:
                        item.setTextAlignment(Qt.AlignCenter)
                        item.setForeground(QColor(255, 255, 255))

            conn.close()

        except Exception as e:
            print(f"加载数据时出错: {e}")

    # def load_data_batch(self):
    #     """
    #     从数据库加载一批数据
    #     """
    #     import sqlite3
    #     import os
    #
    #     if not os.path.exists(self.db_path):
    #         print("数据库文件不存在")
    #         return
    #
    #     try:
    #         conn = sqlite3.connect(self.db_path)
    #         cursor = conn.cursor()
    #
    #         # 查询有车牌号的车辆信息
    #         query = """
    #             SELECT plateNumber, entryTime, departureTime
    #             FROM vehicles
    #             WHERE plateNumber IS NOT NULL AND plateNumber != ''
    #             ORDER BY entryTime DESC
    #             LIMIT ? OFFSET ?
    #         """
    #
    #         cursor.execute(query, (self.page_size, self.current_row))
    #         rows = cursor.fetchall()
    #
    #         # 填充表格
    #         for i, row in enumerate(rows):
    #             row_index = self.current_row + i
    #
    #             # 确保有足够的行
    #             if row_index >= self.table.rowCount():
    #                 self.table.setRowCount(row_index + 1)
    #
    #             # 添加数据
    #             self.table.setItem(row_index, 0, QTableWidgetItem(row[0] or "无车牌"))  # 车牌号
    #             self.table.setItem(row_index, 1, QTableWidgetItem(row[1] or "未知"))  # 驶入时间
    #             self.table.setItem(row_index, 2, QTableWidgetItem(row[2] or "未离开"))  # 驶出时间
    #
    #             # 设置居中对齐
    #             for col in range(3):
    #                 item = self.table.item(row_index, col)
    #                 if item:
    #                     item.setTextAlignment(Qt.AlignCenter)
    #                     item.setForeground(QColor(255, 255, 255))
    #
    #         self.current_row += len(rows)
    #         conn.close()
    #
    #     except Exception as e:
    #         print(f"加载数据时出错: {e}")

    # def on_vertical_scroll(self, value):
    #     """
    #     垂直滚动条滚动事件处理
    #     """
    #     # 当滚动到接近底部时加载更多数据
    #     if value >= self.table.verticalScrollBar().maximum() * 0.8:
    #         self.load_data_batch()

    def get_latest_vehicles(self, limit: int = 20) -> list:
        """
        获取最新的车辆记录
        :param limit: 返回记录数量限制
        :return: 车辆记录列表
        """
        try:
            import sqlite3
            import os

            if not os.path.exists(self.db_path):
                print("数据库文件不存在")
                return []
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()

            cursor.execute('''
                SELECT plateNumber, entryTime, departureTime
                FROM vehicles
                WHERE plateNumber IS NOT NULL AND plateNumber != '' AND plateNumber != '对向来车'
                ORDER BY entryTime DESC
                LIMIT ?
            ''', (limit,))

            rows = cursor.fetchall()
            conn.close()

            # 转换为字典列表方便使用
            vehicles = []
            for row in rows:
                vehicles.append({
                    'plate_number': row[0],
                    'entry_time': row[1],
                    'departure_time': row[2] if row[2] else "未离开"
                })

            return vehicles
        except Exception as e:
            print(f"获取最新车辆记录时出错: {e}")
            import traceback
            traceback.print_exc()
            return []



