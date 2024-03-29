from abc import ABC

from rest_framework import serializers
from .models import RecipientContact, User, ContactGroup, UserSenders, SenderEmail, SenderPhoneNumber, \
    ContactImportFiles, UserSendersContactStatistic
from sender.services.all_service import phone_normalize, is_valid_phone_number
from .services.user_service import user_data_validate
from .services.contact_service import recipient_contact_patch_validate, recipient_contact_all_fields_valid, \
    set_m2m_fields_to_recipient_contact, recipient_contact_update
from .services.senders_account_service import email_check_null, whatsapp_check_null
from .services.contact_import_service import contact_import_run_request_data_validate
from .services.WA_sender_service import wa_sender_run_data_validate, wa_sender_run_account_login_validate
from .services.email_service import email_account_run_validate, email_sender_run_data_validate
from django.core.exceptions import ObjectDoesNotExist


class EmailCheckSeveralSerializer(serializers.Serializer):
    email_ids = serializers.ListField(child=serializers.IntegerField(), required=True)


class WaAccountCheckSerializer(serializers.Serializer):
    groups_ids = serializers.ListField(child=serializers.IntegerField(), required=True)
    contact_ids = serializers.ListField(child=serializers.IntegerField(), required=True)


class SenderSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserSenders
        fields = ('id', 'type', 'title', 'start_date', "finish_date", "count_letter")


class SenderStatisticSerializer(serializers.ModelSerializer):
    contact_str = serializers.SerializerMethodField()

    class Meta:
        model = UserSendersContactStatistic
        fields = ('contact', 'contact_str', 'is_send', 'comment')

    def get_contact_str(self, obj):
        # Возвращаем результат метода __str__ модели RecipientContact
        return str(obj.contact)


class EmailSenderSerializer(serializers.Serializer):
    """ Для приема параметров на рассылку"""
    text_id = serializers.IntegerField(min_value=0, required=False)
    mailing_subject = serializers.CharField(max_length=50, required=True)
    text = serializers.CharField(required=False)
    title = serializers.CharField(required=False)
    send_accounts = serializers.ListField(child=serializers.CharField(), required=True)
    contacts_group = serializers.ListField(child=serializers.IntegerField(min_value=0), required=False)
    contacts = serializers.ListField(child=serializers.IntegerField(min_value=0), required=False)
    comment = serializers.CharField(required=False)

    def validate(self, data):
        request = self.context.get('request')
        user = request.user
        email_account_run_validate(data, user)
        data = email_sender_run_data_validate(data, user)
        return data


class WASenderSerializer(serializers.Serializer):
    """ Для приема параметров на рассылку"""
    text_id = serializers.IntegerField(min_value=0, required=False)
    text = serializers.CharField(required=False)
    title = serializers.CharField(required=False)
    send_accounts = serializers.ListField(child=serializers.CharField(), required=True)
    contacts_group = serializers.ListField(child=serializers.IntegerField(min_value=0), required=False)
    contacts = serializers.ListField(child=serializers.IntegerField(min_value=0), required=False)
    comment = serializers.CharField(required=False)

    def validate(self, data):
        request = self.context.get('request')
        user = request.user
        data = wa_sender_run_data_validate(data, user)
        return data


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
    login_date = serializers.DateTimeField(read_only=True)
    id = serializers.IntegerField(read_only=True)

    class Meta:
        model = SenderPhoneNumber
        fields = ("id",
                  'contact',
                  'title',
                  'is_login',
                  'login_date'
                  )

    def validate(self, data):
        phone_norm = phone_normalize(data.get("contact"))
        try:
            request = self.context.get('request')
            user = request.user
            SenderPhoneNumber.objects.get(owner=user, contact=phone_norm)
            raise serializers.ValidationError("У вас уже есть аккаунт с таким контактом")
        except ObjectDoesNotExist:
            pass
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
    checked_date = serializers.DateTimeField(read_only=True)
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
                  "login_error_msg"
                  )

    def validate(self, data):
        try:
            request = self.context.get('request')
            email = data.get("contact")
            user = request.user
            SenderEmail.objects.get(owner=user, contact=email)
            raise serializers.ValidationError("У вас уже есть аккаунт с таким контактом")
        except ObjectDoesNotExist:
            pass
        return super().validate(data)

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
        if request.method == "PATCH":
            view = self.context['view']
            contact_id = view.kwargs['pk']
        else:
            contact_id = None
        recipient_contact_all_fields_valid(contact_id, data, phone_valid_error, request,
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
