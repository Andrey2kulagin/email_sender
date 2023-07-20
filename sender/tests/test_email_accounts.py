from rest_framework.test import APITestCase
from ..models import User, SenderEmail
from rest_framework.authtoken.models import Token
from django.urls import reverse


class RecipientContactCreateTest(APITestCase):

    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser', email='testuser@mail.com', password='password')
        self.token = Token.objects.create(user=self.user)
        self.token.save()
        self.email_1 = SenderEmail.objects.create(owner=self.user, contact="test_email@yandex.com",
                                                  title="email1", password="qwer123", is_check_pass=True)
        self.email_2 = SenderEmail.objects.create(owner=self.user, contact="test_email1@yandex.com",
                                                  title="email1", password="qwer123", is_check_pass=True)

    def test_get_email_1(self):
        url = reverse('email_get', kwargs={'pk': 1})
        self.client.force_authenticate(user=self.user, token=self.token)
        response = self.client.get(url, format='json')
        data = response.data
        self.assertEqual(200, response.status_code)
        self.assertEqual(self.email_1.contact, data["contact"])
        self.assertEqual(self.email_1.title, data["title"])
        self.assertEqual(self.email_1.is_check_pass, data["is_check_pass"])
        self.assertEqual(self.email_1.checked_date, data["checked_date"])

    def test_get_email_2(self):
        url = reverse('email_get', kwargs={'pk': 1})
        response = self.client.get(url, format='json')
        data = response.data
        self.assertEqual(401, response.status_code)

    def test_get_email_3(self):
        url = reverse('email_get', kwargs={'pk': 1358443})
        self.client.force_authenticate(user=self.user, token=self.token)
        response = self.client.get(url, format='json')
        data = response.data
        self.assertEqual(404, response.status_code)

    def test_list_email_1(self):
        url = reverse('email_list')
        self.client.force_authenticate(user=self.user, token=self.token)
        response = self.client.get(url, format='json')
        data = response.data
        self.assertEqual(200, response.status_code)
        self.assertEqual(self.email_1.contact, data[0]["contact"])
        self.assertEqual(self.email_1.title, data[0]["title"])
        self.assertEqual(self.email_1.is_check_pass, data[0]["is_check_pass"])
        self.assertEqual(self.email_1.checked_date, data[0]["checked_date"])

        self.assertEqual(self.email_2.contact, data[1]["contact"])
        self.assertEqual(self.email_2.title, data[1]["title"])
        self.assertEqual(self.email_2.is_check_pass, data[1]["is_check_pass"])
        self.assertEqual(self.email_2.checked_date, data[1]["checked_date"])

    def test_create_email_1(self):
        url = reverse('email_create')
        request_data = {
            "contact": "qwer123@mail.ru",
            "password": "qewewrrwerwe"
        }
        self.client.force_authenticate(user=self.user, token=self.token)
        response = self.client.post(url, format='json', data=request_data)
        data = response.data
        self.assertEqual(201, response.status_code)
        self.assertEqual(request_data["contact"], data["contact"])
        self.assertEqual(3, data["id"])
        self.assertEqual(None, data["is_check_pass"])
        self.assertEqual(None, data.title)
        obj = SenderEmail.objects.get(id=3)
        self.assertEqual(request_data["contact"], obj["contact"])
        self.assertEqual(request_data["password"], obj["password"])
        self.assertEqual(self.user, obj["owner"])
        self.assertEqual(3, obj["id"])
        self.assertEqual(None, obj["is_check_pass"])
        self.assertEqual(None, obj["title"])
