from rest_framework import serializers
from .models import RecipientContact, User, ContactGroup, UserSenders
from .service import send_password, create_password, set_m2m_fields_to_recipient_contact


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
        print(validated_data)
        contact_group = validated_data.pop("contact_group")
        senders = validated_data.pop("senders")
        instance = super().create(validated_data)
        set_m2m_fields_to_recipient_contact(contact_group, instance, senders)
        return instance

    def update(self, instance, validated_data):
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
        if request.method == "POST":
            if User.objects.filter(email=data['email']).exists():
                raise serializers.ValidationError("User with this email already exists.")
        if 'password' in data:
            if 'confirm_password' in data:
                if data['password'] != data['confirm_password']:
                    raise serializers.ValidationError("The two password fields must match.")
            else:
                raise serializers.ValidationError("Подтвердите пароль")
        if 'username' in data:
            if User.objects.filter(username=data['username']).exists():
                raise serializers.ValidationError("Пользователь с таким именем уже существует")
        return data

    def create(self, validated_data):
        print("ызывается CREATE")
        is_password_random = False
        validated_data['username'] = validated_data['email'].split("@")[0]
        if 'password' in validated_data and 'confirm_password' in validated_data:
            validated_data.pop('confirm_password')
            password = validated_data.pop('password')
        else:
            password = create_password()
            is_password_random = True
        user = super(UserSerializer, self).create(validated_data)
        user.set_password(password)
        user.save()
        if is_password_random:
            send_password(validated_data['email'], password)
        return user
