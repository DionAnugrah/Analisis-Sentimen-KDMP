import os
import sys
import time

from selenium import webdriver
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

URL = os.environ.get("STREAMLIT_APP_URL")
if not URL:
    sys.exit("STREAMLIT_APP_URL belum diatur")

WAKE_BUTTON = (By.XPATH, "//button[contains(., 'get this app back up')]")

options = Options()
options.add_argument("--headless=new")
options.add_argument("--no-sandbox")
options.add_argument("--disable-dev-shm-usage")
options.add_argument("--window-size=1280,800")

driver = webdriver.Chrome(options=options)

try:
    print(f"Membuka {URL}")
    driver.get(URL)

    try:
        button = WebDriverWait(driver, 20).until(EC.element_to_be_clickable(WAKE_BUTTON))
        print("App sedang tidur, mengklik tombol wake-up...")
        button.click()
        WebDriverWait(driver, 60).until(EC.invisibility_of_element_located(WAKE_BUTTON))
        print("Tombol hilang, app sedang dibangunkan.")
        time.sleep(90)
    except TimeoutException:
        print("Tombol wake-up tidak ditemukan, app sudah aktif.")
        time.sleep(30)

    print("Selesai.")
finally:
    driver.quit()
