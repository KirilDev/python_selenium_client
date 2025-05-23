import requests
import os
from urllib.parse import urlparse

image_urls = [
    "http://www.periodika.lv/periodika2-viewer/img/block?pid=P6_TB00009&issue=558526",
    "http://www.periodika.lv/periodika2-viewer/img/block?pid=P6_TB00010&issue=558526",
]

folder = "images"
os.makedirs(folder, exist_ok=True)

for img_url in image_urls:
    try:
        img_response = requests.get(img_url, stream=True)
        img_response.raise_for_status()

        content_type = img_response.headers.get('Content-Type')
        extension = ''
        if content_type and 'image' in content_type:
            extension = '.' + content_type.split('/')[-1]
            if extension == '.jpeg':
                extension = '.jpg'

        parsed_url = urlparse(img_url)
        base_name = os.path.basename(parsed_url.path).split('?')[0]
        filename = os.path.join(folder, base_name + extension)

        # Ensure unique filename
        counter = 1
        while os.path.exists(filename):
            filename = os.path.join(folder, f"{base_name}_{counter}{extension}")
            counter += 1

        with open(filename, 'wb') as f:
            for chunk in img_response.iter_content(chunk_size=8192):
                f.write(chunk)
        print(f"Изображение сохранено как: {filename}")

    except requests.exceptions.RequestException as e:
        print(f"Ошибка при скачивании изображения {img_url}: {e}")
        print(f"Детали ошибки: {e}") # Дополнительная информация об ошибке
    except Exception as e:
        print(f"Произошла ошибка: {e}")
        print(f"Детали ошибки: {e}") # Дополнительная информация об ошибке