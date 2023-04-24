from django.shortcuts import render
from rest_framework import viewsets, permissions, generics
from .models import RecipientContact, User
from .serializers import RecipientContactSerializer, UserSerializer
from django.contrib.auth.views import LoginView


class ContactViewSet(viewsets.ModelViewSet):
    serializer_class = RecipientContactSerializer
    permission_classes = [permissions.IsAuthenticated]

    def perform_create(self, serializer):
        serializer.save(owner=self.request.user)

    def get_queryset(self):
        return RecipientContact.objects.filter(owner=self.request.user)


class RegistrationView(generics.CreateAPIView):
    serializer_class = UserSerializer
    queryset = User.objects.all()
    permission_classes = [permissions.AllowAny]
