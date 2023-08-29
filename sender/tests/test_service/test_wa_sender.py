from django.test import TestCase as DjTestKeys
from ...models import User, ContactGroup, RecipientContact, UserLetterText


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
        self.first_user_contact_2.contact_group.add(self.first_user_group3)

        self.first_user_contact_3 = RecipientContact.objects.create(owner=self.user, name="user1_name",  # 3
                                                                    surname="user1_surname", phone="89753412148",
                                                                    email="user1@mail.com", comment="comment")
        self.first_user_contact_3.contact_group.add(self.first_user_group2)
        self.first_user_contact_3.contact_group.add(self.first_user_group3)

        self.second_user_contact_1 = RecipientContact.objects.create(owner=self.second_user, name="user1_name",  # 4
                                                                     surname="user1_surname", phone="89753412148",
                                                                     email="user1@mail.com", comment="comment")
