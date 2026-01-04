import os
import base64
import asyncio

from datetime import datetime
from dotenv import load_dotenv
from openai import AsyncOpenAI

load_dotenv()

async def create_img(query: str, timeout: int = 30):
    """Создание изображения"""

    client = AsyncOpenAI(api_key=os.getenv('TOKEN_AI'))

    PROMPT="""
Create a square (1:1 ratio) illustration that visually represents the following concept about change after a breakup:
Concept: '{query}'
Style: Modern digital art, emotional but not sad, symbolic representation of personal growth and transformation. Use a color palette that represents renewal and positive change."""
    
    try:
        prompt = PROMPT.format(query=query)
        
        print(f"🎨 Создаю изображение для промпта: {prompt[:100]}...")

        # Пытаемся несколько раз с ретраями
        max_retries = 3
        for attempt in range(max_retries):
            try:
                print(f"🖼️ Попытка {attempt + 1} создания изображения...")
                
                img = await asyncio.wait_for(
                    client.images.generate(
                        model="dall-e-3",
                        prompt=prompt,
                        n=1,
                        size="1024x1024",
                        response_format="b64_json"
                    ),
                    timeout=timeout
                )
                
                break  # Успешно, выходим из цикла
                
            except asyncio.TimeoutError:
                if attempt == max_retries - 1:
                    raise
                print(f"⚠️ Таймаут, повторяем через 2 секунды...")
                await asyncio.sleep(2)
            except Exception as e:
                if attempt == max_retries - 1:
                    raise
                print(f"⚠️ Ошибка: {e}, повторяем...")
                await asyncio.sleep(2)
        
        # Проверяем результат
        if not img.data or not hasattr(img.data[0], 'b64_json'):
            print("❌ Не удалось получить изображение")
            return None
        
        # Создаем имя файла
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"temp/image_{timestamp}.png"
        
        # Создаем директорию
        os.makedirs(os.path.dirname(filename), exist_ok=True)
        
        # Сохраняем изображение
        image_data = img.data[0].b64_json
        image_bytes = base64.b64decode(image_data)
        
        with open(filename, "wb") as f:
            f.write(image_bytes)
        
        print(f"✅ Изображение сохранено: {filename}")
        return filename
        
    except asyncio.TimeoutError:
        print(f"❌ Таймаут при создании изображения ({timeout} сек)")
    except Exception as e:
        print(f"❌ Ошибка при создании изображения: {e}")
    
    return None
