import os
import asyncio
import schedule

from datetime import datetime
from dotenv import load_dotenv
from app.core.system.client import Client
from app.core.database.models import async_session

load_dotenv()

# Параметры для подключения
SESSION = os.getenv('SESSION') # SESSION TG
API_ID = os.getenv('API_ID') # API_ID TG
API_HASH = os.getenv('API_HASH') # API_HASH TG
YA_TOKEN = os.getenv('YA_TOKEN') # яндекс токен
PHONE_NUMBER = os.getenv('PHONE_NUMBER') # номер телефона

channel = os.getenv('CHANNEL') # куда постить
# Параметры для генерации
bot_params = {
    'chat': os.getenv('CHAT_BOT_IMG'), # Какой чат
    'query': os.getenv('COMMAND_CREATE_IMG'), # Запрос
    'path': os.getenv('SAVE_PATH') # Путь сохранения
}
yad_path = os.getenv('YAD_PATH') # яндекс путь

async def main():
    print(f"Current server time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    # Создаем подключение к клиенту
    client = Client(SESSION, API_ID, API_HASH, YA_TOKEN, async_session)
    
    try:
        # Авторизация в тг по номеру
        await client.start(PHONE_NUMBER)

        # Запускаем отправку
        await client.send_message(channel, bot_params, yad_path)
    finally:
        await client.disconnect()

def job_wrapper():
    asyncio.create_task(main())

async def schedule_jobs():
    times = ['01:00', '08:00', '15:00', '22:00']

    for time_str in times:
        schedule.every().day.at(time_str).do(job_wrapper)

    while True:
        schedule.run_pending()
        print(f"Current server time in loop: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        await asyncio.sleep(1)

if __name__ == '__main__':
    asyncio.run(schedule_jobs())