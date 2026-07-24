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
    logger.error("❌ BOT_TOKEN не найден в переменных окружения!")
    sys.exit(1)

BASE_DIR = Path(__file__).resolve().parent
IMAGE_PATH = BASE_DIR / "ogo.jpg"

if not IMAGE_PATH.exists():
    logger.warning(f"⚠️ Файл картинки не найден: {IMAGE_PATH}")
else:
    logger.info(f"✅ Картинка найдена: {IMAGE_PATH}")


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Бот на связи! Режим секретаря активен.")


async def handle_ogo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    # БЕЗОПАСНОЕ извлечение сообщения: проверяем и обычный чат, и "Бизнес-режим" (секретарь)
    msg = update.message or update.business_message
    
    # Если сообщения нет или в нем нет текста (например, это просто стикер или фото) — игнорируем
    if not msg or not msg.text:
        return

    text = msg.text.lower()
    
    # Проверяем слово "ого" как отдельное слово
    if re.search(r'\bого\b', text, re.IGNORECASE):
        logger.info(f"🎯 Найдено слово 'ого' в чате {msg.chat.id}. Отправляю картинку...")
        try:
            with open(IMAGE_PATH, 'rb') as photo:
                await msg.reply_photo(photo=photo)
            logger.info("✅ Картинка успешно отправлена")
        except Exception as e:
            logger.error(f"❌ Ошибка при отправке картинки: {e}")
            await msg.reply_text(f"Ошибка при отправке: {e}")


async def debug_catch_all(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Временный отладчик: ловит ВСЕ нестандартные события, чтобы мы видели, что шлет Telegram"""
    logger.warning(f"🕵️ Пойман нестандартный апдейт (не текст): {type(update).__name__}")


def main():
    logger.info("🚀 Запуск бота...")
    
    request = HTTPXRequest(
        connection_pool_size=8,
        connect_timeout=30.0,
        read_timeout=30.0,
        write_timeout=30.0,  # Увеличенный таймаут для загрузки картинок
        pool_timeout=30.0
    )
    
    application = Application.builder().token(BOT_TOKEN).request(request).build()

    application.add_handler(CommandHandler("start", start))
    
    # 1. Основной обработчик для текста (работает и для message, и для business_message, если они проходят фильтр)
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_ogo))
    
    # 2. Отладочный обработчик для всего остального (служебные сообщения, бизнес-подключения и т.д.)
    application.add_handler(MessageHandler(filters.ALL, debug_catch_all))

    logger.info("✅ Бот запущен и готов к работе")
    # allowed_updates=Update.ALL_TYPES гарантирует, что мы получаем и business_message тоже
    application.run_polling(allowed_updates=Update.ALL_TYPES)


if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        logger.error(f"💥 Критическая ошибка при запуске: {e}")
        sys.exit(1)