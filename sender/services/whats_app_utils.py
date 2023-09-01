import datetime
import time
from selenium.webdriver.common.by import By
from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.chrome.options import Options
from ..models import User, SenderPhoneNumber, RecipientContact, AdminData
from selenium.webdriver.support import expected_conditions as EC
from PIL import Image
from io import BytesIO
from django.db.models.query import QuerySet
from selenium.common.exceptions import TimeoutException, StaleElementReferenceException
from django.core.exceptions import ObjectDoesNotExist
import os
from selenium.webdriver import ChromeOptions
from django.conf import settings
import shutil
from rest_framework.response import Response


def get_qr_code(user, wa_id):
    return get_qr_path(user, wa_id) + "qr.png"


def is_there_active_log_session(user, wa_id):
    try:
        account = SenderPhoneNumber.objects.get(id=wa_id, owner=user)
        admin_data = AdminData.objects.first()
        sec_time_from_login_req = account.get_sec_time_from_login_req
        if sec_time_from_login_req is not None and sec_time_from_login_req < admin_data.login_duration_sec:
            return True
        else:
            return False
    except ObjectDoesNotExist:
        return None


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


def gen_qr_code(driver, user, sender_account):
    '''Получает QR-код'''
    driver.get("https://web.whatsapp.com/")
    # скриншот элемента страницы с QR-кодом
    try:
        qr_element = WebDriverWait(driver, 20).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, "canvas[aria-label='Scan me!']"))
        )
    except TimeoutException:
        print("NUUUUUL")
        driver.save_screenshot("screen.png")
        driver.quit()
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
    path = get_qr_path(user, sender_account)
    os.makedirs(path, exist_ok=True)
    im.save(path + "qr.png")
    print("QR_WAS_CREATE")


def get_qr_path(user, sender_account):
    return f"{settings.MEDIA_ROOT}qr_codes/{user.username}/{sender_account.id}/"


def login_and_set_result(check_phone_obj):
    check_phone_obj.last_login_request = datetime.datetime.now()
    check_phone_obj.save()
    res = login_to_wa_account(session_number=check_phone_obj.session_number)
    check_phone_obj.is_login = res
    check_phone_obj.login_date = datetime.datetime.now()
    check_phone_obj.save()


def login_to_wa_account(driver=None, session_number=None):
    try:
        shutil.rmtree(get_cookie_dir(session_number))
    except:
        print("CANT DELETE")
    account = SenderPhoneNumber.objects.get(id=session_number)
    account.login_date = None
    account.is_login = False
    if not driver:
        driver = create_wa_driver(session_number)
    gen_qr_code(driver, user=account.owner, sender_account=account)
    result = check_login(driver)
    driver.quit()
    try:
        shutil.rmtree(get_qr_path(account.owner, account))
    except:
        pass
    return result


def get_cookie_dir(session_id):
    base_dir = settings.BASE_DIR
    return f"{base_dir}/sources/whats_app_sessions/{session_id}"


def create_wa_driver(session_id=None):
    chrome_options = ChromeOptions()
    chrome_options.add_argument('--window-size=1920,1080')
    chrome_options.add_argument('--enable-logging')
    chrome_options.add_argument('--no-sandbox')
    chrome_options.add_argument('--disable-dev-shm-usage')
    chrome_options.add_argument(
        "user-agent=User-Agent: Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/98.0.4758.102 Safari/537.36")
    chrome_options.add_argument('--headless')  # Включение headless режима

    if session_id:
        current_dir = os.path.dirname(os.path.abspath(__file__))
        # Создаем путь к папке для сохранения профиля
        chrome_options.add_argument(f"--user-data-dir={get_cookie_dir(session_id)}")

    driver = webdriver.Chrome(options=chrome_options)
    driver.get("https://web.whatsapp.com/")
    print(session_id)
    return driver


def check_login_view(session_id):
    driver = create_wa_driver(session_id)
    result = check_login(driver)
    driver.quit()
    return result


def check_login(driver):
    admin_data = AdminData.objects.first()
    sleep_time = admin_data.sleep_time
    count_attempt = 0
    max_attempt = int(admin_data.login_duration_sec / sleep_time) + 1
    is_log = is_login(driver=driver)
    while not is_log and count_attempt < max_attempt:
        time.sleep(sleep_time)
        print("is_log=", is_log)
        count_attempt += 1
        is_log = is_login(driver=driver)
    return count_attempt < max_attempt


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
        if check_login(driver=driver):
            driver.quit()
            print(login_acc)
            return login_acc
        if driver:
            driver.quit()


def is_this_number_reg(driver, phone_number) -> bool:
    driver.get(f"https://web.whatsapp.com/send?phone={phone_number}&text=test")
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
        contact.is_phone_whatsapp_reg = is_this_number_reg(driver, contact.phone)
        contact.whats_reg_checked_data = datetime.datetime.now()
        contact.save()
    driver.quit()
