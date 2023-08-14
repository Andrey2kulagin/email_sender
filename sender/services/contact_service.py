from .all_service import phone_normalize, validate_email, is_valid_phone_number
from rest_framework import serializers
from ..models import RecipientContact
from django.core.exceptions import ObjectDoesNotExist


def get_group_contact_count(user, pk):
    qs = RecipientContact.objects.filter(owner=user, contact_group__id=pk)
    return qs.count()


def delete_several_contacts(user, contacts_id, groups_id):
    all_contact_ids = set()
    dell_contact_ids = set()
    for i in contacts_id:
        all_contact_ids.add(i)
        try:
            RecipientContact.objects.get(owner=user, id=i).delete()
            dell_contact_ids.add(i)
        except ObjectDoesNotExist:
            pass
    for group_id in groups_id:
        contacts = RecipientContact.objects.filter(owner=user, contact_group__id=group_id)
        for contact in contacts:
            all_contact_ids.add(contact.id)
            dell_contact_ids.add(contact.id)
            contact.delete()
    return {
        "success_delete": list(dell_contact_ids),
        "fail_delete": list(all_contact_ids - dell_contact_ids)
    }


def recipient_contact_update(validated_data, instance):
    if validated_data.get("phone"):
        validated_data["phone"] = phone_normalize(validated_data["phone"])
    if "phone" in validated_data:
        instance.is_phone_whatsapp_reg = None
        instance.whats_reg_checked_data = None
    instance.name = validated_data.get('name', instance.name)
    instance.surname = validated_data.get('surname', instance.surname)
    instance.phone = validated_data.get('phone', instance.phone)
    instance.email = validated_data.get('email', instance.email)
    instance.comment = validated_data.get('comment', instance.comment)
    contact_group = validated_data.pop('contact_group', None)
    senders = validated_data.pop('senders', None)
    set_m2m_fields_to_recipient_contact(contact_group, instance, senders)
    instance.save()
    return instance


def set_m2m_fields_to_recipient_contact(contact_group: list, instance: RecipientContact, senders: list):
    if contact_group:
        instance.contact_group.clear()
        for group in contact_group:
            instance.contact_group.add(group)
    if senders:
        instance.senders.clear()
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


def recipient_contact_all_fields_valid(data, phone_valid_error, request,
                                       email_valid_error):
    user = request.user
    phone_validate(data, phone_valid_error, user)
    email_validate(data, email_valid_error, user)
    contact_group_validate(data, user)
    senders_validate(data, user)


def senders_validate(data, user):
    # проверяем, принадлежит ли рассылка пользователю, который ее добавляет
    if "senders" in data:
        for sender in data["senders"]:
            if sender.user != user:
                raise serializers.ValidationError(
                    f'Рассылка "{sender}" id:{sender.id} не пренадлежит пользователю, который ее использует')


def contact_group_validate(data, user):
    # проверяем, принадлежит ли группа пользователю, который ее добавляет
    if "contact_group" in data:
        for group in data["contact_group"]:
            if group.user != user:
                raise serializers.ValidationError(
                    f'Группа "{group}" id:{group.id} не пренадлежит пользователю, который ее использует')


def phone_validate(data, phone_valid_error, user):
    if data.get("phone"):
        if not is_valid_phone_number(data["phone"]):
            raise serializers.ValidationError(phone_valid_error)
        else:
            # проверяем, есть ли у пользователя контакт с таким номером, чтобы не было дубликатов
            contacts_with_this_number = RecipientContact.objects.filter(owner=user, phone=data["phone"])
            if len(contacts_with_this_number) != 0:
                raise serializers.ValidationError(
                    f"Уже есть контакт(ы) с таким телефоном id:{[i.id for i in contacts_with_this_number]}")



def email_validate(data, email_valid_error, user):
    if data.get("email"):
        try:
            validate_email(data["email"])
        except:
            raise serializers.ValidationError(email_valid_error)
        # проверяем, есть ли у пользователя контакт с таким email, чтобы не было дубликатов
        contacts_with_this_email = RecipientContact.objects.filter(owner=user, email=data["email"])
        if len(contacts_with_this_email) != 0:
            raise serializers.ValidationError(
                f"Уже есть контакт(ы) с таким email id:{[i.id for i in contacts_with_this_email]}")
