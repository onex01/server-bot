import config

def is_admin(user_id):
    """Проверка, является ли пользователь администратором"""
    return user_id in config.Config.ADMIN_IDS