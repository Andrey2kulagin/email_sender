from rest_framework import serializers
from .models import RecipientContact


class RecipientContactSerializer(serializers.ModelSerializer):
    class Meta:
        model = RecipientContact
        fields = ('owner', 'contact', 'type', 'contact_group')
