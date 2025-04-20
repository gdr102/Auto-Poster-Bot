import os
import requests
from dotenv import load_dotenv

# Загружаем переменные окружения из файла .env
load_dotenv()

# Извлекаем значение OAuth-токена из переменных окружения
YA_TOKEN = os.getenv('YA_TOKEN')

# Функция для загрузки изображения на Яндекс.Диск
def upload_image_to_yandex_disk(file_path, disk_path):
    upload_url = "https://cloud-api.yandex.net/v1/disk/resources/upload"
    headers = {
        "Authorization": f"OAuth {YA_TOKEN}"
    }
    params = {
        "path": disk_path,
        "overwrite": "false"
    }

    # Получаем URL для загрузки файла
    response = requests.get(upload_url, headers=headers, params=params)
    response.raise_for_status()
    upload_link = response.json().get("href")

    # Загружаем файл на Яндекс.Диск
    with open(file_path, 'rb') as f:
        response = requests.put(upload_link, files={"file": f})
    response.raise_for_status()

    print(f"Файл загружен на Яндекс.Диск по пути: {disk_path}")

if __name__ == '__main__':
    # Путь к локальному файлу
    local_file_path = "path/to/your/image.jpg"
    # Путь на Яндекс.Диске
    yandex_disk_path = "disk:/poster/behavior_human/image.jpg"

    # Загружаем изображение на Яндекс.Диск
    upload_image_to_yandex_disk(local_file_path, yandex_disk_path)

