from rest_framework import serializers
from .models import RecipientContact, User, ContactGroup, UserSenders
from sender.services.all_service import set_m2m_fields_to_recipient_contact, recipient_contact_patch_validate, \
    recipient_contact_all_fields_valid, phone_normalize
from .services.user_service import user_data_validate


class ContactGroupSerializer(serializers.ModelSerializer):
    class Meta:
        model = ContactGroup
        fields = ('id', 'title')


class UserSendersGroupSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserSenders
        fields = ('user',
                  'text',
                  'count_letter',
                  'start_date',
                  'comment',
                  )


class RecipientContactSerializer(serializers.ModelSerializer):
    email = serializers.CharField(max_length=250, required=False, allow_null=True)

    class Meta:
        model = RecipientContact
        fields = ('id',
                  'owner',
                  'name',
                  'surname',
                  'phone',
                  'email',
                  'contact_group',
                  'senders',
                  'comment')

    def create(self, validated_data):
        senders, contact_group = [], []
        if "phone" in validated_data:
            validated_data["phone"] = phone_normalize(validated_data["phone"])
        if "contact_group" in validated_data:
            contact_group = validated_data.pop("contact_group")
        if "senders" in validated_data:
            senders = validated_data.pop("senders")
        instance = super().create(validated_data)
        set_m2m_fields_to_recipient_contact(contact_group, instance, senders)
        return instance

    def validate(self, data):
        request = self.context.get('request')
        error_missing_contacts = "Заполните хотя бы один контакт"
        email_valid_error = "Введите правильный email"
        phone_valid_error = "Неправильный номер телефона. Должно быть 11 цифр и начинаться должен с 8 или +7"
        # проверяем все поля на валидность
        recipient_contact_all_fields_valid(data, phone_valid_error, request,
                                           email_valid_error)
        if request.method == "POST":
            if not ("phone" in data or "email" in data):
                raise serializers.ValidationError(error_missing_contacts)
        elif request.method == "PATCH":
            instance = self.instance

            recipient_contact_patch_validate(instance, data, error_missing_contacts, email_valid_error,
                                             phone_valid_error)

        return data

    def update(self, instance, validated_data):
        if validated_data.get("phone"):
            validated_data["phone"] = phone_normalize(validated_data["phone"])
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


class UserSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, allow_blank=True, allow_null=True, required=False)
    confirm_password = serializers.CharField(write_only=True, allow_blank=True, allow_null=True, required=False)
    username = serializers.CharField(allow_blank=True, allow_null=True, required=False)
    email = serializers.EmailField(required=False)
    phone = serializers.CharField(allow_blank=True, allow_null=True, required=False)
    field_of_activity = serializers.CharField(allow_blank=True, allow_null=True, required=False)

    class Meta:
        model = User
        fields = (
            "username",
            "email",
            "password",
            "phone",
            "field_of_activity",
            "confirm_password"
        )

    def validate(self, data):
        request = self.context.get('request')
        return user_data_validate(data, request)
