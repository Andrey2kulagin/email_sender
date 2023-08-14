from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase
from rest_framework.authtoken.models import Token
from ..models import User, ContactImportFiles, RecipientContact, ContactGroup
import os
import shutil
from ..services.all_service import check_or_create_folder


class ImportRunTest(APITestCase):
    def setUp(self):
        # создаем пользователей
        self.user = User.objects.create_user(
            username='testuser', email='testuser@mail.com', password='password')
        self.token = Token.objects.create(user=self.user)
        self.token.save()

        self.second_user = User.objects.create_user(
            username='seconduser', email='testur@mail.com', password='password')
        self.second_token = Token.objects.create(user=self.second_user)
        self.second_token.save()
        # создаем импорты
        self.user_1_file1 = ContactImportFiles.objects.create(owner=self.user, filename="1.xlsx", row_len=5,
                                                              is_contains_headers=True)
        self.user_1_file2 = ContactImportFiles.objects.create(owner=self.user, filename="11.xlsx", row_len=12)
        self.user_1_file3 = ContactImportFiles.objects.create(owner=self.user, filename="2.xlsx", row_len=12,
                                                              is_contains_headers=True)

        # копируем тестовые файлы в рабочую папку
        # check_or_create_folder(f"sources/import_file/{self.user.username}")
        source_folder = 'sender/tests/contact_import_tests_files/'
        # Путь к папке, в которую копируем файлы
        target_folder = f"sources/import_file/{self.user.username}"
        # Копирование файлов
        shutil.copytree(source_folder, target_folder)
        # создание групп пользователей
        self.first_user_group1 = ContactGroup.objects.create(user=self.user, title="Группа1 1 юзера")  # 1
        self.first_user_group2 = ContactGroup.objects.create(user=self.user, title="Группа2 1 юзера")  # 2
        self.first_user_group3 = ContactGroup.objects.create(user=self.user, title="Группа3 1 юзера")  # 3
        self.second_user_group1 = ContactGroup.objects.create(user=self.second_user, title="Группа1 2 юзера")  # 4
        self.second_user_group2 = ContactGroup.objects.create(user=self.second_user, title="Группа2 2 юзера")  # 5
        self.second_user_group3 = ContactGroup.objects.create(user=self.second_user, title="Группа3 2 юзера")  # 6
        # создание контактов
        self.first_user_contact_1 = RecipientContact.objects.create(owner=self.user, name="user1_name",  # 1
                                                                    surname="user1_surname", phone="89753412148",
                                                                    email="user1@mail.com", comment="comment")
        self.first_user_contact_1.contact_group.add(self.first_user_group1)
        self.first_user_contact_1.contact_group.add(self.first_user_group2)
        self.first_user_contact_2 = RecipientContact.objects.create(owner=self.user, name="user2_name",  # 2
                                                                    surname="user2_surname", phone="89753412148",
                                                                    email="user2@mail.com", comment="comment")
        self.first_user_contact_2.contact_group.add(self.first_user_group2)
        self.first_user_contact_2.contact_group.add(self.first_user_group3)

        self.first_user_contact_3 = RecipientContact.objects.create(owner=self.user, name="user3_name",  # 3
                                                                    surname="user3_surname", phone="89753412148",
                                                                    email="user3@mail.com", comment="comment")
        self.first_user_contact_3.contact_group.add(self.first_user_group2)
        self.first_user_contact_3.contact_group.add(self.first_user_group3)

        self.second_user_contact_1 = RecipientContact.objects.create(owner=self.second_user, name="user1_1_name",  # 4
                                                                     surname="user1_1_surname", phone="89753412148",
                                                                     email="user1_1@mail.com", comment="comment")

    @classmethod
    def tearDownClass(self):
        # Путь к папке, где хранятся созданные файлы
        folder_path = f"sources/import_file/testuser"
        if os.path.exists(folder_path):
            # Удаление папки
            shutil.rmtree(folder_path)

    def test_import_run_1(self):
        url = reverse('import_run')
        # Всего 6 контактов, обновление у 2(1 норм, у второго невалидная группа), загрузка 1 все ок, 1 невалидная группа, 2 невалидные контакты
        self.client.force_authenticate(user=self.user, token=self.token)
        request_data = {
            "filename": "1.xlsx",
            "id": 0,
            "name": "",
            "surname": "",
            "email": 2,
            "phone": 1,
            "contact_group": 3,
            "comment": "",
        }
        response = self.client.post(url, request_data)
        response_data = response.data
        self.assertEqual(200, response.status_code)
        # общие параметры
        self.assertEqual(6, response_data["all_handled_lines"])
        self.assertEqual(2, response_data["success_create_update_count"])
        self.assertEqual(2, response_data["partial_success_create_update_count"])
        self.assertEqual(2, response_data["fail_count"])

        # 1 строка - добавление группы контакту с id = 1, который принадлежит 1 юзеру Всё должно быть ОК
        contact_1_obj = RecipientContact.objects.get(id=1)  # целевой юзер
        right_user_group = [self.first_user_group1, self.first_user_group2, self.first_user_group3]  # Целевые группы
        cure_user_groups = contact_1_obj.contact_group.all()  # фактические группы юзера
        for el in right_user_group:
            self.assertEqual(True, el in cure_user_groups)
        self.assertEqual(len(right_user_group), len(cure_user_groups))

        # 2 строка - Добавление контакту с id = 2, который принадлежит 1 юзеру. Группы, которой не существует. Статус PF
        contact_2_obj = RecipientContact.objects.get(id=2)  # целевой юзер
        right_user_group = [self.first_user_group1, self.first_user_group2, self.first_user_group3]  # Целевые группы
        cure_user_groups = contact_2_obj.contact_group.all()  # фактические группы юзера
        for el in right_user_group:
            self.assertEqual(True, el in cure_user_groups)
        self.assertEqual(len(right_user_group), len(cure_user_groups))

        # 3 строка - Создание юзера - Всё ок
        contact_4_obj = RecipientContact.objects.get(id=5)  # юзер
        right_user_group = [self.first_user_group1, self.first_user_group2]  # Целевые группы
        right_phone = "79853411006"
        right_email = "validmail@yandex.ru"
        cure_user_groups = contact_4_obj.contact_group.all()  # фактические группы юзера
        for el in right_user_group:
            self.assertEqual(True, el in cure_user_groups)
        self.assertEqual(len(right_user_group), len(cure_user_groups))
        self.assertEqual(right_phone, contact_4_obj.phone)
        self.assertEqual(right_email, contact_4_obj.email)

        # 4 строка - Создание юзера - Всё ок
        contact_4_obj = RecipientContact.objects.get(id=6)  # юзер
        right_user_group = [self.first_user_group1, self.first_user_group2]  # Целевые группы
        right_phone = "79853411007"
        right_email = None
        cure_user_groups = contact_4_obj.contact_group.all()  # фактические группы юзера
        for el in right_user_group:
            self.assertEqual(True, el in cure_user_groups)
        self.assertEqual(len(right_user_group), len(cure_user_groups))
        self.assertEqual(right_phone, contact_4_obj.phone)
        self.assertEqual(right_email, contact_4_obj.email)

        self.assertEqual(len(RecipientContact.objects.all()), 6)

        # файл с ошибками


class ImportRestTest(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser1', email='testuser@mail.com', password='password')
        self.token = Token.objects.create(user=self.user)
        self.token.save()
        self.user2 = User.objects.create_user(
            username='testuser2', email='testuser2@mail.com', password='password')
        self.token = Token.objects.create(user=self.user2)
        self.token.save()
        self.user_1_file1 = ContactImportFiles.objects.create(owner=self.user, filename="1.xlsx", row_len=5)
        self.user_1_file2 = ContactImportFiles.objects.create(owner=self.user, filename="11.xlsx", row_len=12)
        self.user_1_file3 = ContactImportFiles.objects.create(owner=self.user2, filename="12.xlsx", row_len=12)

    def test_get_1(self):
        url = reverse('import_get', kwargs={'pk': 1})
        # не хватает контактов
        self.client.force_authenticate(user=self.user, token=self.token)
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        resp_data = response.data
        self.assertEqual(resp_data["filename"], "1.xlsx")

    def test_get_2(self):
        url = reverse('import_get', kwargs={'pk': 1})
        # не хватает контактов
        response = self.client.get(url)
        self.assertEqual(response.status_code, 401)

    def test_get_3(self):
        url = reverse('import_get', kwargs={'pk': 15})
        # не хватает контактов
        self.client.force_authenticate(user=self.user, token=self.token)
        response = self.client.get(url)
        self.assertEqual(response.status_code, 404)

    def test_get_4(self):
        url = reverse('import_get', kwargs={'pk': 3})
        # не хватает контактов
        self.client.force_authenticate(user=self.user, token=self.token)
        response = self.client.get(url)
        self.assertEqual(response.status_code, 404)

    def test_list_1(self):
        url = reverse('import_list')
        # не хватает контактов
        self.client.force_authenticate(user=self.user, token=self.token)
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        resp_data = response.data
        self.assertEqual(resp_data["results"][0]["filename"], "1.xlsx")


class ImportRunRequestDataValidateTest(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser1', email='testuser@mail.com', password='password')
        self.token = Token.objects.create(user=self.user)
        self.token.save()
        self.user2 = User.objects.create_user(
            username='testuser2', email='testuser2@mail.com', password='password')
        self.token = Token.objects.create(user=self.user2)
        self.token.save()
        self.user_1_file1 = ContactImportFiles.objects.create(owner=self.user, filename="1.xlsx", row_len=5)
        self.user_1_file2 = ContactImportFiles.objects.create(owner=self.user, filename="11.xlsx", row_len=12)

    def test_import_run_validate_1(self):
        url = reverse('import_run')
        # не хватает контактов
        self.client.force_authenticate(user=self.user, token=self.token)
        request_data = {
            "filename": "1.xlsx",
            "id": "",
            "name": "",
            "surname": "",
            "email": "",
            "phone": "",
            "contact_group": "",
            "comment": "",
        }
        response = self.client.post(url, request_data)
        self.assertEqual(400, response.status_code)

    def test_import_run_validate_2(self):
        # слишком большой индекс id
        url = reverse('import_run')
        self.client.force_authenticate(user=self.user, token=self.token)
        request_data = {
            "filename": "1.xlsx",
            "id": "12",
            "name": "",
            "surname": "",
            "email": 4,
            "phone": "",
            "contact_group": "",
            "comment": "",
        }
        response = self.client.post(url, request_data)
        self.assertEqual(400, response.status_code)


class ImportFileUploadTest(APITestCase):

    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser1', email='testuser@mail.com', password='password')
        self.token = Token.objects.create(user=self.user)
        self.token.save()

    def test_1(self):
        url = reverse('import_file_upload')
        self.client.force_authenticate(user=self.user, token=self.token)
        response = self.client.post(url,
                                    {'file': open("sender/tests/test_service/contact_import_test_file/1.xlsx", 'rb')})
        data = response.data
        result = data["results"]
        self.assertEqual(200, response.status_code)
        self.assertEqual(True, os.path.exists(f"sources/import_file/{self.user.username}"))
        self.assertEqual(True, os.path.exists(f"sources/import_file/{self.user.username}/1.xlsx"))
        shutil.rmtree(f"sources/import_file/{self.user.username}")
        self.assertEqual("1.xlsx", data.get("file_name_on_serv"))
        self.assertEqual(data["count_elements_in_line"], 20)
        self.assertEqual(data["count"], 2)
        self.assertEqual(len(result), 2)
        self.assertEqual(len(result[0]), 20)
        self.assertEqual(result[0][5], "1")
        self.assertEqual(len(result[1]), 20)
        self.assertEqual(result[1][1], "value 1")
        self.assertEqual(result[1][2], "Значение 2")
        contact_objs = ContactImportFiles.objects.filter(owner=self.user, filename="1.xlsx")
        self.assertEqual(1, len(contact_objs))
        self.assertEqual(contact_objs[0].filename, "1.xlsx")
        self.assertEqual(contact_objs[0].row_len, 20)
        self.assertEqual(contact_objs[0].is_contains_headers, False)

    def test_2(self):
        url = reverse('import_file_upload')
        os.mkdir(f"sources/import_file/{self.user.username}")
        f = open(f"sources/import_file/{self.user.username}/1.xlsx", "w")
        f.close()
        self.client.force_authenticate(user=self.user, token=self.token)
        response = self.client.post(url,
                                    {'file': open("sender/tests/test_service/contact_import_test_file/1.xlsx", 'rb')})
        data = response.data
        self.assertEqual(200, response.status_code)
        self.assertEqual(True, os.path.exists(f"sources/import_file/{self.user.username}"))
        self.assertEqual(True, os.path.exists(f"sources/import_file/{self.user.username}/11.xlsx"))
        self.assertEqual("11.xlsx", data.get("file_name_on_serv"))
        shutil.rmtree(f"sources/import_file/{self.user.username}")
        self.assertEqual(1, len(ContactImportFiles.objects.filter(owner=self.user, filename="11.xlsx")))

    def test_3(self):
        url = reverse('import_file_upload')
        self.client.force_authenticate(user=self.user, token=self.token)
        response = self.client.post(url,
                                    {'file': open("sender/tests/test_service/contact_import_test_file/3.xlsx", 'rb'),
                                     'is_contains_headers': True}
                                    )
        data = response.data
        result = data["results"]
        self.assertEqual(200, response.status_code)
        self.assertEqual(True, os.path.exists(f"sources/import_file/{self.user.username}"))
        self.assertEqual(True, os.path.exists(f"sources/import_file/{self.user.username}/3.xlsx"))
        shutil.rmtree(f"sources/import_file/{self.user.username}")
        self.assertEqual("3.xlsx", data.get("file_name_on_serv"))
        self.assertEqual(data["count_elements_in_line"], 20)
        self.assertEqual(data["count"], 3)
        self.assertEqual(len(result), 3)

        self.assertEqual(len(result[1]), 20)
        self.assertEqual(len(result[0]), 20)
        self.assertEqual(result[0][5], "Поле 6")
        self.assertEqual(result[1][5], "1")
        self.assertEqual(len(result[2]), 20)
        self.assertEqual(result[2][1], "value 1")
        self.assertEqual(result[2][2], "Значение 2")
        contact_objs = ContactImportFiles.objects.filter(owner=self.user, filename="3.xlsx")
        self.assertEqual(1, len(contact_objs))
        self.assertEqual(contact_objs[0].filename, "3.xlsx")
        self.assertEqual(contact_objs[0].row_len, 20)
        self.assertEqual(contact_objs[0].is_contains_headers, True)
