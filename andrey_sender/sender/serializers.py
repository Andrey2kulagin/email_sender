from rest_framework import serializers
from .models import RecipientContact, User


class RecipientContactSerializer(serializers.ModelSerializer):
    class Meta:
        model = RecipientContact
        fields = ('owner', 'contact', 'type', 'contact_group')


class UserSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)
    confirm_password = serializers.CharField(write_only=True)

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
        if data['password'] != data['confirm_password']:
            raise serializers.ValidationError("The two password fields must match.")
        return data

    def create(self, validated_data):

        validated_data.pop('confirm_password')
        password = validated_data.pop('password')
        user = super(UserSerializer, self).create(validated_data)
        user.set_password(password)
        user.save()
        return user

