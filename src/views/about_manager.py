# about_manager.py
from PyQt5.QtWidgets import QVBoxLayout, QTextEdit, QLabel, QScrollArea, QWidget
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont


class AboutManager:
    """
    管理"关于我们"页面的内容显示
    """

    def __init__(self, ui):
        self.ui = ui
        self.setup_about_page()

    def setup_about_page(self):
        """
        设置关于我们页面的布局和内容
        """
        # 清空page_3原有的内容
        self.clear_layout(self.ui.page_3.layout())

        # 创建主布局
        main_layout = QVBoxLayout(self.ui.page_3)
        main_layout.setContentsMargins(50, 30, 50, 30)
        main_layout.setSpacing(20)

        # 标题
        title_label = QLabel("关于我们")
        title_font = QFont()
        title_font.setFamily("Microsoft YaHei UI")
        title_font.setPointSize(24)
        title_font.setBold(True)
        title_label.setFont(title_font)
        title_label.setStyleSheet("""
            color: rgb(0, 170, 255);
            margin-bottom: 20px;
        """)
        title_label.setAlignment(Qt.AlignCenter)
        main_layout.addWidget(title_label)

        # 创建滚动区域
        scroll_area = QScrollArea()
        scroll_area.setStyleSheet("""
            QScrollBar:vertical {
                border: none;
                border-radius:5px;
                width: 10px;
                background:rgba(153, 153, 153, 0.5);
            }
            QScrollBar::handle:vertical {
                border: none;
                border-radius:5px; 
                background-color: rgb(55, 156, 212);
            }
            QScrollBar::sub-line:vertical {
                border: none;
                height: 0px;
                subcontrol-position: top;
                subcontrol-origin: margin;
            }
            QScrollBar::add-line:vertical {
                border: none;
                height: 0px;
                subcontrol-position: bottom;
                subcontrol-origin: margin;
            }
            QScrollBar::up-arrow:vertical, QScrollBar::down-arrow:vertical {
                border:none;
                width: 0px;
                height: 0px;
            }
            QScrollBar::add-page:vertical, QScrollBar::sub-page:vertical {
                background: none;
            }

            QScrollBar:horizontal {
                border: none;
                border-radius:2px;
                height: 20px;
                background:rgba(153, 153, 153, 0.5);
                border-image: url(:/icon/tou.png);
            }
            QScrollBar::handle:horizontal {
                border: none;
                border-radius:2px; 
                background-color: rgb(55, 156, 212);
            }
            QScrollBar::sub-line:horizontal {
                border: none;
                width: 0px;
                subcontrol-position: left;
                subcontrol-origin: margin;
            }
            QScrollBar::add-line:horizontal {
                border: none;
                width: 0px;
                subcontrol-position: right;
                subcontrol-origin: margin;
            }
            QScrollBar::up-arrow:horizontal, QScrollBar::down-arrow:vertical {
                border:none;
                width: 0px;
                height: 0px;
            }
            QScrollBar::add-page:horizontal, QScrollBar::sub-page:vertical {
                background: none;
            }
        """)
        scroll_area.setWidgetResizable(True)
        scroll_area.setFrameShape(QScrollArea.NoFrame)

        # 创建内容widget
        content_widget = QWidget()
        content_widget.setStyleSheet("background-color: rgb(33, 37, 43);")
        scroll_area.setWidget(content_widget)

        # 创建内容布局
        content_layout = QVBoxLayout(content_widget)
        content_layout.setContentsMargins(20, 20, 20, 20)

        # 创建文本标签显示内容
        content_label = QLabel()
        content_label.setStyleSheet("""
            color: rgb(255, 255, 255);
            font-family: "Microsoft YaHei UI";
            font-size: 12pt;
            background-color: rgb(33, 37, 43);
        """)
        content_label.setWordWrap(True)
        content_label.setAlignment(Qt.AlignTop)

        # 设置关于我们内容
        about_content = """
<h2 style="color: rgb(0, 170, 255); text-align: center;">智能交通管理系统</h2>

<p>智能交通管理系统是一套集实时监控、数据分析、违规检测于一体的现代化交通管理解决方案。本系统利用先进的计算机视觉技术和大数据分析能力，为城市交通管理提供智能化支持。</p>

<h3 style="color: rgb(0, 170, 255);">核心功能</h3>
<ul>
<li><b>实时监控：</b>7x24小时不间断监控交通状况，实时捕捉道路信息</li>
<li><b>违规检测：</b>自动识别闯红灯、违章变道、逆行等交通违规行为</li>
<li><b>流量统计：</b>精确统计车流量数据，为交通规划提供科学依据</li>
<li><b>数据分析：</b>深度分析交通模式，预测拥堵趋势</li>
<li><b>报表生成：</b>自动生成各类交通统计报表，支持导出功能</li>
</ul>

<h3 style="color: rgb(0, 170, 255);">技术优势</h3>
<ul>
<li>采用先进的AI算法，识别准确率高达99%以上</li>
<li>支持多路视频同时处理，满足大规模部署需求</li>
<li>响应速度快，毫秒级违规检测与记录</li>
<li>友好的用户界面，操作简便直观</li>
<li>高可靠性设计，确保系统稳定运行</li>
</ul>

<h3 style="color: rgb(0, 170, 255);">应用场景</h3>
<p>本系统广泛应用于城市交通管理、高速公路监控、智能停车场、学校周边安全监控等场景，有效提升交通管理效率，降低交通事故发生率。</p>

<h3 style="color: rgb(0, 170, 255);">联系我们</h3>
<p>如果您有任何问题或建议，请通过以下方式联系我们：</p>
<ul>
<li>技术支持邮箱：support@traffic-system.com</li>
<li>客服热线：400-123-4567</li>
<li>官方网站：www.traffic-system.com</li>
</ul>

<p style="text-align: center; margin-top: 30px;">
<b>© 2025 智能交通管理系统 - 让城市交通更智慧</b>
</p>
"""
        content_label.setText(about_content)
        content_layout.addWidget(content_label)

        main_layout.addWidget(scroll_area)

        # 设置页面背景
        self.ui.page_3.setStyleSheet("""
            background-color: rgb(40, 44, 52);
        """)

    def clear_layout(self, layout):
        """
        清理布局中的所有控件
        """
        if layout is not None:
            while layout.count():
                child = layout.takeAt(0)
                if child.widget():
                    child.widget().deleteLater()
