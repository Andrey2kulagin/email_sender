import secrets
import string
from django.core.mail import send_mail


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
