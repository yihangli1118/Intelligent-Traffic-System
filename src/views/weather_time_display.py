# weather_time_display.py
from PyQt5.QtWidgets import QVBoxLayout, QWidget, QLabel, QHBoxLayout, QFrame, QProgressBar
from PyQt5.QtCore import QTimer, Qt
from PyQt5.QtGui import QFont, QColor
import datetime


class WeatherTimeDisplayManager:
    """
    时间天气显示管理器
    """

    def __init__(self, ui_form):
        self.ui = ui_form
        self.time_timer = None
        self.date_timer = None

        # 天气信息（模拟数据）
        self.weather_data = {
            "temperature": "25°C",
            "condition": "晴",
            "humidity": "60%",
            "wind": "3级"
        }

    def create_time_weather_display(self):
        """
        创建时间天气组件，时间分两行显示，天气分两行显示
        """
        # 创建时间天气显示容器
        time_weather_widget = QWidget()
        time_weather_widget.setStyleSheet("""
            QWidget {
                background-color: qlineargradient(x1: 0, y1: 0, x2: 1, y2: 1, 
                                                  stop: 0 #1e3c72, stop: 1 #2a5298);
                border-radius: 12px;
                padding: 12px;
                border: 1px solid rgba(255, 255, 255, 30);
            }
        """)

        # 创建主水平布局
        main_layout = QHBoxLayout(time_weather_widget)
        main_layout.setContentsMargins(15, 10, 15, 10)
        main_layout.setSpacing(20)

        # 创建时间显示区域
        time_frame = QWidget()
        time_frame.setStyleSheet("""
            QWidget {
                background-color: rgba(0, 0, 0, 60);
                border-radius: 8px;
                padding: 8px 12px;
                border: 1px solid rgba(255, 255, 255, 20);
            }
        """)
        time_layout = QVBoxLayout(time_frame)
        time_layout.setContentsMargins(8, 5, 8, 5)
        time_layout.setSpacing(5)

        # 日期显示标签（年月日星期）
        self.date_label = QLabel()
        date_font = QFont()
        date_font.setFamily("Microsoft YaHei UI")
        date_font.setPointSize(9)
        date_font.setBold(True)
        self.date_label.setFont(date_font)
        self.date_label.setStyleSheet("""
            color: #aaffff;
            background-color: rgba(0, 0, 0, 30);
            border-radius: 4px;
            padding: 2px;
        """)
        self.date_label.setAlignment(Qt.AlignCenter)

        # 时间显示标签
        self.time_label = QLabel()
        time_font = QFont()
        time_font.setFamily("Microsoft YaHei UI")
        time_font.setPointSize(14)
        time_font.setBold(True)
        self.time_label.setFont(time_font)
        self.time_label.setStyleSheet("""
            color: white;
            background-color: rgba(0, 0, 0, 30);
            border-radius: 4px;
            padding: 3px;
        """)
        self.time_label.setAlignment(Qt.AlignCenter)

        time_layout.addWidget(self.date_label)
        time_layout.addWidget(self.time_label)

        # 创建天气显示区域
        weather_frame = QWidget()
        weather_frame.setStyleSheet("""
            QWidget {
                background-color: rgba(0, 0, 0, 60);
                border-radius: 8px;
                padding: 8px 12px;
                border: 1px solid rgba(255, 255, 255, 20);
            }
        """)
        weather_layout = QVBoxLayout(weather_frame)
        weather_layout.setContentsMargins(8, 5, 8, 5)
        weather_layout.setSpacing(5)

        # 天气标题
        weather_title = QLabel("天气信息")
        weather_title_font = QFont()
        weather_title_font.setFamily("Microsoft YaHei UI")
        weather_title_font.setPointSize(9)
        weather_title_font.setBold(True)
        weather_title.setFont(weather_title_font)
        weather_title.setStyleSheet("""
            color: #aaffff;
            background-color: rgba(0, 0, 0, 30);
            border-radius: 4px;
            padding: 2px;
        """)
        weather_title.setAlignment(Qt.AlignCenter)

        # 天气详情
        weather_detail = QLabel(f"{self.weather_data['temperature']} {self.weather_data['condition']}")
        weather_detail_font = QFont()
        weather_detail_font.setFamily("Microsoft YaHei UI")
        weather_detail_font.setPointSize(12)
        weather_detail_font.setBold(True)
        weather_detail.setFont(weather_detail_font)
        weather_detail.setStyleSheet("""
            color: white;
            background-color: rgba(0, 0, 0, 30);
            border-radius: 4px;
            padding: 3px;
        """)
        weather_detail.setAlignment(Qt.AlignCenter)

        weather_layout.addWidget(weather_title)
        weather_layout.addWidget(weather_detail)

        # 添加到主布局
        main_layout.addWidget(time_frame)
        main_layout.addWidget(weather_frame)

        # 初始化时间显示
        self.update_datetime_display()

        # 设置定时器更新时间
        self.setup_time_timers()

        return time_weather_widget

    def create_congestion_progress_bar(self):
        """
        创建拥堵程度进度条
        """
        # 创建进度条容器
        progress_container = QWidget()
        progress_container.setStyleSheet("""
            QWidget {
                background-color: qlineargradient(x1: 0, y1: 0, x2: 1, y2: 1, 
                                                  stop: 0 #2c3e50, stop: 1 #4a6491);
                border-radius: 12px;
                padding: 10px;
                border: 1px solid rgba(255, 255, 255, 30);
            }
        """)

        # 创建垂直布局
        layout = QVBoxLayout(progress_container)
        layout.setContentsMargins(12, 8, 12, 8)
        layout.setSpacing(8)

        # 标题
        title_label = QLabel("当前拥堵等级")
        title_font = QFont()
        title_font.setFamily("Microsoft YaHei UI")
        title_font.setPointSize(10)
        title_font.setBold(True)
        title_label.setFont(title_font)
        title_label.setStyleSheet("""
            color: #00ccff;
            background-color: rgba(0, 0, 0, 40);
            border-radius: 6px;
            padding: 4px;
        """)
        title_label.setAlignment(Qt.AlignCenter)

        # 进度条
        self.congestion_progress = QProgressBar()
        self.congestion_progress.setRange(0, 100)  # 设置范围为0-100%
        self.congestion_progress.setValue(10)  # 默认值为90% (对应等级9)
        self.congestion_progress.setTextVisible(True)
        self.congestion_progress.setFormat("拥堵等级 1/10")
        self.congestion_progress.setStyleSheet("""
            QProgressBar {
                border: 2px solid rgba(255, 255, 255, 50);
                border-radius: 8px;
                background-color: rgba(0, 0, 0, 80);
                text-align: center;
                color: white;
                font-size: 10pt;
                font-weight: bold;
                height: 24px;
            }

            QProgressBar::chunk {
                background-color: #ff0000; /* 默认红色 */
                border-radius: 6px;
                border: 1px solid rgba(255, 255, 255, 80);
            }
        """)

        # 添加到布局
        layout.addWidget(title_label)
        layout.addWidget(self.congestion_progress)

        return progress_container

    def update_congestion_progress(self, level):
        """
        根据拥堵等级更新进度条填充区域和颜色
        1-2: 绿色 (#00aa00)
        3-4: 浅绿 (#aaff00)
        5-6: 黄色 (#ffff00)
        7-8: 橙色 (#ffaa00)
        9-10: 红色 (#ff0000)
        """
        if not hasattr(self, 'congestion_progress'):
            return

        # 计算填充百分比 (等级 * 10%)
        percentage = level * 10
        self.congestion_progress.setValue(percentage)

        # 更新显示文本
        self.congestion_progress.setFormat(f"拥堵等级 {level}/10")

        # 根据等级设置颜色
        if 1 <= level <= 2:
            color = "#00aa00"  # 绿色
        elif 3 <= level <= 4:
            color = "#aaff00"  # 浅绿
        elif 5 <= level <= 6:
            color = "#ffff00"  # 黄色
        elif 7 <= level <= 8:
            color = "#ffaa00"  # 橙色
        elif 9 <= level <= 10:
            color = "#ff0000"  # 红色
        else:
            color = "#00aa00"  # 默认绿色

        # 更新进度条样式
        self.congestion_progress.setStyleSheet(f"""
            QProgressBar {{
                border: 1px solid rgb(60, 64, 72);
                border-radius: 5px;
                background-color: rgb(40, 44, 52);
                text-align: center;
                color: white;
                font-size: 8pt;
                font-weight: bold;
            }}

            QProgressBar::chunk {{
                background-color: {color};
                border-radius: 4px;
            }}
        """)

    def setup_time_timers(self):
        """
        设置时间更新定时器
        """
        # 创建时间更新定时器（每秒更新）
        self.time_timer = QTimer()
        self.time_timer.timeout.connect(self.update_datetime_display)
        self.time_timer.start(1000)  # 每秒更新一次

    def update_datetime_display(self):
        """
        更新日期时间显示
        """
        if hasattr(self, 'date_label') and hasattr(self, 'time_label'):
            # 获取当前日期时间
            now = datetime.datetime.now()
            # 日期格式：2023年12月25日 星期一
            date_str = now.strftime("%Y年%m月%d日 %A")
            # 时间格式：14:30:25
            time_str = now.strftime("%H:%M:%S")

            self.date_label.setText(date_str)
            self.time_label.setText(time_str)

    def setup_right_content_layout(self):
        """
        设置右侧内容区域布局
        将时间天气组件放置在 right_content 的最顶端
        """
        # 创建时间天气组件
        time_weather_widget = self.create_time_weather_display()

        # 创建拥堵程度进度条
        congestion_widget = self.create_congestion_progress_bar()

        # 更新进度条显示（示例等级为9）
        self.update_congestion_progress(1)

        # 创建一个新的垂直布局作为 right_content 的主布局
        main_layout = QVBoxLayout(self.ui.right_content)
        main_layout.setContentsMargins(15, 15, 15, 15)
        main_layout.setSpacing(15)

        # 先添加时间天气组件到顶部
        main_layout.addWidget(time_weather_widget)

        # 添加拥堵程度进度条
        main_layout.addWidget(congestion_widget)

        # 然后添加原有的 widget1（包含 right_under 布局）
        main_layout.addWidget(self.ui.widget1)

        # 添加弹性空间
        main_layout.addStretch()

    def stop_timers(self):
        """
        停止所有定时器
        """
        if self.time_timer and self.time_timer.isActive():
            self.time_timer.stop()
