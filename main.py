from selenium import webdriver
from selenium.webdriver.common.by import By
from urllib.parse import urljoin, urlparse
import os
import requests
import time

def download_image(image_url, folder):
    try:
        img_response = requests.get(image_url, stream=True)
        img_response.raise_for_status()

        content_type = img_response.headers.get('Content-Type')
        extension = ''
        if content_type and 'image' in content_type:
            extension = '.' + content_type.split('/')[-1]
            if extension == '.jpeg':
                extension = '.jpg'

        parsed_url = urlparse(image_url)
        base_name = os.path.basename(parsed_url.path).split('?')[0]
        filename = os.path.join(folder, base_name + extension)

        counter = 1
        while os.path.exists(filename):
            filename = os.path.join(folder, f"{base_name}_{counter}{extension}")
            counter += 1

        with open(filename, 'wb') as f:
            for chunk in img_response.iter_content(chunk_size=8192):
                f.write(chunk)
        print(f"Изображение скачано: {filename}")
        return True
    except requests.exceptions.RequestException as e:
        print(f"Ошибка при скачивании {image_url}: {e}")
        print(f"Детали: {e}")
        return False
    except Exception as e:
        print(f"Произошла ошибка при обработке {image_url}: {e}")
        print(f"Детали: {e}")
        return False

def get_specific_images_with_selenium(page_url, download_folder="specific_images", browser='firefox'):
    os.makedirs(download_folder, exist_ok=True)
    driver = None
    try:
        if browser.lower() == 'chrome':
            from selenium.webdriver.chrome.service import Service as ChromeService
            from webdriver_manager.chrome import ChromeDriverManager
            service = ChromeService(ChromeDriverManager().install())
            driver = webdriver.Chrome(service=service)
        elif browser.lower() == 'firefox':
            from selenium.webdriver.firefox.service import Service as FirefoxService
            from webdriver_manager.firefox import GeckoDriverManager
            service = FirefoxService(GeckoDriverManager().install())
            driver = webdriver.Firefox(service=service)
        else:
            raise ValueError(f"Браузер '{browser}' не поддерживается. Поддерживаются 'chrome' и 'firefox'.")

        driver.get(page_url)
        time.sleep(10)

        image_wrap = driver.find_elements(By.CLASS_NAME, 'v-img-wrap')
        downloaded_count = 0
        for wrap in image_wrap:
            img_elements = wrap.find_elements(By.TAG_NAME, 'img')
            for img in img_elements:
                src = img.get_attribute('src')
                data_src = img.get_attribute('data-src')

                img_url = None
                if src:
                    img_url = src
                elif data_src:
                    img_url = data_src

                if img_url:
                    absolute_url = urljoin(page_url, img_url)
                    print(f"Найдена ссылка на изображение: {absolute_url}")
                    if download_image(absolute_url, download_folder):
                        downloaded_count += 1

        print(f"Успешно скачано {downloaded_count} изображений из целевых блоков.")

    except Exception as e:
        print(f"Произошла ошибка при использовании Selenium: {e}")
    finally:
        if driver:
            driver.quit()

if __name__ == "__main__":
    target_url = input("Введите URL страницы для скачивания изображений (Selenium - specific): ")
    browser_choice = input("Выберите браузер (chrome/firefox, по умолчанию firefox): ").lower() or 'firefox'
    get_specific_images_with_selenium(target_url, browser=browser_choice)
    print("Процесс Selenium завершен.")