# file: src/views/top_buttons_manager.py
from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QApplication


class TopButtonsManager:
    def __init__(self, main_window):
        self.main_window = main_window
        self.setup_connections()

    def setup_connections(self):
        """连接顶部按钮的信号与槽函数"""
        # 关闭按钮
        self.main_window.closeAppBtn.clicked.connect(self.close_window)
        # 最大化/恢复按钮
        self.main_window.maximizeRestoreAppBtn.clicked.connect(self.toggle_maximize)
        # 最小化按钮
        self.main_window.minimizeAppBtn.clicked.connect(self.minimize_window)

    def close_window(self):
        """关闭窗口"""
        self.main_window.close()

    def toggle_maximize(self):
        """切换最大化/恢复窗口"""
        if self.main_window.isMaximized():
            self.main_window.showNormal()
            # 可以在这里更新图标为最大化图标
        else:
            # 设置最小尺寸
            self.main_window.setMinimumSize(1331, 831)
            self.main_window.showMaximized()

    def minimize_window(self):
        """最小化窗口"""
        self.main_window.showMinimized()
