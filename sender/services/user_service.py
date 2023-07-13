import secrets
import string
from ..models import User
from rest_framework import serializers
import collections
from rest_framework.request import Request


def user_data_validate(data: collections.OrderedDict, request: Request) -> collections.OrderedDict:
    # проверяем, есть ли уже пользователи с таким ником
    if request.method == "POST":
        if User.objects.filter(email=data['email']).exists():
            raise serializers.ValidationError("Пользователь с таким Email уже существует")
    if 'password' in data:
        if 'confirm_password' in data:
            if data['password'] != data['confirm_password']:
                raise serializers.ValidationError("Пароль и подтверждение пароля не совпадают")
        else:
            raise serializers.ValidationError("Подтвердите пароль")
    if 'username' in data:
        if User.objects.filter(username=data['username']).exists():
            raise serializers.ValidationError("Пользователь с таким именем уже существует")
        if len(data["username"]) == 0:
            raise serializers.ValidationError("Имя пользователя не может быть пустым")
    if 'confirm_password' in data:
        data.pop('confirm_password')
    return data


def create_password() -> str:
    alphabet = string.ascii_letters + string.digits + string.punctuation
    password = ''.join(secrets.choice(alphabet) for i in range(12))
    return password


def user_create(serializer: serializers.ModelSerializer) -> bool:
    serializer.is_valid(raise_exception=True)
    validated_data = serializer.validated_data
    is_password_random = False
    if not ("username" in validated_data):
        auto_username = validated_data['email'].split("@")[0]
        try:
            User.objects.get(username=auto_username)
            validated_data['username'] = validated_data['email']
        except User.DoesNotExist:
            validated_data['username'] = auto_username
    if 'password' in validated_data:
        password = validated_data.pop('password')
    else:
        password = create_password()
        is_password_random = True
    user = User.objects.create_user(username=validated_data["username"], email=validated_data["email"],
                                    password=password)
    if "phone" in validated_data:
        user.phone = validated_data["phone"]

    if "field_of_activity" in validated_data:
        user.field_of_activity = validated_data["field_of_activity"]
    user.save()
    # if is_password_random:
    # send_password(validated_data['email'], password)
    return True
