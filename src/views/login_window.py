# file: src/views/login_window.py
import sys
from PyQt5.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
                             QLabel, QLineEdit, QPushButton, QFrame, QMessageBox, QStackedWidget)
from PyQt5.QtCore import Qt, QTimer
from PyQt5.QtGui import QFont, QPixmap, QIcon

from views.stats import Ui_Form  # 导入stats界面的Ui_Form类
from views.main_window import MainWindow  # 只导入MainWindow

class LoginWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        # 设置窗口无边框
        self.setWindowFlags(Qt.FramelessWindowHint)

        self.ui = Ui_Form()  # 使用stats的界面模板
        self.ui.setupUi(self)

        # 设置窗口标题
        self.setWindowTitle("智能交通管理系统 - 登录")

        # 添加关闭回调属性
        self.close_callback = None

        # 隐藏不需要的界面元素
        self.hide_unnecessary_elements()

        # 设置背景图片
        self.setup_background()

        # 设置登录区域
        self.setup_login_area()

        from controllers.authController import AuthController
        self.auth_controller = AuthController(self)

        # 连接顶部按钮功能
        self.setup_top_buttons()

        # 模拟用户数据库（实际应用中应使用真实数据库）
        # self.users = {
        #     "1": "666",  # 修改管理员账号为1，密码为666
        #     "user": "666"
        # }

    def setup_top_buttons(self):
        """
        设置顶部按钮功能 - 登录界面的关闭按钮真正退出程序
        """
        # 连接关闭按钮到退出程序
        self.ui.closeAppBtn.clicked.connect(self.close_application)

        # 连接最大化/恢复按钮
        self.ui.maximizeRestoreAppBtn.clicked.connect(self.toggle_maximize)

        # 连接最小化按钮
        self.ui.minimizeAppBtn.clicked.connect(self.showMinimized)

    def close_application(self):
        """
        真正退出应用程序
        """
        # 如果有 WindowManager，通过它来退出应用
        if hasattr(self, 'window_manager') and self.window_manager:
            self.window_manager.quit_application()
        else:
            # 直接退出应用程序
            QApplication.quit()

    def toggle_maximize(self):
        """
        切换窗口最大化/恢复状态
        """
        if self.isMaximized():
            self.showNormal()
        else:
            self.showMaximized()

    def hide_unnecessary_elements(self):
        """
        隐藏不需要的界面元素
        """
        # 隐藏侧边栏
        self.ui.sideBar.hide()

        # 隐藏主内容区域中的stackedWidget
        self.ui.stackedWidget.hide()

        # 调整content的位置和大小以填满整个窗口
        self.ui.content.setGeometry(0, 0, 1330, 858)

        # 创建一个新的主内容区域
        self.main_content = QFrame(self.ui.content)
        self.main_content.setGeometry(0, 0, 1330, 808)  # 除去顶部50像素
        self.main_content.setObjectName("main_content")

        # 设置顶部栏标题
        self.ui.titleRightInfo.setText("智能交通管理系统 - 登录")

        # 隐藏顶栏的用户名和用户头像
        self.ui.user_name.hide()
        self.ui.user_pic.hide()

    def setup_background(self):
        """
        设置背景图片
        """
        # 设置背景图片
        self.main_content.setStyleSheet("""
            QFrame#main_content {
                background-image: url(:/images/images/background.jpg);
                background-position: center;
                background-repeat: no-repeat;
                background-size: cover;
            }
        """)

    def setup_login_area(self):
        """
        设置登录区域（放在右面）
        """
        # 创建登录区域容器（放在右面）
        self.login_container = QFrame(self.main_content)
        self.login_container.setGeometry(760, 100, 500, 600)  # 放在右面
        self.login_container.setStyleSheet("background-color: transparent;")

        # 创建堆叠窗口用于切换登录和注册界面
        self.stacked_widget = QStackedWidget(self.login_container)
        self.stacked_widget.setGeometry(0, 0, 500, 600)

        # 创建登录界面
        self.create_login_page()

        # 创建注册界面
        self.create_register_page()

    def create_login_page(self):
        """创建登录界面"""
        login_page = QWidget()
        login_page.setStyleSheet("background-color: transparent;")
        login_layout = QVBoxLayout(login_page)
        login_layout.setContentsMargins(0, 0, 0, 0)
        login_layout.setSpacing(0)

        # 登录表单容器
        login_form = QFrame()
        login_form.setStyleSheet("""
            QFrame {
                background-color: rgba(33, 37, 43, 0.85);
                border-radius: 15px;
                padding: 40px;
            }
        """)
        login_form.setFixedSize(460, 500)  # 增大表单尺寸

        form_layout = QVBoxLayout(login_form)
        form_layout.setSpacing(20)  # 减小间距

        # 标题
        title = QLabel("用户登录")
        title_font = QFont()
        title_font.setFamily("Microsoft YaHei UI")
        title_font.setPointSize(18)  # 调整标题字体大小
        title_font.setBold(True)
        title.setFont(title_font)
        title.setStyleSheet("color: rgb(0, 170, 255); background-color: transparent;")
        title.setAlignment(Qt.AlignCenter)
        title.setFixedHeight(40)  # 固定标题高度

        # 用户名输入
        self.username_input = QLineEdit()
        self.username_input.setPlaceholderText("请输入用户名")
        self.username_input.setStyleSheet("""
            QLineEdit {
                background-color: rgba(40, 44, 52, 0.8);
                border-radius: 8px;
                border: 2px solid #404758;
                padding: 12px 15px;  /* 调整内边距 */
                color: white;
                font-size: 12pt;
                font-family: "Microsoft YaHei UI";
            }
            QLineEdit:focus {
                border: 2px solid rgb(0, 170, 255);
            }
        """)
        self.username_input.setMinimumHeight(50)  # 增加输入框高度

        # 密码输入
        self.password_input = QLineEdit()
        self.password_input.setPlaceholderText("请输入密码")
        self.password_input.setEchoMode(QLineEdit.Password)
        self.password_input.setStyleSheet("""
            QLineEdit {
                background-color: rgba(40, 44, 52, 0.8);
                border-radius: 8px;
                border: 2px solid #404758;
                padding: 12px 15px;  /* 调整内边距 */
                color: white;
                font-size: 12pt;
                font-family: "Microsoft YaHei UI";
            }
            QLineEdit:focus {
                border: 2px solid rgb(0, 170, 255);
            }
        """)
        self.password_input.setMinimumHeight(50)

        # 登录按钮
        login_button = QPushButton("登录")
        login_button.setStyleSheet("""
            QPushButton {
                background-color: rgb(0, 170, 255);
                border-radius: 8px;
                padding: 12px;  /* 调整内边距 */
                color: white;
                font-size: 12pt;
                font-weight: bold;
                font-family: "Microsoft YaHei UI";
            }
            QPushButton:hover {
                background-color: rgb(0, 150, 230);
            }
            QPushButton:pressed {
                background-color: rgb(0, 130, 210);
            }
        """)
        login_button.setMinimumHeight(50)
        login_button.clicked.connect(self.login)

        # 注册链接
        register_layout = QHBoxLayout()
        register_label = QLabel("还没有账号?")
        register_label.setStyleSheet(
            "color: white; font-size: 10pt; font-family: 'Microsoft YaHei UI'; background-color: transparent;")
        register_label.setFixedHeight(20)  # 固定标签高度

        register_button = QPushButton("立即注册")
        register_button.setStyleSheet("""
            QPushButton {
                background-color: transparent;
                border: none;
                color: rgb(0, 170, 255);
                font-size: 10pt;
                text-decoration: underline;
                font-family: "Microsoft YaHei UI";
                padding: 2px 5px;
            }
            QPushButton:hover {
                color: rgb(0, 150, 230);
            }
        """)
        register_button.setCursor(Qt.PointingHandCursor)
        register_button.clicked.connect(self.show_register_page)
        register_button.setFixedHeight(25)  # 固定按钮高度

        register_layout.addStretch()
        register_layout.addWidget(register_label)
        register_layout.addWidget(register_button)
        register_layout.addStretch()

        # 添加控件到表单布局
        form_layout.addWidget(title)
        form_layout.addSpacing(20)  # 减小间距
        form_layout.addWidget(self.username_input)
        form_layout.addWidget(self.password_input)
        form_layout.addWidget(login_button)
        form_layout.addSpacing(15)  # 减小间距
        form_layout.addLayout(register_layout)
        form_layout.addStretch()

        # 将表单添加到登录页面布局并居中
        login_layout.addStretch()
        login_layout.addWidget(login_form, 0, Qt.AlignCenter)
        login_layout.addStretch()

        self.stacked_widget.addWidget(login_page)

    def create_register_page(self):
        """创建注册界面"""
        register_page = QWidget()
        register_page.setStyleSheet("background-color: transparent;")
        register_layout = QVBoxLayout(register_page)
        register_layout.setContentsMargins(0, 0, 0, 0)
        register_layout.setSpacing(0)

        # 注册表单容器
        register_form = QFrame()
        register_form.setStyleSheet("""
            QFrame {
                background-color: rgba(33, 37, 43, 0.85);
                border-radius: 15px;
                padding: 40px;
            }
        """)
        register_form.setFixedSize(460, 500)  # 增大表单尺寸

        form_layout = QVBoxLayout(register_form)
        form_layout.setSpacing(20)  # 减小间距

        # 标题
        title = QLabel("用户注册")
        title_font = QFont()
        title_font.setFamily("Microsoft YaHei UI")
        title_font.setPointSize(18)  # 调整标题字体大小
        title_font.setBold(True)
        title.setFont(title_font)
        title.setStyleSheet("color: rgb(0, 170, 255); background-color: transparent;")
        title.setAlignment(Qt.AlignCenter)
        title.setFixedHeight(40)  # 固定标题高度

        # 用户名输入
        self.reg_username_input = QLineEdit()
        self.reg_username_input.setPlaceholderText("请输入用户名")
        self.reg_username_input.setStyleSheet("""
            QLineEdit {
                background-color: rgba(40, 44, 52, 0.8);
                border-radius: 8px;
                border: 2px solid #404758;
                padding: 12px 15px;  /* 调整内边距 */
                color: white;
                font-size: 12pt;
                font-family: "Microsoft YaHei UI";
            }
            QLineEdit:focus {
                border: 2px solid rgb(0, 170, 255);
            }
        """)
        self.reg_username_input.setMinimumHeight(50)

        # 密码输入
        self.reg_password_input = QLineEdit()
        self.reg_password_input.setPlaceholderText("请输入密码")
        self.reg_password_input.setEchoMode(QLineEdit.Password)
        self.reg_password_input.setStyleSheet("""
            QLineEdit {
                background-color: rgba(40, 44, 52, 0.8);
                border-radius: 8px;
                border: 2px solid #404758;
                padding: 12px 15px;  /* 调整内边距 */
                color: white;
                font-size: 12pt;
                font-family: "Microsoft YaHei UI";
            }
            QLineEdit:focus {
                border: 2px solid rgb(0, 170, 255);
            }
        """)
        self.reg_password_input.setMinimumHeight(50)

        # 确认密码输入
        self.reg_confirm_password_input = QLineEdit()
        self.reg_confirm_password_input.setPlaceholderText("请确认密码")
        self.reg_confirm_password_input.setEchoMode(QLineEdit.Password)
        self.reg_confirm_password_input.setStyleSheet("""
            QLineEdit {
                background-color: rgba(40, 44, 52, 0.8);
                border-radius: 8px;
                border: 2px solid #404758;
                padding: 12px 15px;  /* 调整内边距 */
                color: white;
                font-size: 12pt;
                font-family: "Microsoft YaHei UI";
            }
            QLineEdit:focus {
                border: 2px solid rgb(0, 170, 255);
            }
        """)
        self.reg_confirm_password_input.setMinimumHeight(50)

        # 注册按钮
        register_button = QPushButton("注册")
        register_button.setStyleSheet("""
            QPushButton {
                background-color: rgb(0, 170, 255);
                border-radius: 8px;
                padding: 12px;  /* 调整内边距 */
                color: white;
                font-size: 12pt;
                font-weight: bold;
                font-family: "Microsoft YaHei UI";
            }
            QPushButton:hover {
                background-color: rgb(0, 150, 230);
            }
            QPushButton:pressed {
                background-color: rgb(0, 130, 210);
            }
        """)
        register_button.setMinimumHeight(50)
        register_button.clicked.connect(self.register)

        # 返回登录链接
        login_layout = QHBoxLayout()
        login_label = QLabel("已有账号?")
        login_label.setStyleSheet(
            "color: white; font-size: 10pt; font-family: 'Microsoft YaHei UI'; background-color: transparent;")
        login_label.setFixedHeight(20)  # 固定标签高度

        login_button = QPushButton("立即登录")
        login_button.setStyleSheet("""
            QPushButton {
                background-color: transparent;
                border: none;
                color: rgb(0, 170, 255);
                font-size: 10pt;
                text-decoration: underline;
                font-family: "Microsoft YaHei UI";
                padding: 2px 5px;
            }
            QPushButton:hover {
                color: rgb(0, 150, 230);
            }
        """)
        login_button.setCursor(Qt.PointingHandCursor)
        login_button.clicked.connect(self.show_login_page)
        login_button.setFixedHeight(25)  # 固定按钮高度

        login_layout.addStretch()
        login_layout.addWidget(login_label)
        login_layout.addWidget(login_button)
        login_layout.addStretch()

        # 添加控件到表单布局
        form_layout.addWidget(title)
        form_layout.addSpacing(20)  # 减小间距
        form_layout.addWidget(self.reg_username_input)
        form_layout.addWidget(self.reg_password_input)
        form_layout.addWidget(self.reg_confirm_password_input)
        form_layout.addWidget(register_button)
        form_layout.addSpacing(15)  # 减小间距
        form_layout.addLayout(login_layout)
        form_layout.addStretch()

        # 将表单添加到注册页面布局并居中
        register_layout.addStretch()
        register_layout.addWidget(register_form, 0, Qt.AlignCenter)
        register_layout.addStretch()

        self.stacked_widget.addWidget(register_page)

    def show_login_page(self):
        """显示登录页面"""
        self.stacked_widget.setCurrentIndex(0)

    def show_register_page(self):
        """显示注册页面"""
        self.stacked_widget.setCurrentIndex(1)

    def login(self):
        """处理登录逻辑"""
        username = self.username_input.text().strip()
        password = self.password_input.text().strip()

        # 使用控制器处理登录
        self.auth_controller.handle_login(username, password)

        # if not username or not password:
        #     QMessageBox.warning(self, "登录失败", "请输入用户名和密码！")
        #     return
        #
        # if username in self.users and self.users[username] == password:
        #     # 登录成功后显示1秒提示，然后立即打开主程序界面
        #     self.show_success_message(f"欢迎，{username}！")
        #     # 1秒后打开主程序界面
        #     QTimer.singleShot(1000, self.open_main_window)
        # else:
        #     QMessageBox.warning(self, "登录失败", "用户名或密码错误！")

    def show_success_message(self, message):
        """显示成功消息1秒后消失"""
        # 创建一个临时的消息标签
        msg_label = QLabel(message)
        msg_label.setStyleSheet("""
            QLabel {
                background-color: rgba(0, 170, 255, 0.9);
                color: white;
                padding: 15px;
                border-radius: 8px;
                font-size: 14pt;
                font-weight: bold;
                font-family: "Microsoft YaHei UI";
            }
        """)
        msg_label.setAlignment(Qt.AlignCenter)

        # 创建布局来居中显示消息
        msg_layout = QVBoxLayout()
        msg_layout.addStretch()
        msg_layout.addWidget(msg_label)
        msg_layout.addStretch()

        # 创建一个widget来容纳消息
        msg_widget = QWidget()
        msg_widget.setLayout(msg_layout)
        msg_widget.setStyleSheet("background-color: transparent;")

        # 将消息widget添加到主窗口中央
        layout = QVBoxLayout(self.main_content)
        layout.addWidget(msg_widget, 0, Qt.AlignCenter)

        # 1秒后移除消息
        QTimer.singleShot(1000, lambda: layout.removeWidget(msg_widget) or msg_widget.deleteLater())

    def register(self):
        """处理注册逻辑"""
        username = self.reg_username_input.text().strip()
        password = self.reg_password_input.text().strip()
        confirm_password = self.reg_confirm_password_input.text().strip()

        # 使用控制器处理注册
        self.auth_controller.handle_register(username, password, confirm_password)

        # if not username or not password or not confirm_password:
        #     QMessageBox.warning(self, "注册失败", "请填写所有字段！")
        #     return
        #
        # if len(username) < 3:
        #     QMessageBox.warning(self, "注册失败", "用户名至少需要3个字符！")
        #     return
        #
        # if len(password) < 6:
        #     QMessageBox.warning(self, "注册失败", "密码至少需要6个字符！")
        #     return
        #
        # if password != confirm_password:
        #     QMessageBox.warning(self, "注册失败", "两次输入的密码不一致！")
        #     return
        #
        # if username in self.users:
        #     QMessageBox.warning(self, "注册失败", "该用户名已存在！")
        #     return
        #
        # # 注册成功
        # self.users[username] = password
        # QMessageBox.information(self, "注册成功", "注册成功，请登录！")
        # self.show_login_page()
        #
        # # 清空注册表单
        # self.reg_username_input.clear()
        # self.reg_password_input.clear()
        # self.reg_confirm_password_input.clear()

    def open_main_window(self):
        """打开主窗口"""
        # 通过 WindowManager 显示主窗口
        from views.window_manager import WindowManager

        # 如果登录窗口有 window_manager 引用，则使用它来显示主窗口
        if hasattr(self, 'window_manager') and self.window_manager:
            self.window_manager.show_main_window()
        else:
            # 否则直接创建主窗口（备用方案）
            # 关闭登录窗口
            self.close()

            # 创建并显示主程序窗口
            self.main_window = MainWindow()
            # 设置主窗口关闭后的回调，返回登录界面
            self.main_window.close_callback = self.return_to_login
            self.main_window.show()

    def return_to_login(self):
        """返回登录界面的回调函数"""
        # 重新显示登录窗口
        new_login = LoginWindow()
        new_login.show()

# 移除了原来的 main() 函数和 if __name__ == "__main__": 部分
