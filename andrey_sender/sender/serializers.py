from rest_framework import serializers
from .models import RecipientContact, User, ContactGroup, UserSenders
from .service import send_password, create_password


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
    contact_group = ContactGroupSerializer(many=True, required=False, read_only=True)
    senders = UserSendersGroupSerializer(many=True, required=False)

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
        contact_group_data = validated_data.pop('contact_group')
        senders_data = validated_data.pop('senders')
        recipient_contact = RecipientContact.objects.create(**validated_data)
        contact_group_list = []
        for group_data in contact_group_data:
            group, created = ContactGroup.objects.get_or_create(title=group_data['title'], user=recipient_contact.owner)
            group.recipient_contact.add(recipient_contact)
            contact_group_list.append(group)
        recipient_contact.contact_group.set(contact_group_list)
        recipient_contact.senders.set(senders_data)
        return recipient_contact

    def update(self, instance, validated_data):
        instance.name = validated_data.get('name', instance.name)
        instance.surname = validated_data.get('surname', instance.surname)
        instance.phone = validated_data.get('phone', instance.phone)
        instance.email = validated_data.get('email', instance.email)
        instance.comment = validated_data.get('comment', instance.comment)

        contact_group_data = validated_data.pop('contact_group', None)
        senders_data = validated_data.pop('senders', None)

        if contact_group_data is not None:
            contact_group_list = []
            for group_data in contact_group_data:
                group, created = ContactGroup.objects.get_or_create(title=group_data['title'], user=instance.owner)
                group.recipient_contact.add(instance)
                contact_group_list.append(group)
            instance.contact_group.set(contact_group_list)

        if senders_data is not None:
            instance.senders.set(senders_data)

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
