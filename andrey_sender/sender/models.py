from django.db import models

# Create your models here.
from django.contrib.auth.models import AbstractUser


class User(AbstractUser):
    phone = models.CharField(verbose_name="Номер телефона", max_length=20)
    field_of_activity = models.CharField(verbose_name="Область деятельности", max_length=100)
    choices = (('Активна', 'Активна'),
               ('Не активна', 'Не активна'),)
    subscription = models.CharField(verbose_name="Статус подписки", max_length=50, choices=choices,
                                    default="Не активна", null=True)
    activation_date = models.DateField(verbose_name="Дата активации подписки", null=True, blank=True)
    subscription_days = models.PositiveIntegerField(verbose_name="Длина подписки(дней)", null=True)
    end_of_subscription = models.DateField(verbose_name="Дата истечения подписки", null=True, blank=True)
    api_token = models.CharField(max_length=500, null=True)


class ContactGroup(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    title = models.CharField(verbose_name="Группа контактов", max_length=100)


class RecipientContact(models.Model):
    owner = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    contact = models.CharField(verbose_name="Контакт", max_length=100)
    choices = (('Email', 'Email'),
               ('WhatsApp', 'WhatsApp'),)
    type = models.CharField(verbose_name="Тип контакта", max_length=50, choices=choices, null=True)
    contact_group = models.ForeignKey(ContactGroup, on_delete=models.SET_NULL, null=True)


class UserLetterText(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    title = models.CharField(verbose_name="Внутренние название письма", max_length=100)
    letter_subject = models.CharField(verbose_name="Тема письма для клиента", max_length=100)
    text = models.TextField(verbose_name="Tекст письма")


class UserSenders(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    text = models.ForeignKey(UserLetterText, on_delete=models.SET_NULL, null=True)
    count_letter = models.PositiveIntegerField(verbose_name="Число отправленных сообщений")
    start_date = models.DateField(auto_now_add=True)
