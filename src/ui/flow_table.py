# flow_table.py
from PyQt5.QtWidgets import QTableWidget, QTableWidgetItem, QHeaderView, QVBoxLayout, QWidget, QPushButton, QHBoxLayout, \
    QFrame, QLabel
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QColor, QFont
from PyQt5 import QtGui

class FlowTableManager:
    """
    流量信息表格管理器
    """

    def __init__(self, ui_form):
        self.ui = ui_form
        self.table = None

    def create_flow_table(self):
        """
        创建流量信息表格
        表格有5列，表头按顺序为时间、地点、车流量、拥堵等级、查看详情
        """
        # 创建表格控件
        self.table = QTableWidget()

        # 设置表格行列
        self.table.setColumnCount(5)  # 增加到5列
        self.table.setRowCount(0)

        # 设置表头
        self.table.setHorizontalHeaderLabels(['时间', '地点', '车流量', '拥堵等级', '查看详情'])

        # 设置表格属性
        self.table.setEditTriggers(QTableWidget.NoEditTriggers)  # 只读
        self.table.setSelectionBehavior(QTableWidget.SelectRows)  # 整行选择
        self.table.verticalHeader().setVisible(False)  # 隐藏行号

        # 增大行高
        self.table.verticalHeader().setDefaultSectionSize(40)

        # 设置列宽自适应策略
        header = self.table.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.ResizeToContents)  # 时间列自适应内容
        header.setSectionResizeMode(1, QHeaderView.ResizeToContents)  # 地点列自适应内容
        header.setSectionResizeMode(2, QHeaderView.ResizeToContents)  # 车流量列自适应内容
        header.setSectionResizeMode(3, QHeaderView.ResizeToContents)  # 拥堵等级列自适应内容
        header.setSectionResizeMode(4, QHeaderView.Fixed)  # 查看详情列固定宽度

        # 设置查看详情列的宽度
        self.table.setColumnWidth(4, 100)

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
        self.table.setMinimumSize(620, 620)  # 调整尺寸以适应新布局

        # 设置最小行数，确保空表格也有相同的外观
        self.table.setRowCount(15)  # 设置15行空行
        self.table.clearContents()  # 清除内容但保持行数

        # 添加示例数据
        self.add_sample_data()

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
        在 label_query_flow 下方插入表格，并与 label_query_flow 垂直分布
        """
        # 创建新的垂直布局容器
        layout_container = QWidget(self.ui.frame_query_flow)
        layout_container.setGeometry(0, 0, 800, 721)
        layout_container.setStyleSheet("background-color: rgb(40, 44, 52);")

        # 创建垂直布局
        main_layout = QVBoxLayout(layout_container)
        main_layout.setContentsMargins(15, 15, 15, 15)
        main_layout.setSpacing(15)

        # 创建包含 label_query_flow 和按钮的容器，设置固定宽度与表格对齐
        header_container = QWidget()
        header_container.setFixedWidth(620)  # 与表格宽度一致
        header_container_layout = QHBoxLayout(header_container)
        header_container_layout.setContentsMargins(0, 0, 0, 0)
        header_container_layout.setSpacing(5)

        # 添加左侧空白（相当于2个字的距离）
        spacer = QLabel("  ")  # 两个空格字符
        spacer.setStyleSheet(
            "color: rgb(0, 170, 255); font-family: '汉仪雅酷黑X 85W'; font-size: 12pt; font-weight: bold;")
        header_container_layout.addWidget(spacer)

        # 添加原始的 label_query_flow
        header_container_layout.addWidget(self.ui.label_query_flow)

        # 添加弹性空间将内容推到左侧
        header_container_layout.addStretch()

        # 创建导出数据按钮，样式与 output_vio 一致
        self.output_flow = QPushButton("导出数据")
        self.output_flow.setMinimumSize(100, 30)
        self.output_flow.setMaximumSize(120, 30)
        self.output_flow.setStyleSheet("""
            QPushButton{
                background-color: rgb(40, 44, 52);
                border-radius: 5px;
                border: 2px solid #404758;
                padding: 5px;
                padding-left: 10px;
                color: #f8f8f2;
                font-size: 10pt;
            }

            /* 鼠标悬停 */
            QPushButton:hover{
                background-color: rgb(205, 205, 205);
            }

            /* 点击和按下 */
            QPushButton:pressed{
                background-color:rgb(33, 37, 43);    
            }
        """)

        # 设置图标
        icon = QtGui.QIcon()
        icon.addPixmap(QtGui.QPixmap(":/images/images/output_data.png"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.output_flow.setIcon(icon)

        header_container_layout.addWidget(self.output_flow)

        # 添加包含 label_query_flow 和按钮的容器到主布局中
        main_layout.addWidget(header_container)

        # 创建表格容器，使用与表格相同的宽度
        table_container = QWidget()
        table_container.setMinimumWidth(640)  # 与表格宽度一致
        table_container_layout = QHBoxLayout(table_container)
        table_container_layout.setContentsMargins(0, 0, 0, 0)
        table_container_layout.setSpacing(0)

        # 添加左侧空白（相当于2个字的距离）
        table_spacer = QLabel("  ")  # 两个空格字符
        table_spacer.setStyleSheet(
            "color: rgb(0, 170, 255); font-family: '汉仪雅酷黑X 85W'; font-size: 12pt; font-weight: bold;")
        table_container_layout.addWidget(table_spacer)

        # 创建并添加流量信息表格
        self.create_flow_table()

        # 将表格添加到容器中
        table_container_layout.addWidget(self.table)

        # 添加弹性空间将内容推到左侧
        table_container_layout.addStretch()

        # 将表格容器添加到主布局中
        main_layout.addWidget(table_container)

        # 添加弹性空间
        main_layout.addStretch()

        # 将容器添加到父级布局中
        parent_layout = QVBoxLayout(self.ui.frame_query_flow)
        parent_layout.setContentsMargins(0, 0, 0, 0)
        parent_layout.addWidget(layout_container)

        return layout_container

    def clear_table_data(self):
        """
        清空表格数据
        """
        if self.table:
            # 清除内容但保持行数，确保表格外观一致
            self.table.clearContents()
            self.table.setRowCount(15)  # 保持15行

    def show_flow_details(self, time, location, flow, congestion):
        """
        显示流量详情（可选功能）
        """
        print(f"查看流量详情: 时间={time}, 地点={location}, 车流量={flow}, 拥堵等级={congestion}")
