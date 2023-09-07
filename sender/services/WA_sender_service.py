import datetime
import time
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from PIL import Image
from selenium.webdriver.common.by import By
from io import BytesIO
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from ..models import UserLetterText, SenderPhoneNumber, ContactGroup, RecipientContact, UserSenders, \
    UserSendersContactStatistic
from django.core.exceptions import ObjectDoesNotExist
from rest_framework import serializers
from ..services.whats_app_utils import check_login_view, create_wa_driver, is_this_number_reg
from selenium.common.exceptions import TimeoutException, NoAlertPresentException, UnexpectedAlertPresentException
from django.utils import timezone


def set_error_message_to_statistic(statistic, message):
    statistic.is_send = False
    statistic.comment = message
    statistic.save()


def sender_handler(validated_data, user, cure_sender_obj_id):
    text = get_text(validated_data, user)
    send_accounts = send_accounts_parse(validated_data)
    all_contacts = list(get_all_contacts(validated_data, user))
    all_contacts_len = len(all_contacts)
    send_account_objects = get_send_account(validated_data, user)
    cure_contact_index = 0
    cure_sender_obj = UserSenders.objects.get(id=cure_sender_obj_id)
    cure_sender_obj.type = "wa"
    cure_sender_obj.user = user
    cure_sender_obj.text = text
    cure_sender_obj.comment = validated_data.get("comment")
    cure_sender_obj.title = validated_data.get("title")
    cure_sender_obj.save()
    send_messages_count = 0
    for send_account_id in send_accounts:
        send_account_object = send_account_objects.get(id=send_account_id)
        driver = create_wa_driver(send_account_object.session_number)
        for i in range(send_accounts[send_account_id]):
            if all_contacts_len - cure_contact_index <= 0:
                driver.quit()
                return
            cure_contact = all_contacts[cure_contact_index]
            cure_contact_index += 1
            statistic = UserSendersContactStatistic.objects.create(user=user, sender=cure_sender_obj,
                                                                   contact=cure_contact)
            phone_number = cure_contact.phone
            if phone_number is None:
                message = "У этого контакта нет номера для рассылки по WhatsApp"
                set_error_message_to_statistic(statistic, message)
                continue
            is_phone_whatsapp_reg = cure_contact.is_phone_whatsapp_reg
            if is_phone_whatsapp_reg is None:
                result_is_reg = is_this_number_reg(driver, phone_number)
                cure_contact.is_phone_whatsapp_reg = result_is_reg
                cure_contact.whats_reg_checked_data = datetime.date.today()
                cure_contact.save()
                if not result_is_reg:
                    message = "Номер этого контакта не зарегистрирован в WhatsApp"
                    set_error_message_to_statistic(statistic, message)
                    continue
            elif not is_phone_whatsapp_reg:
                message = "Номер этого контакта не зарегистрирован в WhatsApp"
                set_error_message_to_statistic(statistic, message)
                continue
            try:
                send_msg(driver, phone_number, text)
                send_messages_count += 1
                statistic.is_send = True
                statistic.comment = "Сообщение успешно отправлено"
                statistic.save()
            except Exception as e:
                message = f"Сообщение не отправлено, попробуйте ещё раз. При повторении ошибки обратитесь к администратору\n Сообщение для администратора{e}"
                set_error_message_to_statistic(statistic, message)
                continue
        driver.quit()
    cure_sender_obj.count_letter = send_messages_count
    cure_sender_obj.finish_date = timezone.now()
    cure_sender_obj.save()


def get_text(validated_data, user):
    text_id = validated_data.get("text_id")
    if text_id is not None:
        text_obj = UserLetterText.objects.get(id=text_id, user=user)
        return text_obj.text
    return validated_data.get("text")


def send_accounts_parse(validated_data):
    """
    возвращает словарm {"account_id": кол-во сообщений}
    """
    send_accounts = validated_data.get("send_accounts")
    result = {}
    for send_account in send_accounts:
        account_id, sender_count = send_account.split("-")
        result[account_id] = int(sender_count)
    return result


def get_all_contacts(validated_data, user):
    groups = validated_data.get("contacts_group")
    contacts = validated_data.get("contacts")
    all_contacts = None
    if groups is not None:
        for group in groups:
            cure_group_obj = ContactGroup.objects.get(id=group, user=user)
            cure_contacts = RecipientContact.objects.filter(owner=user, contact_group=cure_group_obj)
            if all_contacts is None:
                all_contacts = cure_contacts
            else:
                all_contacts = all_contacts | cure_contacts
    if contacts is not None:
        for contact_id in contacts:
            cure_contact = RecipientContact.objects.filter(id=contact_id)
            if all_contacts is None:
                all_contacts = cure_contact
            else:
                all_contacts = all_contacts | cure_contact
    if all_contacts is not None:
        return all_contacts.distinct()
    return None


def wa_text_id_validate(text_id, user):
    try:
        UserLetterText.objects.exclude(text=None).get(id=text_id, user=user)
    except ObjectDoesNotExist:
        raise serializers.ValidationError("У вас нет такого текста для рассылки или текст письма не заполнен")


def wa_send_account_validate(data, user):
    send_accounts = data.get("send_accounts")
    if send_accounts is None:
        return
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
                int(letter_count_str)
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
    if contact_groups is None:
        return
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


def wa_sender_run_data_validate(data, user):
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


def get_send_account(data, user):
    send_accounts_id = data.get("send_accounts")
    send_accounts = None
    for account_id in send_accounts_id:
        cure_account = SenderPhoneNumber.objects.filter(id=account_id.split('-')[0], owner=user)
        if send_accounts is None:
            send_accounts = cure_account
        else:
            send_accounts = send_accounts | cure_account
    return send_accounts.distinct()


def wa_sender_run_account_login_validate(data, user):
    send_accounts = get_send_account(data, user)
    not_login_ids = []
    for account in send_accounts:
        if not check_login_view(account.session_number):
            account.is_login = False
            account.login_date = datetime.date.today()
            account.save()
            not_login_ids.append(account.id)
    if len(not_login_ids) != 0:
        raise serializers.ValidationError(
            f"При проверке обнаружилось, что произведён выход из части аккаунтов. Войдите, пожалуйста в аккаунты со "
            f"следующими id{not_login_ids}")


def send_msg(driver, phone_no, text):
    message = text
    print(f"https://web.whatsapp.com/send?phone={phone_no}&text={message}")
    driver.get(f"https://web.whatsapp.com/send?phone={phone_no}&text={message}")
    while True:
        try:
            send_button = WebDriverWait(driver, 1).until(
                EC.presence_of_element_located(
                    (By.CSS_SELECTOR, ".tvf2evcx.oq44ahr5.lb5m6g5c.svlsagor.p2rjqpw5.epia9gcq"))
            )
            break
        except (NoAlertPresentException, TimeoutException, UnexpectedAlertPresentException) as E:
            pass
    send_button.click()
    time.sleep(3)
    while True:
        try:
            WebDriverWait(driver, 1).until(
                EC.presence_of_element_located(
                    (By.CSS_SELECTOR, ".svlsagor.qssinsw9.lniyxyh2.p357zi0d.ac2vgrno.gndfcl4n"))
            )
            break
        except (NoAlertPresentException, TimeoutException, UnexpectedAlertPresentException) as E:
            pass
