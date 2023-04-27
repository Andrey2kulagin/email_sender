from rest_framework import serializers
from .models import RecipientContact, User
from .service import send_password, create_password


class RecipientContactSerializer(serializers.ModelSerializer):
    class Meta:
        model = RecipientContact
        fields = ('owner', 'contact', 'type', 'contact_group')


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
