from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase
from ..models import User, UserSenders, ContactGroup, UserLetterText
from rest_framework.authtoken.models import Token


class RecipientContactCreateTest(APITestCase):

    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser', email='testuser@mail.com', password='password')
        self.token = Token.objects.create(user=self.user)
        self.token.save()
        self.second_user = User.objects.create_user(
            username='seconduser', email='testur@mail.com', password='password')
        self.first_user_group1 = ContactGroup.objects.create(user=self.user, title="Группа1 1 юзера")
        self.first_user_group2 = ContactGroup.objects.create(user=self.user, title="Группа2 1 юзера")
        self.first_user_group3 = ContactGroup.objects.create(user=self.user, title="Группа3 1 юзера")
        self.second_user_group1 = ContactGroup.objects.create(user=self.second_user, title="Группа1 2 юзера")
        self.second_user_group2 = ContactGroup.objects.create(user=self.second_user, title="Группа2 2 юзера")
        self.second_user_group3 = ContactGroup.objects.create(user=self.second_user, title="Группа3 2 юзера")

        self.user1_letter_text = UserLetterText.objects.create(user=self.user, title="title1",
                                                               letter_subject="letter_subject1", text="textlkajd")
        self.user2_letter_text = UserLetterText.objects.create(user=self.second_user, title="title1",
                                                               letter_subject="letter_subject1", text="textlkajd")

        self.first_user_sender1 = UserSenders.objects.create(user=self.user, text=self.user1_letter_text,
                                                             count_letter=300, comment="qwer", title="title")
        self.first_user_sender2 = UserSenders.objects.create(user=self.user, text=self.user1_letter_text,
                                                             count_letter=300, comment="qwer", title="title")
        self.first_user_sender3 = UserSenders.objects.create(user=self.user, text=self.user1_letter_text,
                                                             count_letter=300, comment="qwer", title="title")
        self.second_user_sender1 = UserSenders.objects.create(user=self.second_user, text=self.user1_letter_text,
                                                              count_letter=300, comment="qwer", title="title")
        self.second_user_sender2 = UserSenders.objects.create(user=self.second_user, text=self.user1_letter_text,
                                                              count_letter=300, comment="qwer", title="title")
        self.second_user_sender3 = UserSenders.objects.create(user=self.second_user, text=self.user1_letter_text,
                                                              count_letter=300, comment="qwer", title="title")

    def test_create_contact_1(self):
        url = reverse('contact_create')
        data = {
            'email': "eaqwwda@yandex.ru"
        }
        self.client.force_authenticate(user=self.user, token=self.token)
        response = self.client.post(url, data, format='json')
        data = response.data
        self.assertEqual(201, response.status_code)
        self.assertEqual(self.user.id, data["owner"])
        self.assertEqual(None, data["name"])
        self.assertEqual(None, data["surname"])
        self.assertEqual(None, data["phone"])
        self.assertEqual("eaqwwda@yandex.ru", data["email"])
        self.assertEqual([], data["contact_group"])
        self.assertEqual([], data["senders"])
        self.assertEqual(None, data["comment"])

    def test_create_contact_2(self):
        url = reverse('contact_create')
        data = {
        }
        self.client.force_authenticate(user=self.user, token=self.token)
        response = self.client.post(url, data, format='json')
        self.assertEqual(400, response.status_code)

    def test_create_contact_3(self):
        url = reverse('contact_create')
        data = {
            'email': "eaqwwda@ndexru"
        }
        self.client.force_authenticate(user=self.user, token=self.token)
        response = self.client.post(url, data, format='json')
        self.assertEqual(400, response.status_code)

    def test_create_contact_4(self):
        url = reverse('contact_create')
        data = {
            'email': "eaqwwda@yandex.ru",
            'name': "andrey",
            'surname': "my_surname",
            'phone': '89753428790',
            'contact_group': [1, 2, 3],
            "senders": [1, 2, 3],
            'comment': 'smart comment',
        }
        self.client.force_authenticate(user=self.user, token=self.token)
        response = self.client.post(url, data, format='json')
        data = response.data
        self.assertEqual(201, response.status_code)
        self.assertEqual(self.user.id, data["owner"])
        self.assertEqual("andrey", data["name"])
        self.assertEqual("my_surname", data["surname"])
        self.assertEqual("79753428790", data["phone"])
        self.assertEqual("eaqwwda@yandex.ru", data["email"])
        self.assertEqual([1, 2, 3], data["contact_group"])
        self.assertEqual([1, 2, 3], data["senders"])
        self.assertEqual('smart comment', data["comment"])

    def test_create_contact_5(self):
        url = reverse('contact_create')
        data = {
            'email': "eaqwwda@ndexru"
        }
        response = self.client.post(url, data, format='json')
        self.assertEqual(401, response.status_code)

    def test_create_contact_6(self):
        url = reverse('contact_create')
        data = {
            'email': "eaqwwda@yandex.ru",
            'name': "andrey",
            'surname': "my_surname",
            'phone': '+89753428790',
            'contact_group': [1, 2, 3],
            "senders": [1, 2, 3],
            'comment': 'smart comment',
        }
        self.client.force_authenticate(user=self.user, token=self.token)
        response = self.client.post(url, data, format='json')
        self.assertEqual(400, response.status_code)

    def test_create_contact_7(self):
        url = reverse('contact_create')
        data = {
            'email': "eaqwwda@yandex.ru",
            'name': "andrey",
            'surname': "my_surname",
            'contact_group': [1, 2, 3],
            "senders": [1, 2, 3],
            'comment': 'smart comment',
        }
        self.client.force_authenticate(user=self.user, token=self.token)
        response = self.client.post(url, data, format='json')
        response = self.client.post(url, data, format='json')
        self.assertEqual(400, response.status_code)

    def test_create_contact_8(self):
        url = reverse('contact_create')
        data = {
            'email': "eaqwwda@yandex.ru",
            'name': "andrey",
            'surname': "my_surname",
            'phone': '+79753428790',
            'contact_group': [1, 2, 3],
            "senders": [1, 2, 3],
            'comment': 'smart comment',
        }
        self.client.force_authenticate(user=self.user, token=self.token)
        response = self.client.post(url, data, format='json')
        data = response.data
        self.assertEqual(201, response.status_code)
        self.assertEqual(self.user.id, data["owner"])
        self.assertEqual("andrey", data["name"])
        self.assertEqual("my_surname", data["surname"])
        self.assertEqual("79753428790", data["phone"])
        self.assertEqual("eaqwwda@yandex.ru", data["email"])
        self.assertEqual([1, 2, 3], data["contact_group"])
        self.assertEqual([1, 2, 3], data["senders"])
        self.assertEqual('smart comment', data["comment"])
        response = self.client.post(url, data, format='json')
        self.assertEqual(400, response.status_code)

    def test_create_contact_9(self):
        url = reverse('contact_create')
        data = {
            'email': "eaqwwdayandex.ru",
            'name': "andrey",
            'surname': "my_surname",
            'phone': '+79753428790',
            'contact_group': [1, 2, 3],
            "senders": [1, 2, 3],
            'comment': 'smart comment',
        }
        self.client.force_authenticate(user=self.user, token=self.token)
        response = self.client.post(url, data, format='json')
        data = response.data
        print(data)
        self.assertEqual(400, response.status_code)

