from django.urls import path, include, re_path
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView, TokenVerifyView

from .views import ContactViewSet, RegistrationViewSet, CheckAllWhatsAppNumber, LoginWhatsAppAccount, \
    CheckWhatsAppContactsGroups, EmailAccountViewSet, WhatsAppAccountViewSet, ContactDeleteSeveral, ContactGroupRest, \
    GetContactsInGroupCount, LoadContactImportFile, ContactRunImport, ImportViewSet, ImportBugsFileAPIView, \
    DeleteNotCompleteImport, CheckWhatsAppRun, WhatsAppSenderRun, GetQrCode, LoginSessionCheck, SenderStatistic, \
    CheckIsValidationSuccessPass, CheckIsSuccessFinished, CheckContactStatus, SendersGet, SendersList, EmailCheck, \
    EmailSenderRun

urlpatterns = [
    # авторизация черех JVT
    # это все инкапсулировано, пока не трогаю
    path('token', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('token/refresh', TokenRefreshView.as_view(), name='token_refresh'),
    path('token/verify', TokenVerifyView.as_view(), name='token_verify'),
    # авторизация по токенам
    # это все инкапсулировано, пока не трогаю
    path('auth', include('djoser.urls')),
    re_path(r'api/v1^auth', include('djoser.urls.authtoken')),
    # Взаимодействие с юзером:
    path('user/create', RegistrationViewSet.as_view({'post': 'create'}), name="user_create"),
    path('user/update/<str:username>', RegistrationViewSet.as_view({'patch': 'partial_update'}), name="user_update"),
    path('user/<str:username>', RegistrationViewSet.as_view({'get': 'retrieve'}), name="user_get"),
    path('user/del/<str:username>', RegistrationViewSet.as_view({'delete': 'destroy'}), name="user_del"),
    # Взаимодействие с контактами
    path('contact/list', ContactViewSet.as_view({'get': 'list'}), name="contact_list"),
    path('contact/<int:pk>', ContactViewSet.as_view({'get': 'retrieve'}), name="contact_detail"),
    path('contact/create', ContactViewSet.as_view({'post': 'create'}), name="contact_create"),
    path('contact/update/<int:pk>', ContactViewSet.as_view({'patch': 'partial_update'}), name="contact_update"),
    path('contact/del/<int:pk>', ContactViewSet.as_view({'delete': 'destroy'}), name="contact_delete"),
    path('contact/delete_several', ContactDeleteSeveral.as_view(), name="contact_several_delete"),
    path('contact:check_all_whats_app_number', CheckAllWhatsAppNumber.as_view()),
    path('contact:check_whats_app_number', CheckWhatsAppContactsGroups.as_view()),
    path('contact/check_wa_number/status/<int:stat_id>', CheckContactStatus.as_view()),
    path('contact/get_in_group_count/<int:pk>', GetContactsInGroupCount.as_view(), name="contact_count_in_group"),

    # email sender accounts
    path("send_account/email/<int:pk>", EmailAccountViewSet.as_view({'get': 'retrieve'}), name="email_get"),
    path("send_account/email/list", EmailAccountViewSet.as_view({'get': 'list'}), name="email_list"),
    path("send_account/email/create", EmailAccountViewSet.as_view({'post': 'create'}), name="email_create"),
    path("send_account/update/email/<int:pk>", EmailAccountViewSet.as_view({'patch': 'partial_update'}),
         name="email_update"),
    path("send_account/email/del/<int:pk>", EmailAccountViewSet.as_view({'delete': 'destroy'}), name="email_dell"),
    path("send_account/email/check_several", EmailCheck.as_view(), name="email_check_several"),
    path("send_account/email/check_all", EmailCheck.as_view(), name="all_email_check"),

    # WHATSAPP
    path("send_account/whatsApp/<int:pk>", WhatsAppAccountViewSet.as_view({'get': 'retrieve'}), name="WA_get"),
    path("send_account/whatsApp/list", WhatsAppAccountViewSet.as_view({'get': 'list'}), name="WA_list"),
    path("send_account/whatsApp/create", WhatsAppAccountViewSet.as_view({'post': 'create'}), name="WA_create"),
    path("send_account/update/whatsApp/<int:pk>", WhatsAppAccountViewSet.as_view({'patch': 'partial_update'}),
         name="WA_update"),
    path("send_account/whatsApp/del/<int:pk>", WhatsAppAccountViewSet.as_view({'delete': 'destroy'}), name="WA_dell"),

    path("send_account/whatsApp/login/<int:WA_id>", LoginWhatsAppAccount.as_view(), name="WA_login"),
    path("send_account/whatsApp/login_get_qr/<int:WA_id>", GetQrCode.as_view(), name="WA_login_get_qr"),
    path("send_account/whatsApp/login_check_result/<int:WA_id>", LoginSessionCheck.as_view(), name="WA_login_get_qr"),

    path("send_account/whatsApp/check_login_run/<int:WA_id>", CheckWhatsAppRun.as_view(),
         name="WA_check_login"),

    # Группы контактов
    # rest
    path("contact_group/<int:pk>", ContactGroupRest.as_view({'get': 'retrieve'}), name="contact_group_get"),
    path("contact_group/list", ContactGroupRest.as_view({'get': 'list'}), name="contact_group_list"),
    path("contact_group/create", ContactGroupRest.as_view({'post': 'create'}), name="contact_group_create"),
    path("contact_group/update/<int:pk>", ContactGroupRest.as_view({'patch': 'partial_update'}),
         name="contact_group_update"),
    path("contact_group/replace/<int:pk>", ContactGroupRest.as_view({'put': 'update'}),
         name="contact_group_replace"),
    path("contact_group/del/<int:pk>", ContactGroupRest.as_view({'delete': 'destroy'}), name="contact_group_delete"),

    # import
    path("import/<int:pk>", ImportViewSet.as_view({'get': 'retrieve'}), name="import_get"),
    path("import/list", ImportViewSet.as_view({'get': 'list'}), name="import_list"),
    path("import/file_upload", LoadContactImportFile.as_view(), name="import_file_upload"),
    path("import/run", ContactRunImport.as_view(), name="import_run"),
    path("import/errors_file/<int:import_id>", ImportBugsFileAPIView.as_view(), name="import_report"),
    path("import/delete/<int:import_id>", DeleteNotCompleteImport.as_view(), name="import_delete"),

    # Рассылки - общее
    path("mailing/<int:pk>", SendersGet.as_view(), name="sender_get"),
    path("mailing/list", SendersList.as_view(), name="sender_list"),
    path("mailing/statistic/<int:id>", SenderStatistic.as_view(), name="sender_statistic"),
    path("mailing/statistic/<int:id>", SenderStatistic.as_view(), name="sender_statistic"),
    path("mailing/is_success_finished/<int:sender_id>", CheckIsSuccessFinished.as_view(),
         name="WA_sender_is_success_finished"),

    # рассылки WhatsApp
    path("mailing/WhatsApp/create", WhatsAppSenderRun.as_view(), name="WA_sender_create"),
    path("mailing/WhatsApp/is_validation_passed/<int:sender_id>", CheckIsValidationSuccessPass.as_view(),
         name="WA_sender_is_validation_passed"),


    # Рассылки Email
    path("mailing/Email/create", EmailSenderRun.as_view(), name="email_sender_create"),

]
