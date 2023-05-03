from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase


class RecipientContactCreateTest(APITestCase):
    def test_create_account_1(self):
        url = reverse('contact_create')
        data = {
            'email': "eaqwwda@yandex.ru"
        }
        response = self.client.post(url, data, format='json')
