from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase
from rest_framework.authtoken.models import Token
from ..models import User, ContactImportFiles
import os
import shutil


class ImportRunRequestDataValidateTest(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser', email='testuser@mail.com', password='password')
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
        # слишком большой id
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

    def test_import_run_validate_3(self):
        # OK
        url = reverse('import_run')
        self.client.force_authenticate(user=self.user, token=self.token)
        request_data = {
            "filename": "1.xlsx",
            "id": "",
            "name": "",
            "surname": "",
            "email": 4,
            "phone": "",
            "contact_group": "",
            "comment": "",
        }
        response = self.client.post(url, request_data)
        self.assertEqual(200, response.status_code)

    def test_import_run_validate_4(self):
        # OK
        url = reverse('import_run')
        self.client.force_authenticate(user=self.user, token=self.token)
        request_data = {
            "filename": "1.xlsx",
            "id": "",
            "name": "",
            "surname": "",
            "email": "",
            "phone": 2,
            "contact_group": "",
            "comment": "",
        }
        response = self.client.post(url, request_data)
        self.assertEqual(200, response.status_code)


class ImportFileUploadTest(APITestCase):

    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser', email='testuser@mail.com', password='password')
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
