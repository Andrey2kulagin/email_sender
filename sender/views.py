from django.shortcuts import render
from rest_framework import viewsets, permissions, generics
from .models import RecipientContact, User
from .serializers import RecipientContactSerializer, UserSerializer
from django.contrib.auth.views import LoginView
from django.core.mail import send_mail
from rest_framework import status
from rest_framework.response import Response
from .services.user_service import user_create


class ContactViewSet(viewsets.ModelViewSet):
    serializer_class = RecipientContactSerializer
    permission_classes = [permissions.IsAuthenticated]

    def perform_create(self, serializer):
        serializer.save(owner=self.request.user)

    def get_queryset(self):
        return RecipientContact.objects.filter(owner=self.request.user)


class RegistrationViewSet(viewsets.ModelViewSet):
    serializer_class = UserSerializer
    queryset = User.objects.all()
    permission_classes = [permissions.AllowAny]

    def update(self, request, *args, **kwargs):
        # Изменяем поиск модели для изменения
        self.lookup_field = 'username'
        # Вызываем оригинальный метод viewset
        response = super().update(request, *args, **kwargs)
        return response

    def retrieve(self, request, *args, **kwargs):
        # Изменяем поиск модели для изменения
        self.lookup_field = 'username'
        # Вызываем оригинальный метод viewset
        response = super().retrieve(request, *args, **kwargs)
        return response

    def destroy(self, request, *args, **kwargs):
        # Изменяем поиск модели для изменения
        self.lookup_field = 'username'
        # Вызываем оригинальный метод viewset
        response = super().destroy(request, *args, **kwargs)
        return response

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        user_create(serializer)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    def get_serializer(self, *args, **kwargs):
        serializer = super().get_serializer(*args, **kwargs)

        # Добавляем правила валидации
        if self.action == 'create':
            serializer.fields['email'].required = True
        elif self.action == 'update':
            serializer.fields['email'].required = False

        return serializer
