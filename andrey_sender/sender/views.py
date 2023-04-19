from django.shortcuts import render
from rest_framework import viewsets, permissions
from .models import RecipientContact
from .serializers import RecipientContactSerializer


# Create your views here.
class ContactViewSet(viewsets.ModelViewSet):
    serializer_class = RecipientContactSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return RecipientContact.objects.filter(owner=self.request.user)
