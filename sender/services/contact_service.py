from .all_service import phone_normalize, validate_email, is_valid_phone_number
from rest_framework import serializers
from ..models import RecipientContact
from django.db.models.query import QuerySet


def check_contacts(contacts_queryset: QuerySet[RecipientContact]):
    # если профиль для проверки авторизован, то проверяем, иначе авторизуемся
    pass


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


def recipient_contact_all_fields_valid(data, phone_valid_error, request,
                                       email_valid_error):
    if data.get("phone"):
        if not is_valid_phone_number(data["phone"]):
            raise serializers.ValidationError(phone_valid_error)
        else:
            # проверяем, есть ли у пользователя контакт с таким номером, чтобы не было дубликатов
            contacts_with_this_number = RecipientContact.objects.filter(owner=request.user, phone=data["phone"])
            if len(contacts_with_this_number) != 0:
                raise serializers.ValidationError(
                    f"Уже есть контакт(ы) с таким телефоном id:{[i.id for i in contacts_with_this_number]}")
    if data.get("email"):
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
