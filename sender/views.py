import datetime

from rest_framework import viewsets, permissions
from .models import RecipientContact, User, SenderPhoneNumber, SenderEmail
from .serializers import RecipientContactSerializer, UserSerializer, EmailAccountSerializer, WhatsAppAccountSerializer
from rest_framework import status
from rest_framework.response import Response
from .services.user_service import user_create
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from .services.whats_app_utils import get_active_whatsapp_account, check_whatsapp_contacts, login_to_wa_account, \
    get_user_queryset
from django.core.exceptions import ObjectDoesNotExist


class WhatsAppAccountViewSet(viewsets.ModelViewSet):
    serializer_class = WhatsAppAccountSerializer
    permission_classes = [permissions.IsAuthenticated]

    def perform_create(self, serializer):
        serializer.save(owner=self.request.user)

    def get_queryset(self):
        qs = SenderPhoneNumber.objects.filter(owner=self.request.user)
        return qs


class EmailAccountViewSet(viewsets.ModelViewSet):
    serializer_class = EmailAccountSerializer
    permission_classes = [permissions.IsAuthenticated]

    def perform_create(self, serializer):
        serializer.save(owner=self.request.user)

    def get_queryset(self):
        return SenderEmail.objects.filter(owner=self.request.user)


class ContactViewSet(viewsets.ModelViewSet):
    serializer_class = RecipientContactSerializer
    permission_classes = [permissions.IsAuthenticated]

    def perform_create(self, serializer):
        serializer.save(owner=self.request.user)

    def get_queryset(self):
        return RecipientContact.objects.filter(owner=self.request.user)


class CheckAllWhatsAppNumber(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        user = self.request.user
        auth_account = get_active_whatsapp_account(user=user)
        if auth_account:
            contacts_for_checking = RecipientContact.objects.filter(owner=user, phone__isnull=False,
                                                                    is_phone_whatsapp_reg=False)
            check_whatsapp_contacts(contacts_for_checking, auth_account)
            return Response(status=200)
        else:
            "возвращаем ошибку в стиле авторизуйтесь в WhatsApp"
            return Response(status=400)


class CheckWhatsAppContactsGroups(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        user = self.request.user
        groups = request.data.get("groups")
        users = request.data.get("users")
        auth_account = get_active_whatsapp_account(user=user)
        if auth_account:
            all_checking_obj = get_user_queryset(groups, users, self.request.user)
            check_whatsapp_contacts(all_checking_obj, auth_account)
            return Response(status=200)
        else:
            "возвращаем ошибку в стиле авторизуйтесь в WhatsApp"
            return Response(status=400)


class LoginWhatsAppAccount(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, WA_id):
        user = request.user
        try:
            response_data = {
                "status": "FAIL TRY AGAIN"
            }
            check_phone_obj = SenderPhoneNumber.objects.get(owner=user, id=WA_id)

            if login_to_wa_account(session_number=check_phone_obj.session_number):
                check_phone_obj.is_login = True
                check_phone_obj.login_date = datetime.datetime.now()
                check_phone_obj.save()
                response_data["status"] = "OK"
                return Response(status=200, data=response_data)
            else:
                return Response(status=400, data=response_data)
        except ObjectDoesNotExist:
            return Response(status=404, data={"Такого аккаунта для рассылки Whats App не добавлено"})


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
