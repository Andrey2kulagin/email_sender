from django.urls import path, include
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView, TokenVerifyView

from .views import ContactViewSet, RegistrationView

urlpatterns = [
    path('api/v1/token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('api/v1/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('api/v1/token/verify/', TokenVerifyView.as_view(), name='token_verify'),
    path('api/v1/user/reg', RegistrationView.as_view()),
    path('api/v1/contact/list', ContactViewSet.as_view({'get': 'list'})),
    path('api/v1/contact/<int:pk>', ContactViewSet.as_view({'get': 'retrieve'})),
    path('api/v1/contact/create', ContactViewSet.as_view({'post': 'create'})),
    path('api/v1/contact/create/<int:pk>', ContactViewSet.as_view({'put': 'update'})),
    path('api/v1/contact/del/<int:pk>', ContactViewSet.as_view({'delete': 'destroy'})),
]
