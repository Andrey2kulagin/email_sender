from abc import ABC

from rest_framework import serializers
from .models import RecipientContact, User, ContactGroup, UserSenders, SenderEmail, SenderPhoneNumber, \
    ContactImportFiles
from sender.services.all_service import phone_normalize, is_valid_phone_number
from .services.user_service import user_data_validate
from .services.contact_service import recipient_contact_patch_validate, recipient_contact_all_fields_valid, \
    set_m2m_fields_to_recipient_contact, recipient_contact_update
from .services.senders_account_service import email_check_null, whatsapp_check_null
from .services.contact_import_service import contact_import_run_request_data_validate


class ImportSerializer(serializers.ModelSerializer):
    id = serializers.IntegerField(read_only=True)

    class Meta:
        model = ContactImportFiles
        fields = ('id', 'filename', 'date', 'is_imported', 'all_handled_lines', 'success_create_update_count',
                  'partial_success_create_update_count', 'fail_count')


class ContactRunImportSerializer(serializers.Serializer):
    filename = serializers.CharField(max_length=100, required=True)

    id = serializers.IntegerField(max_value=20, default=None, allow_null=True)
    name = serializers.IntegerField(max_value=20, default=None, allow_null=True)
    surname = serializers.IntegerField(max_value=20, default=None, allow_null=True)
    email = serializers.IntegerField(max_value=20, default=None, allow_null=True)
    phone = serializers.IntegerField(max_value=20, default=None, allow_null=True)
    contact_group = serializers.IntegerField(max_value=20, default=None, allow_null=True)
    comment = serializers.IntegerField(max_value=20, default=None, allow_null=True)

    def validate(self, data):
        request = self.context.get('request')
        user = request.user
        contact_import_run_request_data_validate(data, user)
        return data


class ImportFileUploadSerializer(serializers.Serializer):
    def validate(self, data):
        filename = data.get("file").name
        if filename.find(".xlsx") == -1 or filename.find(".xlsx") + 5 != len(filename):
            raise serializers.ValidationError("Загрузите excel-файл")
        return data

    file = serializers.FileField()
    is_contains_headers = serializers.BooleanField(default=False)


class ContactGroupSerializer(serializers.ModelSerializer):
    id = serializers.IntegerField(read_only=True)

    class Meta:
        model = ContactGroup
        fields = ('id', 'title')


class WhatsAppAccountSerializer(serializers.ModelSerializer):
    is_login = serializers.BooleanField(read_only=True)
    id = serializers.IntegerField(read_only=True)

    class Meta:
        model = SenderPhoneNumber
        fields = ("id",
                  'contact',
                  'title',
                  'is_login',
                  )

    def validate(self, data):
        phone_norm = phone_normalize(data.get("contact"))
        if not is_valid_phone_number(phone_norm):
            raise serializers.ValidationError("Номер не валидный")
        data["contact"] = phone_norm
        return data

    def update(self, instance, validated_data):
        instance = super().update(instance, validated_data)
        whatsapp_check_null(instance, validated_data)
        return instance


class EmailAccountSerializer(serializers.ModelSerializer):
    password = serializers.CharField(max_length=50, write_only=True)
    checked_date = serializers.DateField(read_only=True)
    is_check_pass = serializers.BooleanField(read_only=True)
    id = serializers.IntegerField(read_only=True)

    class Meta:
        model = SenderEmail
        fields = ("id",
                  'contact',
                  'title',
                  'password',
                  'checked_date',
                  'is_check_pass',
                  )

    def update(self, instance, validated_data):
        instance = super().update(instance, validated_data)
        email_check_null(instance, validated_data)
        return instance


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
    is_phone_whatsapp_reg = serializers.BooleanField(read_only=True)

    class Meta:
        model = RecipientContact
        fields = ('id',
                  'owner',
                  'name',
                  'surname',
                  'is_phone_whatsapp_reg',
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

    def update(self, instance, validated_data):
        return recipient_contact_update(validated_data, instance)

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
