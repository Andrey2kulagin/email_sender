import time

from selenium.webdriver.common.by import By
from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.chrome.options import Options
from ..models import User, SenderPhoneNumber
from selenium.webdriver.support import expected_conditions as EC
from PIL import Image
from io import BytesIO


def gen_qr_code(driver):
    '''Получает QR-код'''
    driver.get("https://web.whatsapp.com/")
    # скриншот элемента страницы с QR-кодом
    qr_element = WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.CSS_SELECTOR, "canvas[aria-label='Scan me!']"))
    )
    location = qr_element.location
    size = qr_element.size
    png = driver.get_screenshot_as_png()
    im = Image.open(BytesIO(png))  # создание PIL Image из байтов png-изображения
    left = location['x'] - 20
    top = location['y'] - 20
    right = location['x'] + size['width'] + 20
    bottom = location['y'] + size['height'] + 20
    im = im.crop((left, top, right, bottom))  # обрезка изображения по размерам элемента
    # сохранение изображения в файл
    im.save('qr_code.png')


def login(driver):
    gen_qr_code(driver)
    count_attempt = 0
    max_attempt = 15
    sleep_time = 5
    while not is_login(driver) and count_attempt < max_attempt:
        time.sleep(sleep_time)
        count_attempt += 1
    return count_attempt < max_attempt


def get_cookie():
    cookie_dir = "cookies"
    phone_number = input('enter the number you will be entering. If you want to stop, enter "stop"\n')
    options = webdriver.ChromeOptions()
    options.add_argument('--headless')
    options.add_argument(f'--user-data-dir=./{cookie_dir}/{phone_number}')
    driver = webdriver.Chrome(options=options)
    driver.get("https://web.whatsapp.com/")
    time.sleep(10)
    return login(driver)


def is_login(session_id: str, driver=None):
    """
    проверка, произошел ли вход в аккаунт
    """
    if not driver:
        chrome_options = Options()
        chrome_options.add_argument(f'--user-data-dir=./whats_app_session/{session_id}')
        chrome_options.add_argument("--headless")
        driver = webdriver.Chrome(options=chrome_options)
        driver.maximize_window()
        driver.get("https://web.whatsapp.com/")
    try:
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located(
                (By.CSS_SELECTOR, "._64p9P"))
        )
        return True
    except TimeoutError:
        return False


def get_active_whatsapp_account(user: User) -> SenderPhoneNumber:
    """
    проверка авторизован ли аккаунт пользователя
    """
    login_whats_app_acc = SenderPhoneNumber.objects.filter(owner=user, is_login=True)
    for login_acc in login_whats_app_acc:
        if is_login(login_acc.session_number):
            return login_acc
