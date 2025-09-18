# file: src/views/window_manager.py
from PyQt5.QtWidgets import QApplication
from views.login_window import LoginWindow
from views.main_window import MainWindow

class WindowManager:
    def __init__(self):
        self.login_window = None
        self.main_window = None

    def show_login_window(self):
        """显示登录窗口"""
        if self.main_window:
            self.main_window.close()
            self.main_window = None

        self.login_window = LoginWindow()
        # 将 WindowManager 实例传递给登录窗口
        self.login_window.window_manager = self
        # 设置窗口关闭时的回调
        self.login_window.close_callback = self.on_login_window_closed
        self.login_window.show()

    def show_main_window(self):
        """显示主窗口"""
        if self.login_window:
            self.login_window.close()
            self.login_window = None

        self.main_window = MainWindow()
        # 设置主窗口关闭后的回调，返回登录界面
        self.main_window.close_callback = self.on_main_window_closed
        self.main_window.show()

    def on_login_window_closed(self):
        """登录窗口关闭时的处理"""
        self.login_window = None

    def on_main_window_closed(self):
        """主窗口关闭时的处理"""
        self.main_window = None
        # 主窗口关闭时显示登录窗口
        self.show_login_window()

    def quit_application(self):
        """退出应用程序"""
        if self.login_window:
            self.login_window.close()
        if self.main_window:
            self.main_window.close()
        QApplication.quit()
