import logging

from aiogram import Bot
from aiogram.types import FSInputFile
from aiogram.enums.parse_mode import ParseMode

from pathlib import Path
from datetime import datetime

from app.core.database.requests import Query
from app.core.database.models import async_session
from app.core.system.create_image import create_img

logger = logging.getLogger(__name__)

async def send(bot: Bot, channel_id: int):
    """Функция для отправки сообщения"""
    
    db = Query(async_session)
    
    try:
        # Получаем пост из БД
        post = await db.get_post()
        
        if not post:
            logger.warning("📭 Нет доступных постов для отправки")
            return
        
        logger.info(f"📝 Найден пост ID {post.id}")
        
        # Создаем изображение
        image_filename = None
        try:
            logger.info("🎨 Создаю изображение...")
            image_filename = await create_img(query=post.text, timeout=45)
            
        except Exception as img_error:
            logger.error(f"❌ Ошибка при создании изображения: {img_error}")
            image_filename = None
        
        # Отправляем сообщение
        try:
            if image_filename and Path(image_filename).exists():
                file_size = Path(image_filename).stat().st_size / 1024
                logger.info(f"🖼️ Размер изображения: {file_size:.2f} KB")
                
                photo = FSInputFile(image_filename)

                # Отправляем с изображением
                await bot.send_photo(
                    chat_id=channel_id,
                    photo=photo,
                    caption=post.text[:1024],
                    parse_mode=ParseMode.MARKDOWN
                )
                logger.info(f"✅ Отправлено фото: {image_filename}")
                
                # Удаляем временный файл
                try:
                    Path(image_filename).unlink()
                    logger.debug(f"🗑️ Удален временный файл: {image_filename}")
                except Exception as e:
                    logger.warning(f"⚠️ Не удалось удалить временный файл: {e}")
                    
            else:
                # Отправляем только текст
                await bot.send_message(
                    chat_id=channel_id,
                    text=post.text,
                    parse_mode=ParseMode.MARKDOWN
                )
                logger.info("📄 Отправлен только текст")
            
            # Обновляем статус поста
            await db.update_status(post.id)
            logger.info(f"✅ Пост ID {post.id} отправлен в {datetime.now().strftime('%H:%M:%S')}")
            
        except Exception as send_error:
            logger.error(f"❌ Ошибка при отправке: {send_error}", exc_info=True)
            # Пытаемся отправить хотя бы текст
            try:
                await bot.send_message(
                    chat_id=channel_id,
                    text=post.text,
                    parse_mode=ParseMode.MARKDOWN
                )
                await db.update_status(post.id)
                logger.info("📄 Отправлен только текст (после ошибки с фото)")
            except Exception as fallback_error:
                logger.error(f"❌ Ошибка при отправке текста: {fallback_error}")
        
    except Exception as e:
        logger.error(f'❌ Критическая ошибка: {e}', exc_info=True)
