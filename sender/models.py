from django.db import models
# Create your models here.
from django.contrib.auth.models import AbstractUser
from django.utils import timezone
from django.conf import settings


class User(AbstractUser):
    phone = models.CharField(verbose_name="Номер телефона", max_length=20, null=True, blank=True)
    field_of_activity = models.CharField(verbose_name="Область деятельности", max_length=100, null=True, blank=True)
    choices = (('Активна', 'Активна'),
               ('Не активна', 'Не активна'),)
    subscription = models.CharField(verbose_name="Статус подписки", max_length=50, choices=choices,
                                    default="Не активна", null=True)
    activation_date = models.DateField(verbose_name="Дата активации подписки", null=True, blank=True)
    subscription_days = models.PositiveIntegerField(verbose_name="Длина подписки(дней)", null=True)
    end_of_subscription = models.DateField(verbose_name="Дата истечения подписки", null=True, blank=True)
    api_token = models.CharField(max_length=500, null=True)


class ContactImportFiles(models.Model):
    owner = models.ForeignKey(User, on_delete=models.CASCADE)
    date = models.DateTimeField(auto_now_add=True)
    filename = models.CharField(max_length=100)
    row_len = models.IntegerField()
    is_contains_headers = models.BooleanField(default=False, null=True)
    is_imported = models.BooleanField(default=False, null=True)
    all_handled_lines = models.IntegerField(default=None, null=True)
    success_create_update_count = models.IntegerField(default=None, null=True)
    partial_success_create_update_count = models.IntegerField(default=None, null=True)
    fail_count = models.IntegerField(default=None, null=True)

    def __str__(self):
        return f"import{self.id}"


class ContactGroup(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    title = models.CharField(verbose_name="Группа контактов", max_length=100)

    def __str__(self):
        return self.title


class UserLetterText(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    title = models.CharField(verbose_name="Внутренние название письма", max_length=100)
    letter_subject = models.CharField(verbose_name="Тема письма для клиента", max_length=100)
    text = models.TextField(verbose_name="Tекст письма", null=True)


class UserSenders(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True)  # пользователь - владелец рассылки
    text = models.TextField(null=True)  # текст - что вообще рассылалось
    count_letter = models.PositiveIntegerField(verbose_name="Число отправленных сообщений", null=True,
                                               default=0)  # Число разосланных сообщений
    start_date = models.DateTimeField(auto_now_add=True)  # Дата создания рассылки
    finish_date = models.DateTimeField(null=True)  # Дата окончания рассылки. Если не окончена, то None

    comment = models.TextField(null=True)
    title = models.CharField(max_length=100, null=True, blank=True, default="Без названия")
    type_choices = [
        ('wa', 'WhatsApp'),
        ('em', 'Email'),
    ]
    type = models.CharField(max_length=2, null=True, choices=type_choices)
    is_error_with_accounts = models.BooleanField(default=False)  # Есть ошибка с аккаунтами
    is_account_validation_pass = models.BooleanField(default=False)  # прошла ли валидация аккаунтов
    account_error_msg = models.TextField(null=True)  # текст ошибки с аккаунтами

    def __str__(self):
        return self.title

    def is_have_account_error(self):
        if not self.is_account_validation_pass:
            return None, ""
        return self.is_error_with_accounts, self.account_error_msg

    def is_success_stopped(self):
        """ Есть ли успешное завершение рассылки?"""
        if not self.is_account_validation_pass or self.is_error_with_accounts:
            return None
        elif self.is_account_validation_pass and not self.is_error_with_accounts and self.finish_date is not None:
            return True
        else:
            return False


class RecipientContact(models.Model):
    owner = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    name = models.CharField(max_length=150, null=True, blank=True)
    surname = models.CharField(max_length=150, null=True, blank=True)
    phone = models.CharField(verbose_name="Телефон", max_length=100, null=True, blank=True)
    is_phone_whatsapp_reg = models.BooleanField(verbose_name="Телефон проверен на наличие в WhatsApp", default=None,
                                                null=True)
    whats_reg_checked_data = models.DateField(default=None, null=True, blank=True)
    email = models.EmailField(verbose_name="Email", null=True, blank=True)
    contact_group = models.ManyToManyField(ContactGroup, default=[], blank=True)
    senders = models.ManyToManyField(UserSenders, default=[], blank=True)
    comment = models.TextField(null=True, blank=True)

    def __str__(self):
        base_str = ""
        if self.name is not None:
            base_str += f"{self.name} - "
        if self.surname is not None:
            base_str += f"{self.surname} - "
        if self.phone and self.email:
            return f"{base_str}{self.phone} - {self.email}"
        if self.phone:
            return f"{base_str}{self.phone}"
        if self.email:
            return f"{base_str}{self.email}"
        return f"{base_str}"


class UserSendersContactStatistic(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name="Пользователь")
    sender = models.ForeignKey(UserSenders, on_delete=models.CASCADE, verbose_name="Рассылка")
    contact = models.ForeignKey(RecipientContact, on_delete=models.CASCADE, verbose_name="Контакт")
    is_send = models.BooleanField(null=True)
    comment = models.TextField(verbose_name="Комментарий", null=True)

    def __str__(self):
        return f"{self.user} - {self.sender} - {self.contact.phone}  {self.contact.email}- {self.is_send},"


class SenderEmail(models.Model):
    owner = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    contact = models.CharField(verbose_name="Контакт", max_length=50)
    title = models.CharField(verbose_name="Название", max_length=150, null=True, blank=True)
    password = models.CharField(max_length=50, blank=True, null=True)
    checked_date = models.DateField(null=True, default=None, blank=True)
    is_check_pass = models.BooleanField(null=True, default=None, blank=True)
    login_error_msg = models.TextField(null=True, blank=True)


class SenderPhoneNumber(models.Model):
    owner = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    title = models.CharField(verbose_name="Название", max_length=150, null=True)
    contact = models.CharField(verbose_name="Контакт", max_length=50, null=True)
    login_date = models.DateTimeField(null=True, default=None, blank=True)  # дата последней успешной авторизации
    is_login = models.BooleanField(null=True, default=False)  # авторизован ли пользователь
    last_login_request = models.DateTimeField(null=True, blank=True)  # дата последнего запроса на авторизация
    qr_code = models.ImageField(default=None, null=True, upload_to='qr_codes/',
                                blank=True)  # поле для хранения qr-кода
    is_login_start = models.BooleanField(
        default=False)  # флаг, который True в течении всего процесса входа в WhatsApp с момента запроса до входа

    @property
    def session_number(self):
        return self.id

    @property
    def get_sec_time_from_login_req(self):
        if self.last_login_request:
            now = timezone.now()
            time_difference = now - self.last_login_request
            return time_difference.total_seconds()
        return None

    @property
    def get_sec_time_from_last_login(self):
        if self.login_date:
            now = timezone.now()
            time_difference = now - self.login_date
            return time_difference.total_seconds()
        return None


class AdminData(models.Model):
    login_duration_sec = models.PositiveIntegerField(verbose_name="Длительность ожидания входа в WhatsApp, сек",
                                                     default=120)
    sleep_time = models.PositiveIntegerField(verbose_name="Задержка между проверками сканирования qr, сек", default=10)
    timeout_before_mail_sec = models.PositiveIntegerField(verbose_name="Задержка между сообщениями, сек", default=3)
    check_login_time_sec = models.PositiveIntegerField(
        verbose_name="Длительность возможности проверки входа при авторизации в WhatsApp, сек", default=120)
    repeat_check_attempt = models.PositiveIntegerField(default=3,
                                                       verbose_name="Кол-во попыток при повторной проверка логина в whatsApp")


class ContactCheckStatistic(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    status_data = models.JSONField(default={"status_code": 202, "message": "Процесс начат, но не завершен"})
    date = models.DateTimeField(auto_now_add=True)
