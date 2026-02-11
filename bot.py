import logging
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    Application, CommandHandler, CallbackQueryHandler,
    ContextTypes, MessageHandler, filters
)
import config
from commands import execute_command, predefined_commands
from monitoring import (
    get_system_info,
    get_disk_info,
    get_network_info,
    get_services_status,
    get_detailed_disk_info,
    get_processes_info
)
from auth import is_admin

# Настройка логирования
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO,
    handlers=[
        logging.FileHandler('logs/bot.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# Состояния для хранения последних сообщений с кнопками
user_messages = {}

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Команда /start - главное меню"""
    user_id = update.effective_user.id
    
    if not is_admin(user_id):
        await update.message.reply_text("⛔ Доступ запрещен")
        return
    
    # Удаляем старое меню если есть
    if user_id in user_messages:
        try:
            await context.bot.delete_message(
                chat_id=user_id,
                message_id=user_messages[user_id]
            )
        except:
            pass
    
    keyboard = [
        [InlineKeyboardButton("📊 Мониторинг", callback_data='monitoring')],
        [InlineKeyboardButton("⚡ Быстрые команды", callback_data='quick_cmds')],
        [InlineKeyboardButton("🖥️ Терминал", callback_data='terminal')],
        [InlineKeyboardButton("🔧 Управление", callback_data='management')],
        [InlineKeyboardButton("ℹ️ Помощь", callback_data='help_menu')]
    ]
    
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    msg = await update.message.reply_text(
        "👋 *Добро пожаловать в панель управления сервером!*\n\n"
        "Выберите раздел:",
        reply_markup=reply_markup,
        parse_mode='Markdown'
    )
    
    # Сохраняем ID сообщения с кнопками
    user_messages[user_id] = msg.message_id


async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обработчик кнопок"""
    query = update.callback_query
    await query.answer()
    
    user_id = query.from_user.id
    
    if not is_admin(user_id):
        await query.edit_message_text("⛔ Доступ запрещен")
        return
    
    if query.data == 'main_menu':
        await show_main_menu(query)
    
    elif query.data == 'monitoring':
        await show_monitoring_menu(query)
    
    elif query.data == 'quick_cmds':
        await show_quick_commands(query)
    
    elif query.data == 'terminal':
        await show_terminal_menu(query)
    
    elif query.data == 'management':
        await show_management_menu(query)
    
    elif query.data == 'help_menu':
        await show_help_menu(query)
    
    elif query.data == 'system_status':
        info = get_system_info()
        keyboard = [[InlineKeyboardButton("🔙 Назад", callback_data='monitoring')]]
        await query.edit_message_text(
            info,
            reply_markup=InlineKeyboardMarkup(keyboard),
            parse_mode='Markdown'
        )
    
    elif query.data == 'disk_status':
        info = get_disk_info()
        keyboard = [[InlineKeyboardButton("🔙 Назад", callback_data='monitoring')]]
        await query.edit_message_text(
            info,
            reply_markup=InlineKeyboardMarkup(keyboard),
            parse_mode='Markdown'
        )
    
    elif query.data == 'network_status':
        info = get_network_info()
        keyboard = [[InlineKeyboardButton("🔙 Назад", callback_data='monitoring')]]
        await query.edit_message_text(
            info,
            reply_markup=InlineKeyboardMarkup(keyboard),
            parse_mode='Markdown'
        )
    
    elif query.data == 'services_status':
        info = get_services_status()
        keyboard = [[InlineKeyboardButton("🔙 Назад", callback_data='monitoring')]]
        await query.edit_message_text(
            info,
            reply_markup=InlineKeyboardMarkup(keyboard),
            parse_mode='Markdown'
        )
    
    # НОВЫЕ ОБРАБОТЧИКИ ДЛЯ ДОПОЛНИТЕЛЬНЫХ КНОПОК
    elif query.data == 'disk_detailed':
        info = get_detailed_disk_info()  # Теперь функция импортирована
        keyboard = [[InlineKeyboardButton("🔙 Назад", callback_data='monitoring')]]
        await query.edit_message_text(
            info,
            reply_markup=InlineKeyboardMarkup(keyboard),
            parse_mode='Markdown'
        )
    
    elif query.data == 'memory_status':
        info = get_system_info()
        # Берем только часть о памяти - исправленная версия
        lines = info.split('\n')
        memory_lines = []
        for line in lines:
            lower_line = line.lower()
            if any(word in lower_line for word in ['память', 'memory', 'оператив', 'swap', 'свободно', 'использовано', 'доступно']):
                memory_lines.append(line)
        
        if memory_lines:
            memory_info = '\n'.join(memory_lines)
        else:
            memory_info = "Информация о памяти не найдена"
            
        keyboard = [[InlineKeyboardButton("🔙 Назад", callback_data='monitoring')]]
        await query.edit_message_text(
            f"🧠 *Детальная информация о памяти:*\n\n{memory_info}",
            reply_markup=InlineKeyboardMarkup(keyboard),
            parse_mode='Markdown'
        )
    
    elif query.data == 'processes_status':
        info = get_processes_info()  # Теперь функция импортирована
        keyboard = [[InlineKeyboardButton("🔙 Назад", callback_data='monitoring')]]
        await query.edit_message_text(
            info,
            reply_markup=InlineKeyboardMarkup(keyboard),
            parse_mode='Markdown'
        )
    
    elif query.data.startswith('quick_'):
        cmd_name = query.data[6:]  # Убираем 'quick_'
        if cmd_name in predefined_commands:
            await query.edit_message_text("⏳ Выполняю команду...")
            result = execute_command(predefined_commands[cmd_name]['command'])
            
            keyboard = [
                [InlineKeyboardButton("🔄 Повторить", callback_data=f'quick_{cmd_name}')],
                [InlineKeyboardButton("🔙 Назад", callback_data='quick_cmds')]
            ]
            
            await query.edit_message_text(
                f"*{predefined_commands[cmd_name]['description']}*\n\n"
                f"```\n{predefined_commands[cmd_name]['command']}\n```\n\n"
                f"*Результат:*\n```\n{result}\n```",
                reply_markup=InlineKeyboardMarkup(keyboard),
                parse_mode='Markdown'
            )
    
    elif query.data == 'custom_command':
        context.user_data['awaiting_command'] = True
        keyboard = [[InlineKeyboardButton("❌ Отмена", callback_data='terminal')]]
        await query.edit_message_text(
            "📝 *Введите команду для выполнения:*\n\n"
            "Примеры:\n"
            "• `ls -la`\n"
            "• `df -h`\n"
            "• `systemctl status nginx`\n\n"
            "⚠️ *Будьте осторожны с командами!*",
            reply_markup=InlineKeyboardMarkup(keyboard),
            parse_mode='Markdown'
        )

async def show_main_menu(query):
    """Показать главное меню"""
    keyboard = [
        [InlineKeyboardButton("📊 Мониторинг", callback_data='monitoring')],
        [InlineKeyboardButton("⚡ Быстрые команды", callback_data='quick_cmds')],
        [InlineKeyboardButton("🖥️ Терминал", callback_data='terminal')],
        [InlineKeyboardButton("🔧 Управление", callback_data='management')],
        [InlineKeyboardButton("ℹ️ Помощь", callback_data='help_menu')]
    ]
    
    await query.edit_message_text(
        "👋 *Добро пожаловать в панель управления сервером!*\n\n"
        "Выберите раздел:",
        reply_markup=InlineKeyboardMarkup(keyboard),
        parse_mode='Markdown'
    )

async def show_monitoring_menu(query):
    """Меню мониторинга"""
    keyboard = [
        [InlineKeyboardButton("📈 Статус системы", callback_data='system_status')],
        [InlineKeyboardButton("💾 Дисковое пространство", callback_data='disk_status')],
        [InlineKeyboardButton("💽 Детально о дисках", callback_data='disk_detailed')],
        [InlineKeyboardButton("🧠 Использование памяти", callback_data='memory_status')],
        [InlineKeyboardButton("🌐 Сетевая информация", callback_data='network_status')],
        [InlineKeyboardButton("📡 Состояние сервисов", callback_data='services_status')],
        [InlineKeyboardButton("📈 Топ процессов", callback_data='processes_status')],
        [InlineKeyboardButton("🔙 Главное меню", callback_data='main_menu')]
    ]
    
    await query.edit_message_text(
        "📊 *Мониторинг сервера*\n\n"
        "Выберите что хотите посмотреть:",
        reply_markup=InlineKeyboardMarkup(keyboard),
        parse_mode='Markdown'
    )

async def show_quick_commands(query):
    """Меню быстрых команд"""
    keyboard = []
    
    # Добавляем кнопки для каждой заготовленной команды
    for cmd_name, cmd_info in predefined_commands.items():
        keyboard.append([InlineKeyboardButton(
            cmd_info['description'],
            callback_data=f'quick_{cmd_name}'
        )])
    
    keyboard.append([InlineKeyboardButton("🔙 Главное меню", callback_data='main_menu')])
    
    await query.edit_message_text(
        "⚡ *Быстрые команды*\n\n"
        "Выберите команду для выполнения:",
        reply_markup=InlineKeyboardMarkup(keyboard),
        parse_mode='Markdown'
    )

async def show_terminal_menu(query):
    """Меню терминала"""
    keyboard = [
        [InlineKeyboardButton("📝 Ввести команду", callback_data='custom_command')],
        [InlineKeyboardButton("🔙 Главное меню", callback_data='main_menu')]
    ]
    
    await query.edit_message_text(
        "🖥️ *Терминал сервера*\n\n"
        "Вы можете выполнить любую команду на сервере.\n"
        "⚠️ *Внимание:* Выполняйте только проверенные команды!",
        reply_markup=InlineKeyboardMarkup(keyboard),
        parse_mode='Markdown'
    )

async def show_management_menu(query):
    """Меню управления"""
    keyboard = [
        [InlineKeyboardButton("🔄 Перезагрузить сервер", callback_data='quick_reboot')],
        [InlineKeyboardButton("⏹️ Остановить сервер", callback_data='quick_shutdown')],
        [InlineKeyboardButton("📊 Логи системы", callback_data='quick_logs')],
        [InlineKeyboardButton("🔙 Главное меню", callback_data='main_menu')]
    ]
    
    await query.edit_message_text(
        "🔧 *Управление сервером*\n\n"
        "Выберите действие:",
        reply_markup=InlineKeyboardMarkup(keyboard),
        parse_mode='Markdown'
    )

async def show_help_menu(query):
    """Меню помощи"""
    keyboard = [[InlineKeyboardButton("🔙 Главное меню", callback_data='main_menu')]]
    
    help_text = """
🆘 *Помощь по управлению ботом*

*Основные команды в чате:*
`/start` - Главное меню
`/menu` - Показать меню
`/status` - Краткий статус
`/cmd <команда>` - Выполнить команду
`/help` - Эта справка

*Быстрые команды в меню:*
• 📊 Мониторинг - информация о системе
• ⚡ Быстрые команды - готовые команды
• 🖥️ Терминал - ввод своих команд
• 🔧 Управление - управление сервером

*Безопасность:*
• Только администраторы имеют доступ
• Все действия логируются
• Опасные команды требуют подтверждения
    """
    
    await query.edit_message_text(
        help_text,
        reply_markup=InlineKeyboardMarkup(keyboard),
        parse_mode='Markdown'
    )

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обработка текстовых сообщений"""
    user_id = update.effective_user.id
    
    if not is_admin(user_id):
        return
    
    # Если ждем команду от пользователя
    if context.user_data.get('awaiting_command'):
        command = update.message.text
        
        # Отмена
        if command.lower() in ['отмена', 'cancel', '❌']:
            context.user_data['awaiting_command'] = False
            await update.message.reply_text("❌ Команда отменена")
            await show_terminal_menu(update)
            return
        
        # Выполняем команду
        await update.message.reply_text("⏳ Выполняю команду...")
        result = execute_command(command)
        
        # Обрезаем слишком длинный вывод
        if len(result) > 3500:
            result = result[:3500] + "\n... (вывод обрезан)"
        
        keyboard = [
            [InlineKeyboardButton("🔄 Повторить", callback_data='custom_command')],
            [InlineKeyboardButton("🔙 Терминал", callback_data='terminal')]
        ]
        
        await update.message.reply_text(
            f"*Команда:* `{command}`\n\n"
            f"*Результат:*\n```\n{result}\n```",
            reply_markup=InlineKeyboardMarkup(keyboard),
            parse_mode='Markdown'
        )
        
        context.user_data['awaiting_command'] = False
    
    # Быстрые команды через слэши
    elif update.message.text.startswith('/cmd '):
        command = update.message.text[5:]  # Убираем '/cmd '
        await update.message.reply_text("⏳ Выполняю команду...")
        result = execute_command(command)
        
        if len(result) > 3500:
            result = result[:3500] + "\n... (вывод обрезан)"
        
        await update.message.reply_text(
            f"*Команда:* `{command}`\n\n"
            f"*Результат:*\n```\n{result}\n```",
            parse_mode='Markdown'
        )

async def menu_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Команда /menu для показа меню"""
    user_id = update.effective_user.id
    
    if not is_admin(user_id):
        await update.message.reply_text("⛔ Доступ запрещен")
        return
    
    keyboard = [
        [InlineKeyboardButton("📊 Мониторинг", callback_data='monitoring')],
        [InlineKeyboardButton("⚡ Быстрые команды", callback_data='quick_cmds')],
        [InlineKeyboardButton("🖥️ Терминал", callback_data='terminal')],
        [InlineKeyboardButton("🔧 Управление", callback_data='management')],
        [InlineKeyboardButton("ℹ️ Помощь", callback_data='help_menu')]
    ]
    
    # Удаляем старое меню если есть
    if user_id in user_messages:
        try:
            await context.bot.delete_message(
                chat_id=user_id,
                message_id=user_messages[user_id]
            )
        except:
            pass
    
    msg = await update.message.reply_text(
        "👋 *Главное меню*\n\nВыберите раздел:",
        reply_markup=InlineKeyboardMarkup(keyboard),
        parse_mode='Markdown'
    )
    
    user_messages[user_id] = msg.message_id

async def status_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Команда /status для быстрого статуса"""
    if not is_admin(update.effective_user.id):
        await update.message.reply_text("⛔ Доступ запрещен")
        return
    
    from monitoring import get_system_info
    info = get_system_info()
    
    # Обрезаем для краткости
    lines = info.split('\n')
    short_info = '\n'.join(lines[:15])  # Первые 15 строк
    
    keyboard = [[InlineKeyboardButton("📊 Подробнее", callback_data='system_status')]]
    
    await update.message.reply_text(
        short_info,
        reply_markup=InlineKeyboardMarkup(keyboard),
        parse_mode='Markdown'
    )

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Команда /help"""
    help_text = """
*Быстрые команды в чате:*

`/start` - Главное меню с кнопками
`/menu` - Показать меню
`/status` - Краткий статус системы
`/cmd <команда>` - Выполнить команду
`/help` - Справка

*Быстрые клавиши:*
Для быстрого доступа закрепите эти команды:
• `Статус` → `/status`
• `Диски` → `/cmd df -h`
• `Память` → `/cmd free -h`
• `Процессы` → `/cmd ps aux --sort=-%cpu | head -10`

Используйте `/menu` для полного меню с кнопками!
    """
    
    keyboard = [[InlineKeyboardButton("📋 Открыть меню", callback_data='main_menu')]]
    
    await update.message.reply_text(
        help_text,
        reply_markup=InlineKeyboardMarkup(keyboard),
        parse_mode='Markdown'
    )

def main():
    """Запуск бота"""
    print("🚀 Запуск бота с улучшенным интерфейсом...")
    
    application = Application.builder().token(config.Config.BOT_TOKEN).build()
    
    # Регистрация обработчиков
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("menu", menu_command))
    application.add_handler(CommandHandler("status", status_command))
    application.add_handler(CommandHandler("help", help_command))
    application.add_handler(CommandHandler("cmd", 
        lambda u, c: handle_message(u, c) if u.message.text.startswith('/cmd ') else None))
    
    application.add_handler(CallbackQueryHandler(button_handler))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    
    print("✅ Бот запущен")
    print("📱 Используйте /menu для открытия меню с кнопками")
    
    application.run_polling(drop_pending_updates=True)

if __name__ == '__main__':
    main()
