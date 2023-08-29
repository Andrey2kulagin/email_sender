import time
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from PIL import Image
from selenium.webdriver.common.by import By
from io import BytesIO
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from ..models import UserLetterText, SenderPhoneNumber, ContactGroup, RecipientContact
from django.core.exceptions import ObjectDoesNotExist
from rest_framework import serializers


def wa_text_id_validate(text_id, user):
    try:
        UserLetterText.objects.exclude(text=None).get(id=text_id, user=user)
    except ObjectDoesNotExist:
        raise serializers.ValidationError("У вас нет такого текста для рассылки или текст письма не заполнен")


def wa_send_account_validate(data, user):
    send_accounts = data.get("send_accounts")
    if len(send_accounts) == 0:
        raise serializers.ValidationError("Передайте хотя бы 1 аккаунт для рассылки")
    for i in send_accounts:
        try:
            id_str, letter_count_str = i.split("-")
            try:
                account_id = int(id_str)
            except ValueError:
                raise serializers.ValidationError(f"Ошибка в send_accounts в {i} id должно быть числом")
            try:
                letter_count = int(letter_count_str)
            except ValueError:
                raise serializers.ValidationError(f"Ошибка в send_accounts в {i} letter_count должно быть числом")
            try:
                account_obj = SenderPhoneNumber.objects.get(owner=user, id=account_id)
                if not account_obj.is_login:
                    raise serializers.ValidationError(
                        f"Ошибка в send_accounts в {i} Требуется войти в аккаунт с ID {account_id}")
            except ObjectDoesNotExist:
                raise serializers.ValidationError(f"Ошибка в send_accounts в {i} У вас нет аккаунта с id {account_id}")
        except ValueError:
            raise serializers.ValidationError(f"Ошибка в send_accounts в {i} не хватает аргументов")


def wa_contact_group_validate(contact_groups, user):
    for i in contact_groups:
        try:
            ContactGroup.objects.get(id=i, user=user)
        except ObjectDoesNotExist:
            raise serializers.ValidationError(f"У вас нет группы с id {i}")


def wa_contacts_validate(contacts, user):
    for contact in contacts:
        try:
            RecipientContact.objects.get(owner=user, id=contact)
        except ObjectDoesNotExist:
            raise serializers.ValidationError(f"У вас нет контакта с id {contact}")


def wa_sender_run_validate(data, user):
    text_id = data.get("text_id")
    if text_id is not None:
        wa_text_id_validate(text_id, user)
    elif data.get("text") is None:
        raise serializers.ValidationError("Должен быть заполнен контент письма. Либо текст, либо text_id")
    contact_groups = data.get("contacts_group")
    contacts = data.get("contacts")
    if contact_groups is None and contacts is None:
        raise serializers.ValidationError("Передайте хотя бы одну группу или получателя")
    wa_send_account_validate(data, user)
    wa_contact_group_validate(contact_groups, user)
    wa_contacts_validate(contacts, user)
    return data


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


def is_this_number_reg(driver) -> bool:
    try:
        wrong_phone_div = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, ".f8jlpxt4.iuhl9who"))
        )
        if wrong_phone_div.text == "Неверный номер телефона.":
            return False
        else:
            raise
    except:
        try:
            WebDriverWait(driver, 10).until(
                EC.presence_of_element_located(
                    (By.CSS_SELECTOR, ".tvf2evcx.oq44ahr5.lb5m6g5c.svlsagor.p2rjqpw5.epia9gcq"))
            )
            return True
        except:
            return False


def send_msg(driver, phone_no, text):
    print(phone_no)
    message = text
    driver.get(f"https://web.whatsapp.com/send?phone={phone_no}&text={message}")
    # time.sleep(500000000)
    if is_this_number_reg(driver):
        send_button = driver.find_element(By.CSS_SELECTOR, ".tvf2evcx.oq44ahr5.lb5m6g5c.svlsagor.p2rjqpw5.epia9gcq")
        send_button.click()
        print("сообщение успешно отправлено")
    else:
        print("Нет такого номера")


def is_login(driver):
    try:
        driver.find_element(By.CSS_SELECTOR, "._64p9P")
        return True
    except:
        return False


def login(driver):
    gen_qr_code(driver)
    count_attempt = 0
    max_attempt = 15
    sleep_time = 5
    while not is_login(driver) and count_attempt < max_attempt:
        time.sleep(sleep_time)
        count_attempt += 1
    if count_attempt < max_attempt:
        return True
    else:
        return False


def get_text():
    text = open("text.txt", encoding='utf-8').read().replace("\n", "%0A")
    return text


def get_numbers():
    f = open("base_of_numbers.txt")
    return set(f.readlines())


def phone_normalize(number: str) -> str:
    out_str = ""
    is_firs_symb = True
    for symb in number:
        digits = "0123456789"
        if is_firs_symb:
            digits = '+' + digits
            is_firs_symb = False
        if symb in digits:
            out_str += symb
    if out_str[0] == '+' and out_str[1] == '7':
        out_str = '7' + out_str[2::]
    elif out_str[0] == '8':
        out_str = '7' + out_str[1::]
    return out_str


def main():
    options = Options()
    driver = webdriver.Chrome(options=options)
    if login(driver):
        print("Вы успешно вошли")
        text = get_text()
        numbers = get_numbers()
        for number in numbers:
            number = phone_normalize(number)
            send_msg(driver, number, text)

    else:
        print("Войти не удалось")
