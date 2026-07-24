from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes
import re
import os
import logging
from pathlib import Path

# Настройка логирования
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# Получение токена из переменных окружения
BOT_TOKEN = os.environ.get("BOT_TOKEN")
if not BOT_TOKEN:
    raise ValueError("❌ BOT_TOKEN не установлен в переменных окружения!")

# Путь к картинке (относительный, работает на любой ОС)
BASE_DIR = Path(__file__).resolve().parent
IMAGE_PATH = BASE_DIR / "ogo.jpg"

if not IMAGE_PATH.exists():
    logger.warning(f"⚠️ Файл картинки не найден: {IMAGE_PATH}")


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обработчик команды /start"""
    await update.message.reply_text(
        "Привет! Я бот-секретарь. Отправь мне сообщение со словом 'ого' "
        "в любом регистре, и я пришлю картинку!"
    )


async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обработчик текстовых сообщений"""
    if not update.message or not update.message.text:
        return

    text = update.message.text.lower()

    # Проверяем наличие слова "ого" в любом регистре
    if re.search(r'\bого\b', text, re.IGNORECASE):
        try:
            with open(IMAGE_PATH, 'rb') as photo:
                await update.message.reply_photo(photo=photo)
        except Exception as e:
            logger.error(f"Ошибка при отправке картинки: {e}")
            await update.message.reply_text(f"Ошибка при отправке картинки: {e}")


def main():
    """Запуск бота"""
    logger.info("🚀 Запуск бота...")
    
    application = Application.builder().token(BOT_TOKEN).build()

    application.add_handler(CommandHandler("start", start))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

    logger.info("✅ Бот запущен и готов к работе")
    application.run_polling(allowed_updates=Update.ALL_TYPES)


if __name__ == "__main__":
    main()