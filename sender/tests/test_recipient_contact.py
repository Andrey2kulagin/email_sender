from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase
from ..models import User, UserSenders, ContactGroup, UserLetterText, RecipientContact
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
        self.assertEqual(400, response.status_code)

    def test_create_contact_10(self):
        url = reverse('contact_create')
        data = {
            'name': "andrey",
            'surname': "my_surname",
            'contact_group': [1, 2, 3],
            "senders": [1, 2, 3],
            'comment': 'smart comment',
        }
        self.client.force_authenticate(user=self.user, token=self.token)
        response = self.client.post(url, data, format='json')
        self.assertEqual(400, response.status_code)

    def test_create_contact_11(self):
        url = reverse('contact_create')
        data = {
            'name': "andrey",
            'surname': "my_surname",
            'contact_group': [1, 2, 4],
            "senders": [1, 2, 3],
            'comment': 'smart comment',
        }
        self.client.force_authenticate(user=self.user, token=self.token)
        response = self.client.post(url, data, format='json')
        self.assertEqual(400, response.status_code)

    def test_create_contact_12(self):
        url = reverse('contact_create')
        data = {
            'name': "andrey",
            'surname': "my_surname",
            'contact_group': [1, 2, 3],
            "senders": [1, 2, 5],
            'comment': 'smart comment',
        }
        self.client.force_authenticate(user=self.user, token=self.token)
        response = self.client.post(url, data, format='json')
        self.assertEqual(400, response.status_code)


class RecipientContactUpdateTest(APITestCase):

    def setUp(self):
        # создание юзеров
        self.user = User.objects.create_user(
            username='testuser', email='testuser@mail.com', password='password')
        self.token = Token.objects.create(user=self.user)
        self.token.save()
        self.second_user = User.objects.create_user(
            username='seconduser', email='testur@mail.com', password='password')
        self.second_token = Token.objects.create(user=self.second_user)
        self.second_token.save()
        # Создание групп контактов
        self.first_user_group1 = ContactGroup.objects.create(user=self.user, title="Группа1 1 юзера")
        self.first_user_group2 = ContactGroup.objects.create(user=self.user, title="Группа2 1 юзера")
        self.first_user_group3 = ContactGroup.objects.create(user=self.user, title="Группа3 1 юзера")
        self.second_user_group1 = ContactGroup.objects.create(user=self.second_user, title="Группа1 2 юзера")
        self.second_user_group2 = ContactGroup.objects.create(user=self.second_user, title="Группа2 2 юзера")
        self.second_user_group3 = ContactGroup.objects.create(user=self.second_user, title="Группа3 2 юзера")
        groups_first_user = ContactGroup.objects.filter(user=self.user)
        groups_second_user = ContactGroup.objects.filter(user=self.second_user)
        # Создание писем
        self.user1_letter_text = UserLetterText.objects.create(user=self.user, title="title1",
                                                               letter_subject="letter_subject1", text="textlkajd")
        self.user2_letter_text = UserLetterText.objects.create(user=self.second_user, title="title1",
                                                               letter_subject="letter_subject1", text="textlkajd")
        # Создание рассылок
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
        senders_first_user = UserSenders.objects.filter(user=self.user)
        senders_second_user = UserSenders.objects.filter(user=self.second_user)
        # создание контактов
        self.first_user_contact_1 = RecipientContact.objects.create(owner=self.user, name="user1_name",
                                                                    surname="user1_surname", phone="89753412148",
                                                                    email="user1@mail.com", comment="comment")
        self.first_user_contact_1.contact_group.add(*groups_first_user)
        self.first_user_contact_1.senders.add(*senders_first_user)
        self.first_user_contact_2 = RecipientContact.objects.create(owner=self.user, name="user1_name",
                                                                    surname="user1_surname", phone="89753412148",
                                                                    email="user1@mail.com", comment="comment")
        self.first_user_contact_2.contact_group.add(*groups_first_user)
        self.first_user_contact_2.senders.add(*senders_first_user)

        self.first_user_contact_3 = RecipientContact.objects.create(owner=self.user, name="user1_name",
                                                                    surname="user1_surname", phone="89753412148",
                                                                    email="user1@mail.com", comment="comment")
        self.first_user_contact_3.contact_group.add(*groups_first_user)
        self.first_user_contact_3.senders.add(*senders_first_user)

        self.second_user_contact_1 = RecipientContact.objects.create(owner=self.second_user, name="user1_name",
                                                                     surname="user1_surname", phone="89753412148",
                                                                     email="user1@mail.com", comment="comment")
        self.second_user_contact_1.contact_group.add(*groups_second_user)
        self.second_user_contact_1.senders.add(*senders_second_user)

        self.second_user_contact_2 = RecipientContact.objects.create(owner=self.second_user, name="user1_name",
                                                                     surname="user1_surname", phone="89653412148",
                                                                     email="user1@mail.com", comment="comment")
        self.second_user_contact_2.contact_group.add(*groups_second_user)
        self.second_user_contact_2.senders.add(*senders_second_user)

        self.second_user_contact_3 = RecipientContact.objects.create(owner=self.second_user, name="user1_name",
                                                                     surname="user1_surname", phone="89753412148",
                                                                     email="user1@mail.com", comment="comment")
        self.second_user_contact_3.contact_group.add(*groups_second_user)
        self.second_user_contact_3.senders.add(*senders_second_user)

    def test_update_contact_1(self):
        url = reverse('contact_update', kwargs={'pk': 1})
        data = {
            'email': "eaqwwdayandex.ru"
        }
        self.client.force_authenticate(user=self.user, token=self.token)
        response = self.client.patch(url, data, format='json')
        self.assertEqual(400, response.status_code)

    def test_update_contact_2(self):
        url = reverse('contact_update', kwargs={'pk': 1})
        data = {
            'email': None,
            'phone': None
        }
        self.client.force_authenticate(user=self.user, token=self.token)
        response = self.client.patch(url, data, format='json')
        self.assertEqual(400, response.status_code)

    def test_update_contact_3(self):
        url = reverse('contact_update', kwargs={'pk': 2})
        data = {
            'email': "eaqwwda@yandex.ru",
            'phone': None
        }
        self.client.force_authenticate(user=self.user, token=self.token)
        response = self.client.patch(url, data, format='json')
        data = response.data
        self.assertEqual(200, response.status_code)
        self.assertEqual(None, data["phone"])
        self.assertEqual("eaqwwda@yandex.ru", data["email"])

    def test_update_contact_4(self):
        url = reverse('contact_update', kwargs={'pk': 2})
        data = {
            'email': "eaqwwda@yandex.ru",
            'phone': None
        }
        self.client.force_authenticate(user=self.user, token=self.token)
        self.client.patch(url, data, format='json')
        data = {
            'email': None,
            'phone': "89167853497"
        }
        response = self.client.patch(url, data, format='json')
        data = response.data
        self.assertEqual(200, response.status_code)
        self.assertEqual("79167853497", data["phone"])
        self.assertEqual(None, data["email"])

    def test_update_contact_5(self):
        url = reverse('contact_update', kwargs={'pk': 1})
        data = {
            'phone': "89753412148"
        }
        self.client.force_authenticate(user=self.user, token=self.token)
        response = self.client.patch(url, data, format='json')
        self.assertEqual(400, response.status_code)

    def test_update_contact_6(self):
        url = reverse('contact_update', kwargs={'pk': 2})
        data = {
            'phone': "89653412148"
        }
        self.client.force_authenticate(user=self.user, token=self.token)
        response = self.client.patch(url, data, format='json')
        data = response.data
        self.assertEqual(200, response.status_code)
        self.assertEqual("79653412148", data["phone"])

    def test_update_contact_7(self):
        url = reverse('contact_update', kwargs={'pk': 2})
        data = {
            'phone': "89653412148"
        }
        self.client.force_authenticate(user=self.second_user, token=self.second_token)
        response = self.client.patch(url, data, format='json')
        self.assertEqual(404, response.status_code)

    def test_update_contact_8(self):
        url = reverse('contact_update', kwargs={'pk': 2})
        data = {
            'phone': None
        }
        self.client.force_authenticate(user=self.user, token=self.token)
        self.client.patch(url, data, format='json')
        data = {
            'email': None,
        }
        response = self.client.patch(url, data, format='json')
        self.assertEqual(400, response.status_code)

    def test_update_contact_9(self):
        url = reverse('contact_update', kwargs={'pk': 2})
        data = {
            'email': None
        }
        self.client.force_authenticate(user=self.user, token=self.token)
        self.client.patch(url, data, format='json')
        data = {
            'phone': None,
        }
        response = self.client.patch(url, data, format='json')
        self.assertEqual(400, response.status_code)

    def test_update_contact_10(self):
        url = reverse('contact_update', kwargs={'pk': 2})
        data = {
            'name': 'new_name',
            'surname': 'new_surname',
            'phone': "89653412148",
            'email': 'newemail@yandex.ru',
            'contact_group': [1, 2],
            'senders': [2, 3],
            'comment': "qwert"
        }
        self.client.force_authenticate(user=self.user, token=self.token)
        response = self.client.patch(url, data, format='json')
        data = response.data
        self.assertEqual(200, response.status_code)
        self.assertEqual("new_name", data["name"])
        self.assertEqual("new_surname", data["surname"])
        self.assertEqual("79653412148", data["phone"])
        self.assertEqual([1, 2], data["contact_group"])
        self.assertEqual([2, 3], data["senders"])
        self.assertEqual("qwert", data["comment"])

    def test_update_contact_11(self):
        url = reverse('contact_update', kwargs={'pk': 2})
        data = {
            'name': 'new_name',
            'surname': 'new_surname',
            'phone': "89653412148",
            'email': 'newemail@yandex.ru',
            'contact_group': [1, 2],
            'senders': [2, 3, 4],
            'comment': "qwert"
        }
        self.client.force_authenticate(user=self.user, token=self.token)
        response = self.client.patch(url, data, format='json')
        self.assertEqual(400, response.status_code)

    def test_update_contact_12(self):
        url = reverse('contact_update', kwargs={'pk': 2})
        data = {
            'name': 'new_name',
            'surname': 'new_surname',
            'phone': "89653412148",
            'email': 'newemail@yandex.ru',
            'contact_group': [1, 2],
            'senders': [2, 3],
            'comment': "qwert"
        }
        response = self.client.patch(url, data, format='json')
        self.assertEqual(401, response.status_code)


class RecipientContactListDetailDeleteTest(APITestCase):

    def setUp(self):
        # создание юзеров
        self.user = User.objects.create_user(
            username='testuser', email='testuser@mail.com', password='password')
        self.token = Token.objects.create(user=self.user)
        self.token.save()
        self.second_user = User.objects.create_user(
            username='seconduser', email='testur@mail.com', password='password')
        self.second_token = Token.objects.create(user=self.second_user)
        self.second_token.save()
        # Создание групп контактов
        self.first_user_group1 = ContactGroup.objects.create(user=self.user, title="Группа1 1 юзера")
        self.first_user_group2 = ContactGroup.objects.create(user=self.user, title="Группа2 1 юзера")
        self.first_user_group3 = ContactGroup.objects.create(user=self.user, title="Группа3 1 юзера")
        self.second_user_group1 = ContactGroup.objects.create(user=self.second_user, title="Группа1 2 юзера")
        self.second_user_group2 = ContactGroup.objects.create(user=self.second_user, title="Группа2 2 юзера")
        self.second_user_group3 = ContactGroup.objects.create(user=self.second_user, title="Группа3 2 юзера")
        groups_first_user = ContactGroup.objects.filter(user=self.user)
        groups_second_user = ContactGroup.objects.filter(user=self.second_user)
        # Создание писем
        self.user1_letter_text = UserLetterText.objects.create(user=self.user, title="title1",
                                                               letter_subject="letter_subject1", text="textlkajd")
        self.user2_letter_text = UserLetterText.objects.create(user=self.second_user, title="title1",
                                                               letter_subject="letter_subject1", text="textlkajd")
        # Создание рассылок
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
        senders_first_user = UserSenders.objects.filter(user=self.user)
        senders_second_user = UserSenders.objects.filter(user=self.second_user)
        # создание контактов
        self.first_user_contact_1 = RecipientContact.objects.create(owner=self.user, name="user1_name",
                                                                    surname="user1_surname", phone="89753412148",
                                                                    email="user1@mail.com", comment="comment")
        self.first_user_contact_1.contact_group.add(*groups_first_user)
        self.first_user_contact_1.senders.add(*senders_first_user)
        self.first_user_contact_2 = RecipientContact.objects.create(owner=self.user, name="user1_name2",
                                                                    surname="user1_surname2", phone="89753412148",
                                                                    email="user1@mail.com", comment="comment")
        self.first_user_contact_2.contact_group.add(*groups_first_user)
        self.first_user_contact_2.senders.add(*senders_first_user)

        self.first_user_contact_3 = RecipientContact.objects.create(owner=self.user, name="user1_name",
                                                                    surname="user1_surname", phone="89753412148",
                                                                    email="user1@mail.com", comment="comment")
        self.first_user_contact_3.contact_group.add(*groups_first_user)
        self.first_user_contact_3.senders.add(*senders_first_user)

        self.second_user_contact_1 = RecipientContact.objects.create(owner=self.second_user, name="user1_name",
                                                                     surname="user1_surname", phone="89753412148",
                                                                     email="user1@mail.com", comment="comment")
        self.second_user_contact_1.contact_group.add(*groups_second_user)
        self.second_user_contact_1.senders.add(*senders_second_user)

        self.second_user_contact_2 = RecipientContact.objects.create(owner=self.second_user, name="user1_name",
                                                                     surname="user1_surname", phone="89653412148",
                                                                     email="user1@mail.com", comment="comment")
        self.second_user_contact_2.contact_group.add(*groups_second_user)
        self.second_user_contact_2.senders.add(*senders_second_user)

        self.second_user_contact_3 = RecipientContact.objects.create(owner=self.second_user, name="user1_name",
                                                                     surname="user1_surname", phone="89753412148",
                                                                     email="user1@mail.com", comment="comment")
        self.second_user_contact_3.contact_group.add(*groups_second_user)
        self.second_user_contact_3.senders.add(*senders_second_user)

    def test_list_contact_1(self):
        url = reverse('contact_list')
        self.client.force_authenticate(user=self.user, token=self.token)
        response = self.client.get(url, format='json')
        data = response.data
        self.assertEqual(200, response.status_code)
        self.assertEqual(3, len(data))

    def test_list_contact_2(self):
        url = reverse('contact_list')
        response = self.client.get(url, format='json')
        self.assertEqual(401, response.status_code)

    def test_detail_contact_1(self):
        url = reverse('contact_detail', kwargs={'pk': 2})
        self.client.force_authenticate(user=self.user, token=self.token)
        response = self.client.get(url, format='json')
        data = response.data
        self.assertEqual(200, response.status_code)
        self.assertEqual("user1_name2", data["name"])
        self.assertEqual("user1_surname2", data["surname"])

    def test_detail_contact_2(self):
        url = reverse('contact_detail', kwargs={'pk': 4})
        self.client.force_authenticate(user=self.user, token=self.token)
        response = self.client.get(url, format='json')
        self.assertEqual(404, response.status_code)

    def test_detail_contact_3(self):
        url = reverse('contact_detail', kwargs={'pk': 2})
        response = self.client.get(url, format='json')
        self.assertEqual(401, response.status_code)

    def test_del_contact_1(self):
        url = reverse('contact_delete', kwargs={'pk': 2})
        self.client.force_authenticate(user=self.user, token=self.token)
        response = self.client.delete(url, format='json')
        self.assertEqual(204, response.status_code)
        self.assertEqual(0, len(RecipientContact.objects.filter(id=2)))

    def test_del_contact_2(self):
        url = reverse('contact_delete', kwargs={'pk': 4})
        self.client.force_authenticate(user=self.user, token=self.token)
        response = self.client.delete(url, format='json')
        self.assertEqual(404, response.status_code)

    def test_del_contact_3(self):
        url = reverse('contact_delete', kwargs={'pk': 2})
        response = self.client.delete(url, format='json')
        self.assertEqual(401, response.status_code)
