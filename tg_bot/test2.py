# bot by Zharkov Roman (tg @arabich222)
# todo:
# [x] check_a_records
# [ ] search_by_domain
# [ ] search_by_ip

import os
#import socket
import logging
import time
import configparser
import subprocess
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, InputFile
from telegram.ext import Application, CommandHandler, MessageHandler, CallbackQueryHandler, filters, ContextTypes, ConversationHandler
#from yarl import Query

# Настройка логирования
logging.basicConfig(
    filename="bot.log",
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger("Bot")

# Конфигурация из cred.txt
config = configparser.ConfigParser()
config.read('/Users/romanzharkov/Documents/GitHub/domain-subdomain-api-beget-check/tg_bot/cred.txt')
PASSWORD = config['TEST']['pass']
TOKEN = config['TEST']['token']

# Конфигурация
FILES_DIR = '/Users/romanzharkov/Documents/GitHub/domain-subdomain-api-beget-check/'
files_to_check = ["free.txt", "close.txt", "ssl_https.txt", "ssl.txt", "nossl.txt", "domain_tree.txt", "A.txt", "manual.txt", "regru.txt", "auto.txt"]

# Списки пользователей
authorized_users = set()
awaiting_password = set()

# Функция для обработки команды /start
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    username = update.effective_user.username
    logger.info(f"Команда /start от пользователя {username} (ID: {user_id})")

    if user_id in authorized_users:
        await show_menu(update)
    else:
        awaiting_password.add(user_id)
        await update.message.reply_text(
            "Добро пожаловать! Пожалуйста, введите пароль для авторизации."
        )

# Функция для обработки пароля
async def handle_password(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    username = update.effective_user.username

    if user_id in authorized_users:
        return

    if user_id in awaiting_password:
        if update.message.text == PASSWORD:
            authorized_users.add(user_id)
            awaiting_password.remove(user_id)
            logger.info(f"Пользователь {username} (ID: {user_id}) авторизовался успешно")
            await update.message.reply_text("Авторизация успешна! Теперь вы можете пользоваться ботом.")
            await show_menu(update)
        else:
            logger.warning(f"Ошибка ввода пароля пользователем {username} (ID: {user_id})")
            await update.message.reply_text("Неверный пароль. Попробуйте еще раз.")

# Меню с кнопками
async def show_menu(update: Update):
    keyboard = [
        [InlineKeyboardButton("List Files", callback_data="list_files"), InlineKeyboardButton("Run Scripts", callback_data="run_scripts")],
        [InlineKeyboardButton("Free Beget Domain", callback_data="free_beget_domain"), InlineKeyboardButton("Close Beget Domain", callback_data="close_beget_domain")],
        [InlineKeyboardButton("SSL Domain", callback_data="ssl_domain"), InlineKeyboardButton("No SSL Domain", callback_data="no_ssl_domain")],
        [InlineKeyboardButton("All Domain", callback_data="all_domain"), InlineKeyboardButton("Domain Tree", callback_data="domain_tree")],
        [InlineKeyboardButton("Search by ip", callback_data="search_by_ip"), InlineKeyboardButton("Search by domain", callback_data="search_by_domain")],
        [InlineKeyboardButton("Get new A records", callback_data="check_a_records")]
    ]

    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text("Выберите действие:", reply_markup=reply_markup)

# Функция для обработки действий из меню
async def handle_action(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    user_id = query.from_user.id
    username = query.from_user.username

    if user_id not in authorized_users:
        return

    action = query.data
    logger.info(f"Пользователь {username} (ID: {user_id}) запросил действие: {action}")

    if action == "list_files":
        await list_files(query)
    elif action == "check_a_records":
        await check_a_records(update, context) 
    elif action == "search_by_domain":
        logger.info("Действие search_by_domain вызвано.")
        await context.application.create_task(start_search(update, context))
    elif action == "free_beget_domain":
        await send_file_with_timestamp(query, "/Users/romanzharkov/Documents/GitHub/domain-subdomain-api-beget-check/free.txt")
    elif action == "close_beget_domain":
        await send_file_with_timestamp(query, "/Users/romanzharkov/Documents/GitHub/domain-subdomain-api-beget-check/close.txt")
    elif action == "ssl_domain":
        await send_file_with_timestamp(query, "/Users/romanzharkov/Documents/GitHub/domain-subdomain-api-beget-check/ssl.txt")
    elif action == "no_ssl_domain":
        await send_file_with_timestamp(query, "/Users/romanzharkov/Documents/GitHub/domain-subdomain-api-beget-check/nossl.txt")
    elif action == "all_domain":
        await send_file_with_timestamp(query, "/Users/romanzharkov/Documents/GitHub/domain-subdomain-api-beget-check/ssl_https.txt")
    elif action == "domain_tree":
        await send_file_with_timestamp(query, "/Users/romanzharkov/Documents/GitHub/domain-subdomain-api-beget-check/domain_tree.txt")
    elif action == "run_scripts":
        await run_scripts(query)
    else:
        await query.message.reply_text("Неизвестная команда. Пожалуйста, выберите из меню.")

# Разбить текст на части для Telegram
async def send_long_message(update, text):
    chunk_size = 4000
    for i in range(0, len(text), chunk_size):
        await update.message.reply_text(text[i:i + chunk_size])

# Функция для запуска скриптов main.py и merge.py
async def run_scripts(update: Update):
    try:
        # Уведомление о запуске main.py
        await update.message.reply_text("Запуск скрипта main.py. Пожалуйста, подождите...")
        logger.info("Запуск main.py")

        main_script_path = os.path.join(FILES_DIR, "main.py")
        main_process = subprocess.run(["python3", main_script_path], capture_output=True, text=True)

        if main_process.returncode == 0:
            logger.info("main.py выполнен успешно")
            await send_long_message(update, f"main.py выполнен успешно. Вывод:\n{main_process.stdout}")
        else:
            logger.error(f"Ошибка выполнения main.py: {main_process.stderr}")
            await send_long_message(update, f"Ошибка выполнения main.py:\n{main_process.stderr}")
            return

        # Уведомление о запуске merge.py
        await update.message.reply_text("Запуск скрипта merge.py. Пожалуйста, подождите...")
        logger.info("Запуск merge.py")

        merge_script_path = os.path.join(FILES_DIR, "merge.py")
        merge_process = subprocess.run(["python3", merge_script_path], capture_output=True, text=True)

        if merge_process.returncode == 0:
            logger.info("merge.py выполнен успешно")
            await send_long_message(update, f"merge.py выполнен успешно. Вывод:\n{merge_process.stdout}")
        else:
            logger.error(f"Ошибка выполнения merge.py: {merge_process.stderr}")
            await send_long_message(update, f"Ошибка выполнения merge.py:\n{merge_process.stderr}")
    except Exception as e:
        logger.exception(f"Ошибка при выполнении скриптов: {e}")
        await update.message.reply_text("Произошла ошибка при выполнении скриптов.")


async def check_a_records(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        # Используем сообщение из callback_query
        await update.callback_query.message.reply_text("Запуск скрипта A-check.py. Пожалуйста, подождите...")
        logger.info("Запуск A-check.py")

        main_script_path = os.path.join(FILES_DIR, "A-check.py")
        main_process = subprocess.run(["python3", main_script_path], capture_output=True, text=True)

        if main_process.returncode == 0:
            logger.info("A-check.py выполнен успешно")
            await update.callback_query.message.reply_text(f"A-check.py выполнен успешно. Вывод:\n{main_process.stdout}")
            await send_file_with_timestamp(update, os.path.join(FILES_DIR, "A.txt"))
        else:
            logger.error(f"Ошибка выполнения A-check.py: {main_process.stderr}")
            await update.callback_query.message.reply_text(f"Ошибка выполнения A-check.py:\n{main_process.stderr}")
    except Exception as e:
        logger.exception(f"Ошибка при выполнении A-check.py: {e}")
        await update.callback_query.message.reply_text("Произошла ошибка при выполнении A-check.py.")

#--------------------------------------------------------------------------------------------------

#не дописано
async def search_by_ip(ip, input_file, output_file):
    results = []
    with open(input_file, 'r') as infile:
        for line in infile:
            if ip in line:
                results.append(line.strip())
    with open(output_file, 'w') as outfile:
        for result in results:
            outfile.write(result + '\n')
    return results

#--------------------------------------------------------------------------------------------------

#не дописано
WAITING_FOR_INPUT = range(1)

async def start_search(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Начинает процесс ввода домена."""
    logger.info("start_search вызван")
    try:
        if update.message:
            await update.message.reply_text("Введите домен для поиска:")
        elif update.callback_query:
            await update.callback_query.answer()
            await update.callback_query.message.reply_text("Введите домен для поиска:")
        else:
            logger.error("Неизвестный источник команды")
            return ConversationHandler.END

        logger.info("Переход в состояние WAITING_FOR_INPUT")
        return WAITING_FOR_INPUT
    except Exception as e:
        logger.exception(f"Ошибка в start_search: {e}")
        return ConversationHandler.END

async def handle_domain_input(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обрабатывает ввод домена."""
    logger.info("handle_domain_input вызван")
    try:
        # Проверяем введённый текст
        domain_query = update.message.text.strip()
        logger.info(f"Пользователь ввёл домен: {domain_query}")

        # Путь к файлу
        file_path = os.path.join(FILES_DIR, "A.txt")
        if not os.path.exists(file_path):
            await update.message.reply_text("Файл A.txt не найден. Убедитесь, что файл существует.")
            return ConversationHandler.END

        # Поиск домена в файле
        found_lines = []
        with open(file_path, "r", encoding="utf-8") as file:
            for line in file:
                if domain_query in line:
                    found_lines.append(line.strip())

        if found_lines:
            result = "\n".join(found_lines)
            await update.message.reply_text(f"Найдено:\n{result}")
        else:
            await update.message.reply_text("Домен не найден.")
        
        return ConversationHandler.END
    except Exception as e:
        logger.exception(f"Ошибка в handle_domain_input: {e}")
        await update.message.reply_text("Произошла ошибка при обработке домена.")
        return ConversationHandler.END

async def cancel_search(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Отменяет процесс поиска."""
    await update.message.reply_text("Поиск отменён.")
    return ConversationHandler.END

# Обработчик ConversationHandler
search_handler = ConversationHandler(
    entry_points=[CommandHandler("search_by_domain", start_search)],
    states={
        WAITING_FOR_INPUT: [MessageHandler(filters.TEXT & ~filters.COMMAND, handle_domain_input)],
    },
    fallbacks=[CommandHandler("cancel", cancel_search)],
)

#--------------------------------------------------------------------------------------------------

# Функция для отправки файла
async def send_file_with_timestamp(update: Update, filepath: str):
    try:
        absolute_path = os.path.join(FILES_DIR, filepath)
        logger.info(f"Попытка отправить файл: {absolute_path}")

        # Проверка существования файла
        if not os.path.exists(absolute_path):
            logger.error(f"Файл {filepath} не найден.")
            # Используем соответствующее сообщение
            if update.callback_query:
                await update.callback_query.message.reply_text(f"Файл {filepath} не найден.")
            else:
                await update.message.reply_text(f"Файл {filepath} не найден.")
            return

        # Проверка размера файла
        file_size = os.path.getsize(absolute_path)
        if file_size > 50 * 1024 * 1024:
            logger.error(f"Файл {filepath} превышает лимит 50 МБ: {file_size / (1024 * 1024):.2f} МБ")
            if update.callback_query:
                await update.callback_query.message.reply_text(
                    f"Файл {filepath} слишком большой для отправки (>{file_size / (1024 * 1024):.2f} МБ)."
                )
            else:
                await update.message.reply_text(
                    f"Файл {filepath} слишком большой для отправки (>{file_size / (1024 * 1024):.2f} МБ)."
                )
            return

        modification_time = os.path.getmtime(absolute_path)
        formatted_time = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(modification_time))

        with open(absolute_path, "rb") as file:
            # Используем соответствующее сообщение
            if update.callback_query:
                await update.callback_query.message.reply_document(
                    document=InputFile(file),
                    caption=f"Последнее обновление файла: {formatted_time}"
                )
            else:
                await update.message.reply_document(
                    document=InputFile(file),
                    caption=f"Последнее обновление файла: {formatted_time}"
                )

        logger.info(f"Файл {filepath} успешно отправлен.")
    except Exception as e:
        logger.exception(f"Ошибка при отправке файла {filepath}: {e}")
        if update.callback_query:
            await update.callback_query.message.reply_text("Произошла ошибка при отправке файла.")
        else:
            await update.message.reply_text("Произошла ошибка при отправке файла.")


# Функция для вывода списка файлов
async def list_files(update: Update):
    try:
        logger.info("Попытка получения списка файлов.")
        files = os.listdir(FILES_DIR)
        if files:
            file_list = "\n".join(files)
            await update.message.reply_text(f"Список файлов в директории:\n{file_list}")
            logger.info(f"Список файлов в {FILES_DIR} отправлен.")
        else:
            await update.message.reply_text("Директория пуста.")
            logger.info(f"Директория {FILES_DIR} пуста.")
    except Exception as e:
        logger.exception(f"Ошибка при получении списка файлов: {e}")
        await update.message.reply_text("Произошла ошибка при получении списка файлов.")

# Главная функция
def main():
    application = Application.builder().token(TOKEN).build()

    # Регистрация обработчиков
    application.add_handler(CommandHandler("start", start))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_password))
    #application.add_handler(CommandHandler("search_by_domain", search_by_domain))
    application.add_handler(CallbackQueryHandler(handle_action))
    application.add_handler(search_handler)

    # Запуск бота
    logger.info("Бот запущен")
    application.run_polling()

if __name__ == "__main__":
    main()