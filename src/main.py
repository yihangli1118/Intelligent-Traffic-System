# file: src/main.py
import sys
import os
from PyQt5.QtWidgets import QApplication
from views.window_manager import WindowManager

# 添加当前目录到Python路径
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def main():
    app = QApplication(sys.argv)

    # 创建窗口管理器
    window_manager = WindowManager()

    # 显示登录窗口
    window_manager.show_login_window()

    # 运行应用程序
    sys.exit(app.exec_())

if __name__ == "__main__":
    main()
