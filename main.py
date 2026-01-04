import os
import asyncio
import logging

from dotenv import load_dotenv
from aiogram import Bot, Dispatcher

from app.core.system.sheduler import start_scheduler

# Настройка логгирования
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('bot.log', encoding='utf-8'),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger(__name__)

load_dotenv()

TOKEN_BOT = os.getenv('TOKEN_BOT')
CHANNEL_ID = int(os.getenv('CHANNEL_ID'))

async def main():
    if not TOKEN_BOT:
        logger.error("❌ Не указан TOKEN_BOT в .env файле")
        return
    
    bot = Bot(token=TOKEN_BOT)
    dp = Dispatcher()
    
    logger.info("🚀 Запуск бота...")
    
    # Создаем и запускаем планировщик
    scheduler_task = asyncio.create_task(start_scheduler(bot, CHANNEL_ID))
    
    try:
        # Запускаем бота и планировщик параллельно
        await asyncio.gather(
            dp.start_polling(bot),
            scheduler_task,
            return_exceptions=True
        )

    except KeyboardInterrupt:
        logger.info("🛑 Бот остановлен пользователем")

    except Exception as e:
        logger.error(f"❌ Ошибка: {e}", exc_info=True)
        
    finally:
        await bot.session.close()
        logger.info("👋 Бот завершил работу")

if __name__ == '__main__':
    asyncio.run(main())
