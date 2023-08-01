from django.core.mail import send_mail
from sender.models import RecipientContact, User
import re
from django.core.validators import validate_email
from rest_framework import serializers
import os


def check_or_create_folder(folder_path):
    if not os.path.exists(folder_path):
        os.makedirs(folder_path)


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


def is_valid_phone_number(phone_number: str) -> bool:
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
