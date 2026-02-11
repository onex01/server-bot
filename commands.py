import subprocess
import shlex
import config

def execute_command(command, timeout=config.Config.COMMAND_TIMEOUT):
    """Выполнение команды в терминале"""
    try:
        # Безопасное разделение команды на аргументы
        if '|' in command or '&&' in command or '>' in command or 'sudo' in command:
            # Для сложных команд используем shell=True
            result = subprocess.run(
                command,
                shell=True,
                capture_output=True,
                text=True,
                timeout=timeout
            )
        else:
            # Для простых команд безопаснее без shell
            args = shlex.split(command)
            result = subprocess.run(
                args,
                capture_output=True,
                text=True,
                timeout=timeout
            )
        
        output = result.stdout if result.stdout else result.stderr
        
        if result.returncode == 0:
            return output if output else "✅ Команда выполнена успешно"
        else:
            return f"❌ Ошибка (код {result.returncode}):\n{output}"
    
    except subprocess.TimeoutExpired:
        return "⏰ Таймаут выполнения команды"
    except Exception as e:
        return f"⚠️ Ошибка: {str(e)}"

# Заготовленные команды
predefined_commands = {
    'disk_usage': {
        'command': 'df -h -T',
        'description': '💾 Использование дисков (с типами)'
    },
    'disk_detailed': {
        'command': 'lsblk -o NAME,SIZE,TYPE,MOUNTPOINT,FSTYPE,LABEL,UUID',
        'description': '💽 Детальная информация о дисках'
    },
    'memory': {
        'command': 'free -h',
        'description': '🧠 Использование памяти'
    },
    'memory_detailed': {
        'command': 'cat /proc/meminfo | head -20',
        'description': '🧠 Детальная информация о памяти'
    },
    'uptime': {
        'command': 'uptime',
        'description': '⏱️ Время работы'
    },
    'top_processes': {
        'command': 'ps aux --sort=-%cpu | head -15',
        'description': '📈 Топ процессов (CPU)'
    },
    'top_memory': {
        'command': 'ps aux --sort=-%mem | head -15',
        'description': '📈 Топ процессов (память)'
    },
    'network_stats': {
        'command': 'ss -tulpn',
        'description': '🌐 Сетевые соединения'
    },
    'mount_info': {
        'command': 'mount | grep -E "/dev/sd|/dev/mmc"',
        'description': '📌 Информация о монтировании'
    },
    'check_disks': {
        'command': 'ls -la /dev/sd* /dev/mmcblk*',
        'description': '🔍 Проверить дисковые устройства'
    },
    'external_disk': {
        'command': 'df -h /mnt/cloud 2>/dev/null || echo "Диск не найден"',
        'description': '🗂️ Проверить внешний HDD (/mnt/cloud)'
    },
    'system_logs': {
        'command': 'journalctl -n 20 --no-pager',
        'description': '📋 Последние логи'
    },
    'service_status': {
        'command': 'systemctl list-units --type=service --state=running | head -20',
        'description': '🔄 Запущенные сервисы'
    },
    'cpu_info': {
        'command': 'lscpu | grep -E "Model name|CPU\(s\)|Architecture"',
        'description': '⚙️ Информация о CPU'
    },
    'temperature': {
        'command': 'cat /sys/class/thermal/thermal_zone*/temp 2>/dev/null | head -1',
        'description': '🌡️ Температура CPU'
    }
}
