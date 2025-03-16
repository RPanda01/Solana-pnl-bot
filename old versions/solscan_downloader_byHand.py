import time
import os
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager

def download_solscan_csv(wallet, save_path):
    # Настройки Chrome (изменение папки загрузки)
    chrome_options = Options()
    prefs = {"download.default_directory": os.path.dirname(save_path)}
    chrome_options.add_experimental_option("prefs", prefs)
    
    # Запуск браузера
    service = Service(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service, options=chrome_options)
    driver.set_window_size(1920, 1080)

    try:
        # Открываем страницу Solscan
        solscan_url = f"https://solscan.io/account/{wallet}?exclude_amount_zero=true#transfers"
        driver.get(solscan_url)
        time.sleep(5)  # Ждём загрузки страницы

        # Ищем кнопку "Export CSV" и нажимаем
        export_button = driver.find_element(By.XPATH, "//button[div[contains(text(), 'Export CSV')]]")
        ActionChains(driver).move_to_element(export_button).click().perform()
        print("✅ Клик по 'Export CSV'")

         # 2️⃣ Ждём появления окна и кликаем по кнопке "Download"
        wait = WebDriverWait(driver, 10)
        download_button = wait.until(EC.element_to_be_clickable((By.XPATH, "//button[contains(text(), 'Download')]")))
        download_button.click()
        print("✅ Клик по 'Download'")

        # Ждём загрузки файла
        time.sleep(5)

        print(f"✅ CSV-файл загружен в папку: {os.path.dirname(save_path)}")
    
        # Путь к файлу
        files_dir = os.path.dirname(save_path)
        files = [f for f in os.listdir(files_dir) if f.startswith(f"export_transfer_{wallet}_")]

        if files:
            # Находим файл по паттерну
            default_filename = os.path.join(files_dir, files[0])  # Первое совпадение
            new_filename = os.path.join(files_dir, f"trans_{wallet}.csv")  # Новый формат имени
        
            if os.path.exists(default_filename):  # Проверяем существование файла
                os.rename(default_filename, new_filename)
                print(f"📁 Файл переименован в {new_filename}")
            else:
                print(f"❌ Файл с именем {default_filename} не найден!")
        else:
            print(f"❌ Не найден файл, начинающийся с 'export_transfer_{wallet}_'!")

    except Exception as e:
        print(f"❌ Ошибка: {e}")

    finally:
        driver.quit()

# 🔹 Пример использования
# wallet = "3mQKQtTvzqMSHk9BMewU98G1uNZqywkoCGimt2k7XdVW"  # Укажи свой кошелек
# download_solscan_csv(wallet)
