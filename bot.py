import os
import sys
import logging
from pathlib import Path
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes
from telegram.request import HTTPXRequest
import re

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO,
    force=True
)
logger = logging.getLogger(__name__)

BOT_TOKEN = os.environ.get("BOT_TOKEN")
if not BOT_TOKEN:
    logger.error("❌ BOT_TOKEN не найден!")
    sys.exit(1)

BASE_DIR = Path(__file__).resolve().parent
IMAGE_PATH = BASE_DIR / "ogo.jpg"

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Бот на связи!")

# --- ВРЕМЕННЫЙ ТЕСТОВЫЙ ОБРАБОТЧИК ---
async def debug_all_messages(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Ловит ВСЕ сообщения и пишет в лог, чтобы мы поняли, доходят ли они вообще"""
    chat_type = update.message.chat.type
    chat_title = update.message.chat.title if update.message.chat.title else "Личный чат"
    text = update.message.text
    
    logger.info(f"📩 ПОЛУЧЕНО СООБЩЕНИЕ! Тип чата: {chat_type}, Название: {chat_title}, Текст: '{text}'")
    
    # Если это тот самый "диалог", бот сразу ответит, чтобы вы увидели реакцию
    if chat_type in ['group', 'supergroup']:
        await update.message.reply_text(f"Я вижу сообщение в чате '{chat_title}': {text}")

async def handle_ogo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text.lower()
    if re.search(r'\bого\b', text, re.IGNORECASE):
        try:
            with open(IMAGE_PATH, 'rb') as photo:
                await update.message.reply_photo(photo=photo)
            logger.info("✅ Картинка успешно отправлена")
        except Exception as e:
            logger.error(f"❌ Ошибка при отправке картинки: {e}")

def main():
    logger.info("🚀 Запуск бота...")
    
    request = HTTPXRequest(
        connection_pool_size=8,
        connect_timeout=30.0,
        read_timeout=30.0,
        write_timeout=30.0,
        pool_timeout=30.0
    )
    
    application = Application.builder().token(BOT_TOKEN).request(request).build()

    application.add_handler(CommandHandler("start", start))
    
    # ВАЖНО: Порядок хендлеров имеет значение! Сначала общий дебаг, потом частный
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, debug_all_messages))
    application.add_handler(MessageHandler(filters.Regex(r'(?i)\bого\b'), handle_ogo))

    logger.info("✅ Бот запущен и готов к работе")
    application.run_polling(allowed_updates=Update.ALL_TYPES)

if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        logger.error(f"💥 Критическая ошибка: {e}")
        sys.exit(1)