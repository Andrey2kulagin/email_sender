from django.urls import path
from .views import ContactViewSet

urlpatterns = [
    path('api/v1/contact/list', ContactViewSet.as_view({'get': 'list'})),
    path('api/v1/contact/<int:pk>', ContactViewSet.as_view({'get': 'retrieve'})),
    path('api/v1/contact/update/<int:pk>', ContactViewSet.as_view({'put': 'update'})),
    path('api/v1/contact/del/<int:pk>', ContactViewSet.as_view({'delete': 'destroy'})),
]
