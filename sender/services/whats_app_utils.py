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
from selenium.common.exceptions import TimeoutException, StaleElementReferenceException
from django.core.exceptions import ObjectDoesNotExist


def get_user_queryset(groups: list[int], contacts: list[int], user: User):
    """
    возвращает список контактов пользователя по списку их id и групп
    """
    total_queryset = []
    for group in groups:
        total_queryset += [i for i in RecipientContact.objects.filter(owner=user, contact_group__id=group)]
    for contact in contacts:
        try:
            total_queryset.append(RecipientContact.objects.get(owner=user, id=contact))
        except ObjectDoesNotExist:
            continue
    total_queryset = list(set(total_queryset))
    return total_queryset


def gen_qr_code(driver):
    '''Получает QR-код'''
    driver.get("https://web.whatsapp.com/")
    # скриншот элемента страницы с QR-кодом
    try:
        qr_element = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, "canvas[aria-label='Scan me!']"))
        )
    except TimeoutException:
        return 0
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
    print("after gen_qr")
    count_attempt = 0
    max_attempt = 15
    sleep_time = 10
    is_log = is_login(driver=driver)
    while not is_log and count_attempt < max_attempt:
        time.sleep(sleep_time)
        print("is_log=", is_log)
        count_attempt += 1
        is_log = is_login(driver=driver)
    driver.quit()
    return count_attempt < max_attempt


def create_wa_driver(session_id=None):
    chrome_options = Options()
    if session_id:
        chrome_options.add_argument(f'--user-data-dir=./whats_app_session/{session_id}')

    # chrome_options.add_argument("--headless")
    driver = undetected_chromedriver.Chrome(options=chrome_options)
    driver.get("https://web.whatsapp.com/")
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


def get_active_whatsapp_account(user: User, driver=None) -> SenderPhoneNumber:
    'выбор авторизованного аккаунта whatsApp'
    print("get_active_whatsapp_account")
    login_whats_app_acc = SenderPhoneNumber.objects.filter(owner=user, is_login=True)
    print("len = ", len(login_whats_app_acc))
    for login_acc in login_whats_app_acc:
        if not driver:
            driver = create_wa_driver(session_id=login_acc.session_number)
        if login_to_wa_account(driver=driver, session_number=login_acc.session_number):
            driver.quit()
            print(login_acc)
            return login_acc
        if driver:
            driver.quit()


def is_this_number_reg(driver) -> bool:
    try:
        wrong_phone_div = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, ".f8jlpxt4.iuhl9who"))
        )
        try:
            if wrong_phone_div.text == "Неверный номер телефона.":
                return False
            else:
                raise TimeoutException
        except StaleElementReferenceException:
            raise TimeoutException
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
    driver = create_wa_driver(auth_account.session_number)
    for contact in contacts_queryset:
        driver.get(f"https://web.whatsapp.com/send?phone={contact.phone}&text=test")
        print(is_this_number_reg(driver))
        contact.is_phone_whatsapp_reg = is_this_number_reg(driver)
        contact.whats_reg_checked_data = datetime.datetime.now()
        contact.save()
    driver.quit()
