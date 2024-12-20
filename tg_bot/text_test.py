from telegram import Update
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    MessageHandler,
    filters,
    ConversationHandler,
    ContextTypes,
)
import logging
import configparser
import os

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
AUTHORIZED_USERS = set()
AWAITING_PASSWORD = set()

# Состояния
WAITING_FOR_PASSWORD, WAITING_FOR_DOMAIN = range(2)

async def start_search(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Начинает процесс поиска."""
    user_id = update.effective_user.id
    username = update.effective_user.username

    if user_id not in AUTHORIZED_USERS:
        logger.info(f"Пользователь {username} (ID: {user_id}) не авторизован. Запрос пароля.")
        AWAITING_PASSWORD.add(user_id)
        await update.message.reply_text("Вы не авторизованы. Введите пароль для авторизации:")
        return WAITING_FOR_PASSWORD

    await update.message.reply_text("Введите домен для поиска:")
    return WAITING_FOR_DOMAIN

async def handle_password(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Проверяет введённый пароль."""
    user_id = update.effective_user.id
    username = update.effective_user.username

    if user_id in AUTHORIZED_USERS:
        await update.message.reply_text("Вы уже авторизованы.")
        return WAITING_FOR_DOMAIN

    if user_id in AWAITING_PASSWORD:
        if update.message.text == PASSWORD:
            AUTHORIZED_USERS.add(user_id)
            AWAITING_PASSWORD.remove(user_id)
            logger.info(f"Пользователь {username} (ID: {user_id}) успешно авторизовался.")
            await update.message.reply_text("Авторизация успешна! Теперь введите домен для поиска:")
            return WAITING_FOR_DOMAIN
        else:
            logger.warning(f"Пользователь {username} (ID: {user_id}) ввёл неверный пароль.")
            await update.message.reply_text("Неверный пароль. Попробуйте ещё раз.")
            return WAITING_FOR_PASSWORD

async def handle_domain_input(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Ищет введённый домен в файле."""
    user_id = update.effective_user.id
    username = update.effective_user.username

    if user_id not in AUTHORIZED_USERS:
        logger.warning(f"Пользователь {username} (ID: {user_id}) попытался ввести домен без авторизации.")
        await update.message.reply_text("Вы не авторизованы. Используйте команду снова.")
        return ConversationHandler.END

    domain_query = update.message.text.strip()
    logger.info(f"Пользователь {username} (ID: {user_id}) ввёл домен: {domain_query}")

    file_path = os.path.join(FILES_DIR, "A.txt")
    if not os.path.exists(file_path):
        await update.message.reply_text("Файл A.txt не найден. Убедитесь, что файл существует.")
        return ConversationHandler.END

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

async def cancel_search(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Отменяет процесс поиска."""
    await update.message.reply_text("Процесс отменён.")
    return ConversationHandler.END

# Конфигурация ConversationHandler
search_handler = ConversationHandler(
    entry_points=[CommandHandler("search_by_domain", start_search)],
    states={
        WAITING_FOR_PASSWORD: [MessageHandler(filters.TEXT & ~filters.COMMAND, handle_password)],
        WAITING_FOR_DOMAIN: [MessageHandler(filters.TEXT & ~filters.COMMAND, handle_domain_input)],
    },
    fallbacks=[CommandHandler("cancel", cancel_search)],
)

# Основное приложение
if __name__ == "__main__":
    application = ApplicationBuilder().token(TOKEN).build()

    # Добавляем обработчики
    application.add_handler(search_handler)

    logger.info("Бот запущен!")
    application.run_polling()
