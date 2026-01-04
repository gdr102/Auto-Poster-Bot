import pytz
import asyncio
import logging

from aiogram import Bot
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger

from app.handlers.sender import send

logger = logging.getLogger(__name__)

async def start_scheduler(bot: Bot, channel_id: int):
    """Планировщик"""
    
    # Указываем московскую временную зону
    moscow_tz = pytz.timezone('Europe/Moscow')
    
    # Инициализируем планировщик с московским временем
    scheduler = AsyncIOScheduler(timezone=moscow_tz)
    
    try:
        # Добавляем задачи
        jobs = [
            (9, 0),   # 09:00 МСК - утренний пост
            (14, 0),  # 14:00 МСК - дневной пост  
            (20, 0)   # 20:00 МСК - вечерний пост
        ]
        
        for hour, minute in jobs:
            scheduler.add_job(
                send,
                CronTrigger(hour=hour, minute=minute, timezone=moscow_tz),
                args=[bot, channel_id],
                id=f'send_{hour:02d}_{minute:02d}',
                misfire_grace_time=300,  # 5 минут на опоздание
                coalesce=True,           # Объединять пропущенные задачи
                max_instances=1,
                replace_existing=True    # Заменять существующие задачи при перезапуске
            )
            logger.info(f"⏰ Задача добавлена: {hour:02d}:{minute:02d} МСК")
        
        scheduler.start()
        logger.info('✅ Планировщик запущен! (время МСК)')
        
        # Выводим информацию о запланированных задачах
        logger.info("📅 Расписание публикаций (МСК):")
        for job in scheduler.get_jobs():
            next_run = job.next_run_time.astimezone(moscow_tz)
            logger.info(f"   • {job.id}: {next_run.strftime('%H:%M')} МСК")
        
        # Бесконечный цикл для работы планировщика
        while True:
            await asyncio.sleep(3600)  # Проверка каждый час
            
    except Exception as e:
        logger.error(f"❌ Ошибка планировщика: {e}", exc_info=True)
        raise
