import psutil
import platform
import socket
import requests
from datetime import datetime
import os
import re
import config

def get_system_info():
    """Получение информации о системе для Orange Pi Zero 3"""
    cpu_percent = psutil.cpu_percent(interval=1)
    memory = psutil.virtual_memory()
    load_avg = psutil.getloadavg()
    
    # Получаем температуру для Orange Pi
    cpu_temp = get_cpu_temperature()
    
    # Получаем информацию о swap
    swap = psutil.swap_memory()
    
    info = f"""
📊 *Статус системы Orange Pi Zero 3*

*CPU (4 ядра):*
• Использование: {cpu_percent}%
• Температура: {cpu_temp}
• Загрузка (1, 5, 15 мин): {load_avg[0]:.2f}, {load_avg[1]:.2f}, {load_avg[2]:.2f}

*Оперативная память:*
• Всего: {bytes_to_gb(memory.total):.1f} GB
• Использовано: {bytes_to_gb(memory.used):.1f} GB ({memory.percent}%)
• Свободно: {bytes_to_gb(memory.free):.1f} GB
• Доступно: {bytes_to_gb(memory.available):.1f} GB

*SWAP (подкачка):*
• Всего: {bytes_to_gb(swap.total):.1f} GB
• Использовано: {bytes_to_gb(swap.used):.1f} GB ({swap.percent}%)

*Система:*
• Хост: `{platform.node()}`
• ОС: {platform.system()} {platform.release()}
• Архитектура: {platform.machine()}
• Время работы: {get_uptime()}
• Дата/время: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
    """
    
    return info

def get_disk_info():
    """Информация о дисках с исправлением для внешних HDD"""
    disks = []
    
    # Используем команду df для более точной информации
    try:
        import subprocess
        result = subprocess.run(['df', '-h', '-T'], 
                              capture_output=True, 
                              text=True)
        lines = result.stdout.strip().split('\n')
        
        # Пропускаем заголовок
        for line in lines[1:]:
            parts = line.split()
            if len(parts) >= 7:
                filesystem = parts[0]
                fstype = parts[1]
                size = parts[2]
                used = parts[3]
                avail = parts[4]
                use_percent = parts[5]
                mountpoint = parts[6]
                
                # Форматируем информацию
                disks.append(
                    f"*{filesystem}* (`{mountpoint}`)\n"
                    f"• Тип: {fstype}\n"
                    f"• Размер: {size}\n"
                    f"• Использовано: {used} ({use_percent})\n"
                    f"• Свободно: {avail}\n"
                )
    except:
        # Fallback на psutil если команда не сработала
        for partition in psutil.disk_partitions(all=True):
            try:
                usage = psutil.disk_usage(partition.mountpoint)
                disks.append(
                    f"*{partition.device}* (`{partition.mountpoint}`)\n"
                    f"• Тип: {partition.fstype}\n"
                    f"• Размер: {bytes_to_gb(usage.total):.1f} GB\n"
                    f"• Использовано: {bytes_to_gb(usage.used):.1f} GB ({usage.percent}%)\n"
                    f"• Свободно: {bytes_to_gb(usage.free):.1f} GB\n"
                )
            except:
                continue
    
    # Дополнительно проверяем конкретные точки монтирования
    special_mounts = ['/mnt/cloud', '/media', '/mnt']
    for mount in special_mounts:
        if os.path.ismount(mount):
            try:
                usage = psutil.disk_usage(mount)
                # Найдем устройство для этой точки монтирования
                device = "Unknown"
                for part in psutil.disk_partitions(all=True):
                    if part.mountpoint == mount:
                        device = part.device
                        break
                
                disks.append(
                    f"*{device}* (`{mount}`) [External]\n"
                    f"• Размер: {bytes_to_gb(usage.total):.1f} GB\n"
                    f"• Использовано: {bytes_to_gb(usage.used):.1f} GB ({usage.percent}%)\n"
                    f"• Свободно: {bytes_to_gb(usage.free):.1f} GB\n"
                )
            except:
                pass
    
    if not disks:
        return "💾 *Информация о дисках:*\n\nНет информации о дисках"
    
    return "💾 *Информация о дисках:*\n\n" + "\n".join(disks)

def get_detailed_disk_info():
    """Детальная информация о дисках через lsblk"""
    try:
        import subprocess
        
        # Получаем информацию о блочных устройствах
        result = subprocess.run(['lsblk', '-o', 'NAME,SIZE,TYPE,MOUNTPOINT,FSTYPE', '-r'],
                              capture_output=True, text=True)
        
        devices = []
        current_device = ""
        
        for line in result.stdout.strip().split('\n')[1:]:  # Пропускаем заголовок
            parts = line.split()
            if len(parts) >= 4:
                name = parts[0]
                size = parts[1]
                dev_type = parts[2]
                mountpoint = parts[3] if len(parts) > 3 else ""
                fstype = parts[4] if len(parts) > 4 else ""
                
                if dev_type == "disk":
                    current_device = name
                    devices.append(f"\n*Диск {name}:* {size}")
                elif dev_type == "part" and mountpoint:
                    devices.append(f"  └─ {name}: {size} → `{mountpoint}` ({fstype})")
        
        return "💽 *Детальная информация о дисках:*\n" + "\n".join(devices)
    except Exception as e:
        return f"💽 *Информация о дисках:*\n\nНе удалось получить детальную информацию: {str(e)}"

def get_network_info():
    """Информация о сети"""
    net_io = psutil.net_io_counters()
    
    info = f"""
🌐 *Сетевая информация*

*Передача данных:*
• Отправлено: {bytes_to_mb(net_io.bytes_sent):.1f} MB
• Получено: {bytes_to_mb(net_io.bytes_recv):.1f} MB
• Пакеты отправлено: {net_io.packets_sent:,}
• Пакеты получено: {net_io.packets_recv:,}

*Сетевые интерфейсы:*
    """
    
    interfaces = psutil.net_if_addrs()
    stats = psutil.net_if_stats()
    
    for interface, addrs in interfaces.items():
        if interface in stats and stats[interface].isup:
            info += f"\n• *{interface}* (UP, скорость: {stats[interface].speed} Mbps):"
            for addr in addrs:
                if addr.family == 2:  # IPv4
                    info += f"\n  IPv4: `{addr.address}`"
                    if addr.netmask:
                        info += f" / {addr.netmask}"
                elif addr.family == 10:  # IPv6
                    info += f"\n  IPv6: `{addr.address}`"
                elif addr.family == 17:  # MAC
                    info += f"\n  MAC: `{addr.address}`"
    
    return info

def get_services_status():
    """Статус сервисов"""
    status_text = "📡 *Статус сервисов*\n\n"
    
    # Базовые сервисы для проверки
    services_to_check = [
        ('SSH (22)', 'localhost', 22),
        ('HTTP (80)', 'localhost', 80),
        ('HTTPS (443)', 'localhost', 443),
    ]
    
    # Проверка портов
    for name, host, port in services_to_check:
        status = check_port(host, port)
        status_text += f"{status} *{name}*: {'Онлайн' if '✅' in status else 'Офлайн'}\n"
    
    # Проверка системных сервисов через systemctl
    try:
        import subprocess
        services = ['ssh', 'apache2', 'mysql',]
        
        for service in services:
            try:
                result = subprocess.run(['systemctl', 'is-active', service], 
                                      capture_output=True, text=True)
                if result.stdout.strip() == 'active':
                    status_text += f"✅ *{service}*: Запущен\n"
                else:
                    status_text += f"❌ *{service}*: Не запущен\n"
            except:
                pass
    except:
        pass
    
    # Проверка дополнительных сервисов из конфига
    for name, address in config.Config.SERVICES.items():
        try:
            if address.startswith('http'):
                response = requests.get(address, timeout=3)
                if 200 <= response.status_code < 300:
                    status_text += f"✅ *{name}*: Онлайн ({response.status_code})\n"
                else:
                    status_text += f"⚠️ *{name}*: Ошибка {response.status_code}\n"
            elif ':' in address:
                host, port = address.split(':')
                port = int(port)
                if check_port(host, port, timeout=2) == "✅":
                    status_text += f"✅ *{name}*: Онлайн\n"
                else:
                    status_text += f"❌ *{name}*: Офлайн\n"
        except Exception as e:
            status_text += f"⚠️ *{name}*: Ошибка проверки\n"
    
    return status_text

def get_cpu_temperature():
    """Получение температуры CPU для Orange Pi"""
    temp_paths = [
        '/sys/class/thermal/thermal_zone0/temp',
        '/sys/class/hwmon/hwmon0/temp1_input',
        '/sys/devices/virtual/thermal/thermal_zone0/temp'
    ]
    
    for temp_path in temp_paths:
        if os.path.exists(temp_path):
            try:
                with open(temp_path, 'r') as f:
                    temp = float(f.read().strip())
                    if temp > 1000:  # Если в миллиградусах
                        temp = temp / 1000
                    return f"{temp:.1f}°C"
            except:
                continue
    
    # Попробуем через команду
    try:
        import subprocess
        result = subprocess.run(['vcgencmd', 'measure_temp'], 
                              capture_output=True, text=True)
        if result.returncode == 0:
            temp_str = result.stdout.strip()
            temp = float(temp_str.split('=')[1].split("'")[0])
            return f"{temp:.1f}°C"
    except:
        pass
    
    return "N/A"

def check_port(host, port, timeout=3):
    """Проверка доступности порта"""
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(timeout)
        
        if sock.connect_ex((host, port)) == 0:
            sock.close()
            return "✅"
        else:
            sock.close()
            return "❌"
    except:
        return "⚠️"

def get_uptime():
    """Время работы системы"""
    boot_time = datetime.fromtimestamp(psutil.boot_time())
    uptime = datetime.now() - boot_time
    
    days = uptime.days
    hours, remainder = divmod(uptime.seconds, 3600)
    minutes, seconds = divmod(remainder, 60)
    
    if days > 0:
        return f"{days}д {hours}ч {minutes}м"
    else:
        return f"{hours}ч {minutes}м"

def bytes_to_gb(bytes_value):
    """Конвертация байтов в гигабайты"""
    return bytes_value / (1024 ** 3)

def bytes_to_mb(bytes_value):
    """Конвертация байтов в мегабайты"""
    return bytes_value / (1024 ** 2)

def get_processes_info(top_n=10):
    """Информация о процессах"""
    try:
        processes = []
        for proc in psutil.process_iter(['pid', 'name', 'cpu_percent', 'memory_percent']):
            try:
                processes.append(proc.info)
            except:
                pass
        
        # Сортируем по использованию CPU
        processes.sort(key=lambda x: x['cpu_percent'], reverse=True)
        
        info = "📈 *Топ процессов по CPU:*\n\n"
        info += "PID | Имя | CPU% | Память%\n"
        info += "-" * 40 + "\n"
        
        for proc in processes[:top_n]:
            info += f"{proc['pid']:5} | {proc['name'][:15]:15} | {proc['cpu_percent']:5.1f} | {proc['memory_percent']:6.2f}\n"
        
        return info
    except Exception as e:
        return f"❌ Ошибка получения процессов: {str(e)}"
