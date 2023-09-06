import datetime

from rest_framework import viewsets, permissions
from rest_framework.viewsets import GenericViewSet

from .models import RecipientContact, User, SenderPhoneNumber, SenderEmail, ContactGroup, ContactImportFiles, AdminData
from .serializers import RecipientContactSerializer, UserSerializer, EmailAccountSerializer, WhatsAppAccountSerializer, \
    ContactGroupSerializer, ImportFileUploadSerializer, ContactRunImportSerializer, ImportSerializer, WASenderSerializer
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from .services.whats_app_utils import get_active_whatsapp_account, check_whatsapp_contacts, get_user_queryset, \
    check_login_view, get_qr_handler, check_is_login_wa_account_obj, check_cure_login_session
from .services.user_service import user_create
from .services.contact_service import delete_several_contacts, get_group_contact_count
from django.core.exceptions import ObjectDoesNotExist
from .paginations import DefaultPagination
from .services.contact_import_service import file_upload_handler, contact_import, gen_path_to_import_report, \
    delete_not_complete_import
from rest_framework import mixins
from django.http import FileResponse
from rest_framework_simplejwt.views import TokenObtainPairView
from .services.WA_sender_service import sender_handler
from .tasks import wa_login_task, wa_login_check_task


class WhatsAppSenderRun(APIView):
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = WASenderSerializer

    def post(self, request, *args, **kwargs):
        serializer = WASenderSerializer(data=request.data, context={'request': request})
        if serializer.is_valid(raise_exception=True):
            validated_data = serializer.validated_data
            user = request.user
            sender_handler(validated_data, user)
            return Response(status=200)
        else:
            return Response(status=400)


class MyTokenObtainPairView(TokenObtainPairView):
    def post(self, request, *args, **kwargs):
        response = super().post(request, *args, **kwargs)
        token = response.data.get("refresh")
        if token:
            response.set_cookie("refresh", token, httponly=True)


class DeleteNotCompleteImport(APIView):
    def delete(self, request, import_id):
        return delete_not_complete_import(import_id, request)


class ImportBugsFileAPIView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request, import_id):
        # Путь к файлу, который нужно вернуть
        user = request.user
        res = gen_path_to_import_report(user, import_id)
        if type(res) != str:
            return Response(status=res)
        # Открываем файл в режиме "бинарное чтение"
        file = open(res, 'rb')

        # Возвращаем файл в ответ на GET-запрос
        response = FileResponse(file)
        return response


class ImportViewSet(mixins.RetrieveModelMixin, mixins.ListModelMixin, GenericViewSet):
    serializer_class = ImportSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        qs = ContactImportFiles.objects.filter(owner=self.request.user, is_imported=True).order_by('-date')
        return qs


class ContactRunImport(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        serializer = ContactRunImportSerializer(data=request.data, context={'request': request})
        if serializer.is_valid():
            user = request.user
            validated_data = serializer.validated_data
            statistics = contact_import(validated_data, user)
            response_data = {
                "all_handled_lines": statistics["all_count"],
                "success_create_update_count": statistics["OK"],
                "partial_success_create_update_count": statistics["PF"],
                "fail_count": statistics["FF"]
            }
            return Response(status=200, data=response_data)
        return Response(status=400, data=serializer.errors)


class LoadContactImportFile(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        serializer = ImportFileUploadSerializer(data=request.data)
        if serializer.is_valid():
            file = serializer.validated_data['file']
            user = request.user
            is_contains_headers = serializer.validated_data['is_contains_headers']
            return file_upload_handler(file, user, is_contains_headers)
        else:
            return Response(serializer.errors, status=400)


class ContactGroupRest(viewsets.ModelViewSet):
    serializer_class = ContactGroupSerializer
    permission_classes = [permissions.IsAuthenticated]
    http_method_names = ['get', 'post', 'patch', 'delete']

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

    def get_queryset(self):
        qs = ContactGroup.objects.filter(user=self.request.user)
        return qs


class GetContactsInGroupCount(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, pk):
        if ContactGroup.objects.filter(user=request.user, id=pk).count() == 0:
            return Response(status=status.HTTP_404_NOT_FOUND)
        return Response(status=200, data={"count": get_group_contact_count(request.user, pk)})


class ContactDeleteSeveral(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        user = request.user
        groups = request.data.get("groups_ids", [])
        contacts = request.data.get("contact_ids", [])
        data = delete_several_contacts(user, contacts, groups)
        return Response(status=200, data=data)


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
    pagination_class = DefaultPagination

    def perform_create(self, serializer):
        serializer.save(owner=self.request.user)

    def get_queryset(self):
        return RecipientContact.objects.filter(owner=self.request.user)


class CheckAllWhatsAppNumber(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        user = self.request.user
        auth_account = get_active_whatsapp_account(user=user)
        print(auth_account)
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
        groups = request.data.get("groups_id")
        users = request.data.get("contacts_id")
        auth_account = get_active_whatsapp_account(user=user)
        if auth_account:
            all_checking_obj = get_user_queryset(groups, users, self.request.user)
            check_whatsapp_contacts(all_checking_obj, auth_account)
            return Response(status=200)
        else:
            "возвращаем ошибку в стиле авторизуйтесь в WhatsApp"
            return Response(status=400)


class CheckWhatsAppRun(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, WA_id):
        user = request.user
        try:
            account = SenderPhoneNumber.objects.get(owner=user, id=WA_id)
            if check_cure_login_session(account):
                return Response(status=409, data={"message": "У вас уже запущена сессия"})
            wa_login_check_task.delay(WA_id)
            return Response(status=200)
        except ObjectDoesNotExist:
            return Response(status=404, data={"Такого аккаунта для рассылки Whats App не добавлено"})


class LoginWhatsAppAccount(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, WA_id):
        user = request.user
        try:
            account = SenderPhoneNumber.objects.get(owner=user, id=WA_id)
            if check_cure_login_session(account):
                return Response(status=409, data={"message": "У вас уже запущена сессия"})
            wa_login_task.delay(wa_id=WA_id)
            return Response(status=200)
        except ObjectDoesNotExist:
            return Response(status=404, data={"message": "Такого аккаунта для рассылки Whats App не добавлено"})


class LoginSessionCheck(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, WA_id):
        status_code, body = check_is_login_wa_account_obj(request.user, WA_id)
        return Response(status=status_code, data=body)


class GetQrCode(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, WA_id):
        user = request.user
        session_status, data = get_qr_handler(user, WA_id)
        return Response(status=session_status, data=data)


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
