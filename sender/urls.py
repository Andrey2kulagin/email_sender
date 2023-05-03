from django.urls import path, include, re_path
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView, TokenVerifyView

from .views import ContactViewSet, RegistrationViewSet

urlpatterns = [
    # авторизация черех JVT
    path('api/v1/token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('api/v1/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('api/v1/token/verify/', TokenVerifyView.as_view(), name='token_verify'),
    # авторизация по токенам
    path('api/v1/auth/', include('djoser.urls')),
    re_path(r'api/v1^auth/', include('djoser.urls.authtoken')),
    # Взаимодействие с юзером:
    path('api/v1/user/reg', RegistrationViewSet.as_view({'post': 'create'})),
    path('api/v1/user/update/<str:username>', RegistrationViewSet.as_view({'patch': 'update'})),
    path('api/v1/user/<str:username>', RegistrationViewSet.as_view({'get': 'retrieve'})),
    path('api/v1/user/del/<str:username>', RegistrationViewSet.as_view({'delete': 'destroy'})),
    # other
    path('api/v1/contact/list', ContactViewSet.as_view({'get': 'list'}), name="contact_list"),
    path('api/v1/contact/<int:pk>', ContactViewSet.as_view({'get': 'retrieve'}), name="contact_detail"),
    path('api/v1/contact/create', ContactViewSet.as_view({'post': 'create'}), name="contact_create"),
    path('api/v1/contact/update/<int:pk>', ContactViewSet.as_view({'patch': 'update'}), name="contact_update"),
    path('api/v1/contact/del/<int:pk>', ContactViewSet.as_view({'delete': 'destroy'}), name="contact_delete"),

]
