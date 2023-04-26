from rest_framework import serializers
from .models import RecipientContact, User
import secrets
import string


class RecipientContactSerializer(serializers.ModelSerializer):
    class Meta:
        model = RecipientContact
        fields = ('owner', 'contact', 'type', 'contact_group')


def send_password(email: str):
    pass


class UserSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, allow_blank=True, allow_null=True)
    confirm_password = serializers.CharField(write_only=True, allow_blank=True, allow_null=True)

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
        if not (data['password'] is None) and not (data['confirm_password'] is None):
            if data['password'] != data['confirm_password']:
                raise serializers.ValidationError("The two password fields must match.")
        return data

    def create(self, validated_data):
        is_password_random = False
        if not (validated_data['password'] is None) and not (validated_data['confirm_password'] is None):
            validated_data.pop('confirm_password')
            password = validated_data.pop('password')
        else:
            alphabet = string.ascii_letters + string.digits + string.punctuation
            password = ''.join(secrets.choice(alphabet) for i in range(12))
            is_password_random = True
        user = super(UserSerializer, self).create(validated_data)
        user.set_password(password)
        user.save()
        if is_password_random:
            send_password(validated_data['email'])
        return user
