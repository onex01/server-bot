import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    # Токен бота от @BotFather
    BOT_TOKEN = os.getenv('BOT_TOKEN')
    
    # Проверка загрузки токена
    if not BOT_TOKEN:
        print("❌ ВНИМАНИЕ: BOT_TOKEN не загружен!")
        print(f"   Проверьте .env файл в директории: {os.getcwd()}")
        print(f"   Содержимое .env: {open('.env').read() if os.path.exists('.env') else 'Файл не найден'}")
    else:
        print(f"✅ Токен загружен (первые 10 символов): {BOT_TOKEN[:10]}...")
    
    # ID администраторов
    admin_ids_str = os.getenv('ADMIN_IDS', '')
    ADMIN_IDS = []
    if admin_ids_str:
        for id_str in admin_ids_str.split(','):
            try:
                ADMIN_IDS.append(int(id_str.strip()))
            except ValueError:
                print(f"Warning: Invalid admin ID '{id_str}'")
    else:
        print("⚠️ ADMIN_IDS не загружены")
    
    print(f"✅ Admin IDs: {ADMIN_IDS}")
    
    # Максимальное время выполнения команд (секунды)
    COMMAND_TIMEOUT = 30
    
    # Интервал мониторинга (секунды)
    MONITORING_INTERVAL = 60
    
    # Сервисы для мониторинга
    SERVICES = {
        'website': 'https://onex01.ru',
	    'cloud': 'https://cloud.onex01.ru',
        'minecraft': 'onex01.ddns.net:25565'
    }
