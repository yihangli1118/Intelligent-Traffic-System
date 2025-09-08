# violation_table.py
from PyQt5.QtWidgets import QTableWidget, QTableWidgetItem, QHeaderView, QVBoxLayout, QWidget, QPushButton, QHBoxLayout, \
    QFrame
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QColor, QFont


class ViolationTableManager:
    """
    违规信息表格管理器
    """

    def __init__(self, ui_form):
        self.ui = ui_form
        self.table = None

    def create_violation_table(self):
        """
        创建违规信息表格
        """
        # 创建表格控件
        self.table = QTableWidget()

        # 设置表格行列
        self.table.setColumnCount(6)  # 增加到6列
        self.table.setRowCount(0)

        # 设置表头（按新顺序）
        self.table.setHorizontalHeaderLabels(['车牌号', '违规地点', '违规时间', '违规行为', '审核状态', '查看详情'])

        # 设置表格属性
        self.table.setEditTriggers(QTableWidget.NoEditTriggers)  # 只读
        self.table.setSelectionBehavior(QTableWidget.SelectRows)  # 整行选择
        self.table.verticalHeader().setVisible(False)  # 隐藏行号

        # 增大行高
        self.table.verticalHeader().setDefaultSectionSize(40)

        # 设置列宽自适应策略
        header = self.table.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.ResizeToContents)  # 车牌号列自适应内容
        header.setSectionResizeMode(1, QHeaderView.ResizeToContents)  # 违规地点列自适应内容
        header.setSectionResizeMode(2, QHeaderView.ResizeToContents)  # 违规时间列自适应内容
        header.setSectionResizeMode(3, QHeaderView.ResizeToContents)  # 违规行为列自适应内容
        header.setSectionResizeMode(4, QHeaderView.ResizeToContents)  # 审核状态列自适应内容
        header.setSectionResizeMode(5, QHeaderView.Fixed)  # 查看详情列固定宽度

        # 设置查看详情列的宽度
        self.table.setColumnWidth(5, 100)

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
        self.table.setFixedSize(760, 560)  # 调整尺寸以适应新布局

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

        # 更新示例数据，包含新增的违规地点和违规时间
        sample_data = [
            ("京A12345", "中山路与解放路交叉口", "2023-10-01 08:30:15", "闯红灯", "待审核", ""),
            ("沪B67890", "南京东路", "2023-10-01 09:15:20", "不按车道行驶", "已审核", ""),
            ("粤C11111", "人民广场", "2023-10-01 10:00:10", "违章变道", "待审核", ""),
            ("川D22222", "淮海中路", "2023-10-01 11:30:00", "逆行", "已审核", ""),
            ("浙E33333", "徐家汇路口", "2023-10-01 12:15:30", "压(实)线", "待审核", ""),
            ("苏F44444", "外滩隧道", "2023-10-01 13:45:25", "超速", "已审核", "")
        ]

        # 清除现有内容
        self.table.clearContents()

        # 添加数据
        for row, (plate, location, time, violation, status, _) in enumerate(sample_data):
            # 添加数据
            self.table.setItem(row, 0, QTableWidgetItem(plate))
            self.table.setItem(row, 1, QTableWidgetItem(location))
            self.table.setItem(row, 2, QTableWidgetItem(time))
            self.table.setItem(row, 3, QTableWidgetItem(violation))
            self.table.setItem(row, 4, QTableWidgetItem(status))

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
            # detail_button.clicked.connect(lambda: self.show_violation_details(plate, violation, status))

            # 将按钮添加到表格中
            self.table.setCellWidget(row, 5, detail_button)

            # 设置居中对齐
            for col in range(5):  # 更新为5列
                item = self.table.item(row, col)
                if item:
                    item.setTextAlignment(Qt.AlignCenter)
                    item.setForeground(QColor(255, 255, 255))

            # 设置审核状态列的颜色
            status_item = self.table.item(row, 4)  # 更新为第4列
            if status_item:
                if status == "待审核":
                    status_item.setForeground(QColor(255, 215, 0))  # 金色
                elif status == "已审核":
                    status_item.setForeground(QColor(0, 255, 0))  # 绿色

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

        return layout_container

    def clear_table_data(self):
        """
        清空表格数据
        """
        if self.table:
            # 清除内容但保持行数，确保表格外观一致
            self.table.clearContents()
            self.table.setRowCount(15)  # 保持15行

    def show_violation_details(self, plate, violation, status):
        """
        显示违规详情（可选功能）
        """
        print(f"查看违规详情: 车牌号={plate}, 违规行为={violation}, 状态={status}")


class ViolationTableLayout:
    """
    违规信息表格布局管理器
    负责将违规信息表格插入到 violation_query 下方，并与之垂直分布
    """

    def __init__(self, ui_form):
        self.ui = ui_form
        self.table_manager = ViolationTableManager(ui_form)
        self.layout_container = None

    def setup_layout(self):
        """
        设置违规查询页面的垂直布局
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

        # 创建并添加违规信息表格
        table = self.table_manager.create_violation_table()
        main_layout.addWidget(table)

        # 添加弹性空间
        main_layout.addStretch()

        return self.layout_container

    def update_table_data(self):
        """
        更新表格数据
        """
        self.table_manager.add_sample_data()

    def clear_table(self):
        """
        清空表格数据
        """
        self.table_manager.clear_table_data()
