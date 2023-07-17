import datetime
import time
from selenium.webdriver.common.by import By
import undetected_chromedriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.chrome.options import Options
from ..models import User, SenderPhoneNumber, RecipientContact
from selenium.webdriver.support import expected_conditions as EC
from PIL import Image
from io import BytesIO
from django.db.models.query import QuerySet
from selenium.common.exceptions import TimeoutException


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


def login_to_wa_account(driver=None, session_number=None):
    if not driver:
        driver = create_wa_driver(session_number)
    gen_qr_code(driver)
    count_attempt = 0
    max_attempt = 15
    sleep_time = 10
    while not is_login(driver=driver) and count_attempt < max_attempt:
        time.sleep(sleep_time)
        count_attempt += 1
    return count_attempt < max_attempt


def create_wa_driver(session_id=None):
    chrome_options = Options()
    if session_id:
        chrome_options.add_argument(f'--user-data-dir=./whats_app_session/{session_id}')

    # chrome_options.add_argument("--headless")
    driver = undetected_chromedriver.Chrome(options=chrome_options)
    print("akasklhlsahlk")
    driver.get("https://web.whatsapp.com/")
    print("get whatsapp")
    return driver


def is_login(session_id: str = None, driver=None):
    """
    проверка, произошел ли вход в аккаунт
    """
    if not driver:
        driver = create_wa_driver(session_id)
    try:
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located(
                (By.CSS_SELECTOR, "._64p9P"))
        )
        return True
    except TimeoutException:
        return False


def get_active_whatsapp_account(user: User) -> SenderPhoneNumber:
    'выбор авторизованного аккаунта whatsApp'
    login_whats_app_acc = SenderPhoneNumber.objects.filter(owner=user, is_login=True)
    print(len(login_whats_app_acc))
    for login_acc in login_whats_app_acc:
        if is_login(login_acc.session_number):
            return login_acc


def is_this_number_reg(driver) -> bool:
    try:
        wrong_phone_div = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, ".f8jlpxt4.iuhl9who"))
        )
        if wrong_phone_div.text == "Неверный номер телефона.":
            return False
        else:
            raise
    except TimeoutException:
        try:
            WebDriverWait(driver, 10).until(
                EC.presence_of_element_located(
                    (By.CSS_SELECTOR, ".tvf2evcx.oq44ahr5.lb5m6g5c.svlsagor.p2rjqpw5.epia9gcq"))
            )
            return True
        except TimeoutException:
            return False


def check_whatsapp_contacts(contacts_queryset: QuerySet[RecipientContact], auth_account):
    # если профиль для проверки авторизован, то проверяем, иначе авторизуемся
    chrome_options = Options()
    chrome_options.add_argument(f'--user-data-dir=./whats_app_session/{auth_account.session_number}')
    # chrome_options.add_argument("--headless")
    driver = undetected_chromedriver.Chrome(options=chrome_options)
    driver.maximize_window()
    driver.get("https://web.whatsapp.com")
    for contact in contacts_queryset:
        driver.get(f"https://web.whatsapp.com/send?phone={contact.phone}")
        print(is_this_number_reg(driver))
        contact.is_phone_whatsapp_reg = is_this_number_reg(driver)
        contact.whats_reg_checked_data = datetime.datetime.now()
