from django.urls import path, include, re_path
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView, TokenVerifyView

from .views import ContactViewSet, RegistrationViewSet

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
    # здесь надо поправить бизнес-логику и обработку исключений
    path('user/create', RegistrationViewSet.as_view({'post': 'create'})),
    path('user/update/<str:username>', RegistrationViewSet.as_view({'patch': 'partial_update'})),
    path('user/<str:username>', RegistrationViewSet.as_view({'get': 'retrieve'})),
    path('user/del/<str:username>', RegistrationViewSet.as_view({'delete': 'destroy'})),
    # other
    path('contact/list', ContactViewSet.as_view({'get': 'list'}), name="contact_list"),
    path('contact/<int:pk>', ContactViewSet.as_view({'get': 'retrieve'}), name="contact_detail"),
    path('contact/create', ContactViewSet.as_view({'post': 'create'}), name="contact_create"),
    path('contact/update/<int:pk>', ContactViewSet.as_view({'patch': 'partial_update'}), name="contact_update"),
    path('contact/del/<int:pk>', ContactViewSet.as_view({'delete': 'destroy'}), name="contact_delete"),

    path('contact:check_all_whats_app_number'),
    path('contact:check_whats_app_number')


]
