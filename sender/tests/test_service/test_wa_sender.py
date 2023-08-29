from django.test import TestCase as DjTestKeys
from ...models import User, ContactGroup, RecipientContact, UserLetterText, SenderPhoneNumber
from ...services.WA_sender_service import wa_sender_run_validate
from rest_framework import serializers


class TestContactValidate(DjTestKeys):
    def setUp(self) -> None:
        # надо создать пользователя, несколько групп и контактов
        # создаем пользователей
        self.user = User.objects.create_user(
            username='testuser', email='testuser@mail.com', password='password')

        self.second_user = User.objects.create_user(
            username='seconduser', email='testur@mail.com', password='password')

        # создание групп пользователей
        self.first_user_group1 = ContactGroup.objects.create(user=self.user, title="Группа1 1 юзера")  # 1
        self.first_user_group2 = ContactGroup.objects.create(user=self.user, title="Группа2 1 юзера")  # 2
        self.second_user_group1 = ContactGroup.objects.create(user=self.second_user, title="Группа1 2 юзера")  # 4
        self.second_user_group2 = ContactGroup.objects.create(user=self.second_user, title="Группа2 2 юзера")  # 5
        # создание писем
        self.user1_letter_text = UserLetterText.objects.create(user=self.user, title="title1",
                                                               letter_subject="letter_subject1", text="textlkajd")
        self.user2_letter_text = UserLetterText.objects.create(user=self.second_user, title="title1",
                                                               letter_subject="letter_subject1", text="textlkajd")
        # создание контактов
        self.first_user_contact_1 = RecipientContact.objects.create(owner=self.user, name="user1_name",  # 1
                                                                    surname="user1_surname", phone="89753412148",
                                                                    email="user1@mail.com", comment="comment")
        self.first_user_contact_1.contact_group.add(self.first_user_group1)
        self.first_user_contact_1.contact_group.add(self.first_user_group2)
        self.first_user_contact_2 = RecipientContact.objects.create(owner=self.user, name="user1_name",  # 2
                                                                    surname="user1_surname", phone="89753412148",
                                                                    email="user1@mail.com", comment="comment")
        self.first_user_contact_2.contact_group.add(self.first_user_group2)

        self.first_user_contact_3 = RecipientContact.objects.create(owner=self.user, name="user1_name",  # 3
                                                                    surname="user1_surname", phone="89753412148",
                                                                    email="user1@mail.com", comment="comment")
        self.first_user_contact_3.contact_group.add(self.first_user_group2)

        self.second_user_contact_1 = RecipientContact.objects.create(owner=self.second_user, name="user1_name",  # 4
                                                                     surname="user1_surname", phone="89753412148",
                                                                     email="user1@mail.com", comment="comment")
        # создание аккаунтов для рассылки
        self.user_1_account_1 = SenderPhoneNumber.objects.create(owner=self.user, title="user_1_account_1",
                                                                 contact="89745431211", is_login=True)  # 1
        self.user_1_account_2 = SenderPhoneNumber.objects.create(owner=self.user, title="user_1_account_2",
                                                                 contact="89745431211", is_login=True)  # 2
        self.user_1_account_3 = SenderPhoneNumber.objects.create(owner=self.user, title="user_1_account_3",
                                                                 contact="89745431211", is_login=False)  # 3
        self.user_2_account_1 = SenderPhoneNumber.objects.create(owner=self.second_user, title="user_2_account_1",
                                                                 contact="89745431211", is_login=True)  # 4
        self.user_2_account_2 = SenderPhoneNumber.objects.create(owner=self.second_user, title="user_2_account_2",
                                                                 contact="89745431211", is_login=True)  # 5
        self.user_2_account_3 = SenderPhoneNumber.objects.create(owner=self.second_user, title="user_2_account_3",
                                                                 contact="89745431211", is_login=False)  # 6

    def test_wa_run_validate_1(self):
        #  все ок
        user = self.user
        data = {
            "text": "text_from_letter",
            "title": "title",
            "send_accounts": ["1-12", "2-17"],
            "contacts_group": [1, 2],
            "contacts": [2, 3]
        }
        try:
            wa_sender_run_validate(data, user)
            self.assertEqual(1, 1)
        except serializers.ValidationError:
            self.assertEqual(1, 2)

    def test_wa_run_validate_2(self):
        #  все нет текста
        user = self.user
        data = {
            "title": "title",
            "send_accounts": ["1-12", "2-17"],
            "contacts_group": [1, 2],
            "contacts": [2, 3]
        }
        try:
            wa_sender_run_validate(data, user)
            self.assertEqual(1, 2)
            # self.assertEqual(1, 1)
        except serializers.ValidationError:
            # self.assertEqual(1, 2)
            self.assertEqual(1, 1)

    def test_wa_run_validate_3(self):
        #  все ok
        user = self.user
        data = {
            "text_id": 1,
            "title": "title",
            "send_accounts": ["1-12", "2-17"],
            "contacts_group": [1, 2],
            "contacts": [2, 3]
        }
        try:
            wa_sender_run_validate(data, user)
            # self.assertEqual(1, 2)
            self.assertEqual(1, 1)
        except serializers.ValidationError:
            self.assertEqual(1, 2)
            # self.assertEqual(1, 1)

    def test_wa_run_validate_4(self):
        #  текст не этого юзера
        user = self.user
        data = {
            "text_id": 2,
            "title": "title",
            "send_accounts": ["1-12", "2-17"],
            "contacts_group": [1, 2],
            "contacts": [2, 3]
        }
        try:
            wa_sender_run_validate(data, user)
            self.assertEqual(1, 2)
            # self.assertEqual(1, 1)
        except serializers.ValidationError:
            # self.assertEqual(1, 2)
            self.assertEqual(1, 1)

    def test_wa_run_validate_5(self):
        #  не его аккаунт для рассылки
        user = self.user
        data = {
            "text_id": 1,
            "title": "title",
            "send_accounts": ["1-12", "4-17"],
            "contacts_group": [1, 2],
            "contacts": [2, 3]
        }
        try:
            wa_sender_run_validate(data, user)
            self.assertEqual(1, 2)
            # self.assertEqual(1, 1)
        except serializers.ValidationError:
            # self.assertEqual(1, 2)
            self.assertEqual(1, 1)

    def test_wa_run_validate_6(self):
        # аккаунт для рассылки с буквами
        user = self.user
        data = {
            "text_id": 1,
            "title": "title",
            "send_accounts": ["1-12", "2выф-17"],
            "contacts_group": [1, 2],
            "contacts": [2, 3]
        }
        try:
            wa_sender_run_validate(data, user)
            self.assertEqual(1, 2)
            # self.assertEqual(1, 1)
        except serializers.ValidationError:
            # self.assertEqual(1, 2)
            self.assertEqual(1, 1)

    def test_wa_run_validate_7(self):
        # аккаунт для рассылки с буквами
        user = self.user
        data = {
            "text_id": 1,
            "title": "title",
            "send_accounts": ["1-12", "2-вф17"],
            "contacts_group": [1, 2],
            "contacts": [2, 3]
        }
        try:
            wa_sender_run_validate(data, user)
            self.assertEqual(1, 2)
            # self.assertEqual(1, 1)
        except serializers.ValidationError:
            # self.assertEqual(1, 2)
            self.assertEqual(1, 1)

    def test_wa_run_validate_8(self):
        # аккаунт для рассылки не авторизован
        user = self.user
        data = {
            "text_id": 1,
            "title": "title",
            "send_accounts": ["1-12", "3-17"],
            "contacts_group": [1, 2],
            "contacts": [2, 3]
        }
        try:
            wa_sender_run_validate(data, user)
            self.assertEqual(1, 2)
            # self.assertEqual(1, 1)
        except serializers.ValidationError:
            # self.assertEqual(1, 2)
            self.assertEqual(1, 1)

    def test_wa_run_validate_9(self):
        # Группа, которой нет
        user = self.user
        data = {
            "text_id": 1,
            "title": "title",
            "send_accounts": ["1-12", "3-17"],
            "contacts_group": [1, 2, 98],
            "contacts": [2, 3]
        }
        try:
            wa_sender_run_validate(data, user)
            self.assertEqual(1, 2)
            # self.assertEqual(1, 1)
        except serializers.ValidationError:
            # self.assertEqual(1, 2)
            self.assertEqual(1, 1)

    def test_wa_run_validate_10(self):
        # Юзер, которого нет
        user = self.user
        data = {
            "text_id": 1,
            "title": "title",
            "send_accounts": ["1-12", "3-17"],
            "contacts_group": [1, 2],
            "contacts": [2, 3, 98]
        }
        try:
            wa_sender_run_validate(data, user)
            self.assertEqual(1, 2)
            # self.assertEqual(1, 1)
        except serializers.ValidationError:
            # self.assertEqual(1, 2)
            self.assertEqual(1, 1)

    def test_wa_run_validate_11(self):
        # Нет контактов для рассылки
        user = self.user
        data = {
            "text_id": 1,
            "title": "title",
            "send_accounts": ["1-12", "3-17"],
        }
        try:
            wa_sender_run_validate(data, user)
            self.assertEqual(1, 2)
            # self.assertEqual(1, 1)
        except serializers.ValidationError:
            # self.assertEqual(1, 2)
            self.assertEqual(1, 1)
