import socket
import requests
from requests.exceptions import RequestException
import logging

logger = logging.getLogger(__name__)

def check_service_status(url, timeout=5):
    """Проверка доступности HTTP/HTTPS сервиса"""
    try:
        response = requests.get(url, timeout=timeout)
        if 200 <= response.status_code < 300:
            return "🟢 Онлайн"
        else:
            return f"🟡 Ошибка {response.status_code}"
    except RequestException as e:
        logger.error(f"Ошибка проверки сервиса {url}: {e}")
        return "🔴 Офлайн"

def check_minecraft_server(address, timeout=5):
    """Проверка Minecraft сервера"""
    try:
        if ':' in address:
            host, port = address.split(':')
            port = int(port)
        else:
            host = address
            port = 25565
        
        # Создаем сокет
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(timeout)
        
        result = sock.connect_ex((host, port))
        sock.close()
        
        if result == 0:
            return "🟢 Онлайн"
        else:
            return "🔴 Офлайн"
    except Exception as e:
        logger.error(f"Ошибка проверки Minecraft сервера {address}: {e}")
        return "🔴 Ошибка"
