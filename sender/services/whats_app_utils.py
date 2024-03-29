import datetime
import time
from selenium.webdriver.common.by import By
from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.chrome.options import Options
from ..models import User, SenderPhoneNumber, RecipientContact, AdminData, ContactCheckStatistic
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
from django.utils import timezone
from .all_service import generate_random_string
from django.core.files.base import ContentFile


def check_contact_qs_wa(user_id, stat_id, is_all=False, groups=None, contacts=None):
    stat = ContactCheckStatistic.objects.get(id=stat_id)
    user = User.objects.get(id=user_id)
    if not is_all:
        all_checking_obj = get_user_queryset(groups, contacts, user)
    else:
        all_checking_obj = RecipientContact.objects.filter(owner=user, phone__isnull=False, is_phone_whatsapp_reg=False)
    auth_account = get_active_whatsapp_account(user=user)
    if auth_account:
        check_whatsapp_contacts(all_checking_obj, auth_account)
        stat.is_check_finished = True
        stat.status_data = {"status_code": 200, "message": "Все аккаунты, которые вы передали были проверены"}
        stat.save()
    else:
        stat.is_check_finished = True
        stat.status_data = {"status_code": 400, "message": "Авторизуйтесь хотя бы в 1 аккаунте WhatsApp"}
        stat.save()


def check_wa_run(wa_id: int):
    """
    Запускает проверку входа в аккаунт
    """
    check_phone_obj = SenderPhoneNumber.objects.get(id=wa_id)
    check_phone_obj.last_login_request = timezone.now()
    check_phone_obj.save()
    if not check_phone_obj.is_login:
        return None
    check_phone_obj.is_login = False
    check_phone_obj.login_date = None
    check_phone_obj.is_login_start = True
    check_phone_obj.save()
    print("Начальные данные выставлены")
    if check_login_view(check_phone_obj.session_number, True):
        print("Проверено")
        check_phone_obj.is_login = True
        check_phone_obj.login_date = timezone.now()
        check_phone_obj.save()
    check_phone_obj.is_login_start = False
    check_phone_obj.save()


def check_is_login_wa_account_obj(user: User, wa_id: int):
    """ физическая проверка состояния. Войдено или нет"""
    try:
        account = SenderPhoneNumber.objects.get(owner=user, id=wa_id)
        admin_data = AdminData.objects.first()
        is_login_request_and_time_enough = account.get_sec_time_from_login_req is not None and account.get_sec_time_from_login_req < admin_data.login_duration_sec
        if account.is_login_start and is_login_request_and_time_enough:
            return 404, {"message": "Аккаунт находится на проверке, подождите"}
        elif account.get_sec_time_from_login_req is None:
            return 404, {"message": "Аккаунт не входился"}
        is_login_and_have_time = (
                account.get_sec_time_from_last_login is not None and account.get_sec_time_from_last_login <= admin_data.check_login_time_sec)
        not_login_but_have_time = account.get_sec_time_from_login_req < admin_data.login_duration_sec + admin_data.check_login_time_sec
        if is_login_and_have_time or not_login_but_have_time:
            return 200, {"is_login": account.is_login}
        else:
            return 408, {"message": "Время проверки этого аккаунта истекло"}
    except ObjectDoesNotExist:
        return 404, {"message": "Такого аккаунта не существует"}


def get_qr_handler(user: User, wa_id: int) -> tuple[int, dict[str:str]]:
    """ Функция для получения qr-кода во время входа"""
    try:
        account = SenderPhoneNumber.objects.get(id=wa_id, owner=user)
        admin_data = AdminData.objects.first()
        sec_time_from_login_req = account.get_sec_time_from_login_req
        if sec_time_from_login_req is not None and sec_time_from_login_req < admin_data.login_duration_sec:
            if account.qr_code.url is not None:
                return 200, {"url": account.qr_code.url}
            else:
                return 422, {"message": "qr пока не сгенерирован"}
        else:
            return 404, {"message": "Нет активных сессий входа, сгенерируйте новый qr"}
    except ObjectDoesNotExist:
        return 404, {"message": "Нет такого аккаунта или он вам не принадлежит"}


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


def gen_qr_code(driver: webdriver, user: User, sender_account: SenderPhoneNumber):
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
    buffer = BytesIO()
    im.save(buffer, format="PNG")
    image_data = buffer.getvalue()
    sender_account.qr_code.save(f'qr_{sender_account.id}_{generate_random_string(4)}.png', ContentFile(image_data))
    sender_account.last_login_request = timezone.now()
    sender_account.save()
    print("QR_WAS_CREATE")


def login_and_set_result(check_phone_obj):
    """ входит в аккаунт общая функция для celery"""
    check_phone_obj.is_login_start = True
    check_phone_obj.save()
    res = login_to_wa_account(session_number=check_phone_obj.session_number)
    check_phone_obj.is_login = res
    check_phone_obj.login_date = timezone.now()
    check_phone_obj.is_login_start = False
    check_phone_obj.save()


def login_to_wa_account(driver: webdriver = None, session_number: int = None):
    """Входит в whatsApp инициирует драйвер и генерирует qr"""
    try:
        shutil.rmtree(get_cookie_dir(session_number))
    except:
        print("CANT DELETE")
    account = SenderPhoneNumber.objects.get(id=session_number)
    account.login_date = None
    account.is_login = False
    account.save()
    if not driver:
        driver = create_wa_driver(session_number)
    gen_qr_code(driver, user=account.owner, sender_account=account)
    result = check_login(driver)
    driver.quit()
    # удаление qr
    if account.qr_code is not None:
        account.qr_code.delete()
    account.save()
    return result


def get_cookie_dir(session_id: int):
    """ генерирует путь к папке с куки"""
    base_dir = settings.BASE_DIR
    return f"{base_dir}/sources/whats_app_sessions/{session_id}"


def create_wa_driver(session_id=None):
    """Создает драйвер для всей этой системы"""
    chrome_options = ChromeOptions()
    chrome_options.add_argument('--window-size=1920,1080')
    chrome_options.add_argument('--enable-logging')
    chrome_options.add_argument('--no-sandbox')
    chrome_options.add_argument('--disable-dev-shm-usage')
    chrome_options.add_argument(
        "user-agent=User-Agent: Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/98.0.4758.102 Safari/537.36")
    chrome_options.add_argument('--headless')  # Включение headless режима

    if session_id:
        chrome_options.add_argument(f"--user-data-dir={get_cookie_dir(session_id)}")

    driver = webdriver.Chrome(options=chrome_options)
    driver.get("https://web.whatsapp.com/")
    print(session_id)
    return driver


def check_login_view(session_id, is_repeat_check=False):
    """ Проверяет авторизован ли WhatsApp без входа"""
    driver = create_wa_driver(session_id)
    result = check_login(driver, is_repeat_check)
    driver.quit()
    return result


def check_login(driver, is_repeat_check=False):
    """ проверяет авторизацию"""
    admin_data = AdminData.objects.first()
    count_attempt = 0
    sleep_time = admin_data.sleep_time
    if is_repeat_check:
        max_attempt = admin_data.repeat_check_attempt
    else:
        max_attempt = int(abs(admin_data.login_duration_sec - 5) / sleep_time) + 1
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
    """Проверяет зарегистрирован ли номер в whatsApp"""
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
        contact.whats_reg_checked_data = timezone.now()
        contact.save()
    driver.quit()
