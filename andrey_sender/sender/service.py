import secrets
import string
from django.core.mail import send_mail
from .models import RecipientContact


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
