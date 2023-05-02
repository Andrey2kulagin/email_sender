import secrets
import string
from django.core.mail import send_mail
from .models import RecipientContact
import re


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
    if out_str[0] == '+' and out_str[0] == '7':
        out_str = '7' + out_str[2::]
    elif out_str[0] == '8':
        out_str = '7' + out_str[1::]
    return out_str


def is_valid_phone_number(phone_number: str) -> bool:
    """
    Валидатор номеров мобильных телефонов для России, Беларуси, Украины и Казахстана

    Принимает на вход строку с номером телефона в международном формате, например: +79261234567
    """
    phone_number = phone_normalize(phone_number)
    pattern = r'^(79\d{9})$'
    match = re.match(pattern, phone_number)
    return bool(match)


def send_password(email: str, password: str):
    send_mail(
        'Благодарим за регистрацию',
        f'Спасибо за регистрацию на нашем портале. Ваш пароль: {password}. Сменить пароль вы можете в личном кабинете',
        'andrey2kulagin@yandex.ru',
        [email],
        fail_silently=False,
    )


def create_password() -> str:
    alphabet = string.ascii_letters + string.digits + string.punctuation
    password = ''.join(secrets.choice(alphabet) for i in range(12))
    return password


def set_m2m_fields_to_recipient_contact(contact_group: list, instance: RecipientContact, senders: list):
    for group in contact_group:
        instance.contact_group.add(group)
    for sender in senders:
        instance.senders.add(sender)
    instance.save()
