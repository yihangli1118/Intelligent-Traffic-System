# src/utils/session_manager.py
class SessionManager:
    """
    会话管理器，用于在应用程序中存储和访问当前登录用户的信息
    """
    _instance = None
    _current_user = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(SessionManager, cls).__new__(cls)
        return cls._instance

    def set_current_user(self, username):
        """
        设置当前登录的用户

        Args:
            username (str): 用户名
        """
        self._current_user = username

    def get_current_user(self):
        """
        获取当前登录的用户

        Returns:
            str: 当前登录的用户名，如果未登录则返回None
        """
        return self._current_user

    def clear_session(self):
        """
        清除当前用户会话
        """
        self._current_user = None
