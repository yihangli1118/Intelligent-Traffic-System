# userService.py
from models.user import User, UserManager
from typing import Optional, List

class UserService:
    """
    用户业务逻辑服务类
    """

    def __init__(self):
        # 确保用户表存在
        UserManager.create_table()

    def register_user(self, username: str, password: str) -> bool:
        """
        注册新用户

        Args:
            username: 用户名
            password: 密码

        Returns:
            bool: 注册成功返回True，否则返回False
        """
        # 数据验证
        if not username or not password:
            return False

        if len(username) < 3:
            return False

        if len(password) < 6:
            return False

        # 检查用户名是否已存在
        existing_user = UserManager.get_user_by_username(username)
        if existing_user:
            return False

        # 创建用户对象
        user = User(username=username, password=password)

        # 保存到数据库
        return UserManager.insert_user(user)

    def authenticate_user(self, username: str, password: str) -> Optional[User]:
        """
        验证用户身份

        Args:
            username: 用户名
            password: 密码

        Returns:
            User: 验证成功的用户对象，失败返回None
        """
        if not username or not password:
            return None

        return UserManager.authenticate_user(username, password)

    def get_user_by_id(self, user_id: int) -> Optional[User]:
        """
        根据ID获取用户

        Args:
            user_id: 用户ID

        Returns:
            User: 用户对象，不存在返回None
        """
        return UserManager.get_user_by_id(user_id)

    def get_all_users(self) -> List[User]:
        """
        获取所有用户

        Returns:
            List[User]: 用户列表
        """
        return UserManager.get_all_users()

    def update_user_info(self, user: User) -> bool:
        """
        更新用户信息

        Args:
            user: 用户对象

        Returns:
            bool: 更新成功返回True，否则返回False
        """
        if not user.id:
            return False
        return UserManager.update_user(user)

    def delete_user(self, user_id: int) -> bool:
        """
        删除用户

        Args:
            user_id: 用户ID

        Returns:
            bool: 删除成功返回True，否则返回False
        """
        if user_id <= 0:
            return False
        return UserManager.delete_user(user_id)

    def username_exists(self, username: str) -> bool:
        """
        检查用户名是否存在

        Args:
            username: 用户名

        Returns:
            bool: 用户名存在返回True，否则返回False
        """
        user = UserManager.get_user_by_username(username)
        return user is not None
