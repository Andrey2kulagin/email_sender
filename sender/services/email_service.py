from ..models import SenderEmail
from django.db.models import QuerySet
import smtplib
from django.core.exceptions import ObjectDoesNotExist
from django.utils import timezone

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


def check_login_emails(checked_email_id: QuerySet or list[SenderEmail]) -> None:
    for email_obj in checked_email_id:
        email = email_obj.email
        email_obj.checked_date = timezone.now()
        email_obj.save()
        if email is not None:
            smtp_name, allowed_domains = get_smtp_name(email)
            passw = email.password
            if smtp_name is not None and passw is not None:
                if check_login(email, smtp_name, passw):
                    email_obj.is_check_pass = True
                    email_obj.save()
            elif smtp_name is None:
                email_obj.is_check_pass = False
                email_obj.error_msg = f"Мы поддерживам только почты {allowed_domains}"
                email_obj.save()
            elif passw is None:
                email_obj.error_msg = f"Неправильный код доступа"
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
