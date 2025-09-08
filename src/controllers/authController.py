# authController.py
from services.userService import UserService
from views.login_window import LoginWindow
from PyQt5.QtWidgets import QMessageBox
from PyQt5.QtCore import QTimer

class AuthController:
    """
    认证控制器类，处理登录和注册相关的界面交互
    """

    def __init__(self, login_window: LoginWindow):
        """
        初始化认证控制器

        Args:
            login_window: 登录窗口实例
        """
        self.login_window = login_window
        self.user_service = UserService()

    def handle_login(self, username: str, password: str):
        """
        处理用户登录请求

        Args:
            username: 用户名
            password: 密码
        """
        # 前端验证
        if not username or not password:
            QMessageBox.warning(self.login_window, "登录失败", "请输入用户名和密码！")
            return

        # 调用服务层进行用户认证
        user = self.user_service.authenticate_user(username, password)

        if user:
            # 登录成功
            self.login_window.show_success_message(f"欢迎，{username}！")
            # 1秒后打开主程序界面
            QTimer.singleShot(1000, self.login_window.open_main_window)
        else:
            # 登录失败
            QMessageBox.warning(self.login_window, "登录失败", "用户名或密码错误！")

    def handle_register(self, username: str, password: str, confirm_password: str):
        """
        处理用户注册请求

        Args:
            username: 用户名
            password: 密码
            confirm_password: 确认密码
        """
        # 前端验证
        if not username or not password or not confirm_password:
            QMessageBox.warning(self.login_window, "注册失败", "请填写所有字段！")
            return

        if len(username) < 3:
            QMessageBox.warning(self.login_window, "注册失败", "用户名至少需要3个字符！")
            return

        if len(password) < 6:
            QMessageBox.warning(self.login_window, "注册失败", "密码至少需要6个字符！")
            return

        if password != confirm_password:
            QMessageBox.warning(self.login_window, "注册失败", "两次输入的密码不一致！")
            return

        # 检查用户名是否已存在
        if self.user_service.username_exists(username):
            QMessageBox.warning(self.login_window, "注册失败", "该用户名已存在！")
            return

        # 调用服务层注册用户
        success = self.user_service.register_user(username, password)

        if success:
            QMessageBox.information(self.login_window, "注册成功", "注册成功，请登录！")
            self.login_window.show_login_page()

            # 清空注册表单
            self.login_window.reg_username_input.clear()
            self.login_window.reg_password_input.clear()
            self.login_window.reg_confirm_password_input.clear()
        else:
            QMessageBox.warning(self.login_window, "注册失败", "注册失败，请稍后重试！")
