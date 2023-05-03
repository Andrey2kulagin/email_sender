import secrets
import string
from django.core.mail import send_mail
from .models import RecipientContact, User
import re
from django.core.validators import validate_email
from rest_framework import serializers


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


def recipient_contact_patch_validate(instance, data, error_missing_contacts, email_valid_error, phone_valid_error):
    # обрабатываем случай удаления обоих контактов
    if ("phone" in data and "email" in data) and (data["email"] is None and data["phone"] is None):
        raise serializers.ValidationError(error_missing_contacts)
    # обрабатываем случай, когда phone удаляется
    if "phone" in data and data["phone"] is None:
        if "email" in data:
            try:
                validate_email(data["email"])
            except:
                raise serializers.ValidationError(email_valid_error)
        else:
            if instance.email is None:
                raise serializers.ValidationError(error_missing_contacts)
    # обрабатываем случай, когда email удаляется
    if "email" in data and data["email"] is None:
        if "phone" in data:
            if not is_valid_phone_number(data["phone"]):
                raise serializers.ValidationError(phone_valid_error)
        else:
            if instance.phone is None:
                raise serializers.ValidationError(error_missing_contacts)


def recipient_contact_all_fields_valid(data, username_is_already_occupied_error, phone_valid_error, request,
                                       email_valid_error):
    # проверяем, есть ли уже пользователи с таким ником
    if "username" in data:
        if len(User.objects.filter(username=data["username"])) != 0:
            raise serializers.ValidationError(username_is_already_occupied_error)
    if "phone" in data:
        if not is_valid_phone_number(data["phone"]):
            raise serializers.ValidationError(phone_valid_error)
        else:
            # проверяем, есть ли у пользователя контакт с таким номером, чтобы не было дубликатов
            contacts_with_this_number = RecipientContact.objects.filter(owner=request.user, phone=data["phone"])
            if len(contacts_with_this_number) != 0:
                raise serializers.ValidationError(
                    f"Уже есть контакт(ы) с таким телефоном id:{[i.id for i in contacts_with_this_number]}")
    if "email" in data:
        try:
            validate_email(data["email"])
        except:
            raise serializers.ValidationError(email_valid_error)
        # проверяем, есть ли у пользователя контакт с таким email, чтобы не было дубликатов
        contacts_with_this_email = RecipientContact.objects.filter(owner=request.user, email=data["email"])
        if len(contacts_with_this_email) != 0:
            raise serializers.ValidationError(
                f"Уже есть контакт(ы) с таким email id:{[i.id for i in contacts_with_this_email]}")
    # проверяем, принадлежит ли группа пользователю, который ее добавляет
    if "contact_group" in data:
        for group in data["contact_group"]:
            if group.user != request.user:
                raise serializers.ValidationError(
                    f'Группа "{group}" id:{group.id} не пренадлежит пользователю, который ее использует')
    # проверяем, принадлежит ли рассылка пользователю, который ее добавляет
    if "senders" in data:
        for sender in data["senders"]:
            if sender.user != request.user:
                raise serializers.ValidationError(
                    f'Рассылка "{sender}" id:{sender.id} не пренадлежит пользователю, который ее использует')


