import random

from ..models import SenderEmail, UserSenders, UserSendersContactStatistic
from django.db.models import QuerySet
import smtplib
from django.core.exceptions import ObjectDoesNotExist
from django.utils import timezone
from .WA_sender_service import get_text, send_accounts_parse, get_all_contacts, set_error_message_to_statistic, \
    contact_group_validate, text_id_validate, contacts_validate, send_account_validate
import time
from email.mime.text import MIMEText
from rest_framework import serializers


def email_sender_run_data_validate(data, user):
    text_id = data.get("text_id")
    if text_id is not None:
        text_id_validate(text_id, user)
    elif data.get("text") is None:
        raise serializers.ValidationError("Должен быть заполнен контент письма. Либо текст, либо text_id")
    contact_groups = data.get("contacts_group")
    contacts = data.get("contacts")
    if contact_groups is None and contacts is None:
        raise serializers.ValidationError("Передайте хотя бы одну группу или получателя")
    send_account_validate(data, user, type="email")
    contact_group_validate(contact_groups, user)
    contacts_validate(contacts, user)
    return data


def email_account_run_validate(data, user):
    send_account_objects = get_email_send_account(data, user)
    check_login_emails(send_account_objects)
    fail = []
    for account in send_account_objects:
        if not account.is_check_pass:
            fail.append(account.id)
    if len(fail):
        raise serializers.ValidationError(f"Не удалось войти в почты с id:{fail}")


def get_email_send_account(data, user):
    send_accounts_id = data.get("send_accounts")
    send_accounts = None
    for account_id in send_accounts_id:
        cure_account = SenderEmail.objects.filter(id=account_id.split('-')[0], owner=user)
        if send_accounts is None:
            send_accounts = cure_account
        else:
            send_accounts = send_accounts | cure_account
    return send_accounts.distinct()


def email_sender_run(validated_data, user, cure_sender_obj_id):
    text = get_text(validated_data, user)
    send_accounts = send_accounts_parse(validated_data)
    all_contacts = list(get_all_contacts(validated_data, user))
    all_contacts_len = len(all_contacts)
    send_account_objects = get_email_send_account(validated_data, user)
    cure_contact_index = 0
    cure_sender_obj = UserSenders.objects.get(id=cure_sender_obj_id)
    cure_sender_obj.type = "wa"
    cure_sender_obj.user = user
    cure_sender_obj.text = text
    cure_sender_obj.comment = validated_data.get("comment")
    cure_sender_obj.title = validated_data.get("title")
    cure_sender_obj.save()
    subject = validated_data.get("mailing_subject")
    send_messages_count = 0
    for send_account_id in send_accounts:
        send_account_object = send_account_objects.get(id=send_account_id)
        from_email = send_account_object.contact
        password = send_account_object.password
        smtp_name = get_smtp_name(from_email)[0]
        for i in range(send_accounts[send_account_id]):
            if all_contacts_len - cure_contact_index <= 0:
                cure_sender_obj.count_letter = send_messages_count
                cure_sender_obj.finish_date = timezone.now()
                cure_sender_obj.save()
                return
            cure_contact = all_contacts[cure_contact_index]
            cure_contact_index += 1
            statistic = UserSendersContactStatistic.objects.create(user=user, sender=cure_sender_obj,
                                                                   contact=cure_contact)
            to_email = cure_contact.email
            if to_email is None:
                message = "У этого контакта нет почты для получения сообщений"
                set_error_message_to_statistic(statistic, message)
                continue
            try:
                # Создаем объект SMTP
                server = smtplib.SMTP(smtp_name, 587)
                # Указываем, что используем TLS
                server.starttls()
                # Авторизация на почте
                server.login(from_email, password)
                # Создаем сообщение
                message = MIMEText(text, "html", "utf-8")
                message["Subject"] = subject
                message["From"] = from_email
                # Добавляем адрес получателя в сообщение
                message["To"] = to_email
                # Отправляем письмо
                server.sendmail(from_email, to_email, message.as_string())
                server.quit()
                statistic.is_send = True
                statistic.comment = "Успешно отправлено"
                statistic.save()
                print(f"Отправлено сообщение на {to_email}")
                time.sleep(random.randint(1, 5))
            except Exception as e:
                statistic.is_send = False
                statistic.comment = "Не отправлено"+str(e)
                statistic.save()
    cure_sender_obj.count_letter = send_messages_count
    print("ОТПРАВЛИЛОСЬ:!!!", send_messages_count)
    cure_sender_obj.finish_date = timezone.now()
    cure_sender_obj.save()


def get_smtp_name(from_email):
    cure_domain = from_email[from_email.rfind('@') + 1:]
    allowed_domains = ("yandex.ru", "mail.ru", "gmail.com")
    if cure_domain in allowed_domains:
        return f"smtp.{cure_domain}", ""
    return None, allowed_domains


def get_checked_emails(user, ids: list[int]):
    emails_objs = []
    for email_id in ids:
        try:
            email_obj = SenderEmail.objects.get(owner=user, id=email_id)
            emails_objs.append(email_obj)
        except ObjectDoesNotExist:
            pass
    return emails_objs


def check_login_emails(checked_email_id: QuerySet or list[SenderEmail]) -> None:
    for email_obj in checked_email_id:
        email = email_obj.contact
        email_obj.checked_date = timezone.now()
        email_obj.save()
        if email is not None:
            smtp_name, allowed_domains = get_smtp_name(email)
            passw = email_obj.password
            if smtp_name is not None and passw is not None:
                if check_login(email, smtp_name, passw):
                    email_obj.is_check_pass = True
                    email_obj.save()
                else:
                    email_obj.is_check_pass = False
                    email_obj.login_error_msg = f"Неправильный код доступа"
                    email_obj.save()
            elif smtp_name is None:
                email_obj.is_check_pass = False
                email_obj.login_error_msg = f"Мы поддерживаем только почты {allowed_domains}"
                email_obj.save()
            elif passw is None:
                email_obj.is_check_pass = False
                email_obj.login_error_msg = f"Нет кода доступа"
                email_obj.save()


def check_login(email, smtp_domain, passw):
    try:
        server = smtplib.SMTP(smtp_domain, 587)
        server.starttls()
        server.login(email, passw)
        server.quit()
        return True
    except smtplib.SMTPAuthenticationError:
        server.quit()
        return False
