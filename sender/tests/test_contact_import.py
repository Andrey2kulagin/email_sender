from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase
from rest_framework.authtoken.models import Token
from ..models import User, ContactImportFiles
import os
import shutil


class RecipientContactUpdateTest(APITestCase):

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
        self.assertEqual(True, os.path.exists(f"import_file/{self.user.username}"))
        self.assertEqual(True, os.path.exists(f"import_file/{self.user.username}/1.xlsx"))
        shutil.rmtree(f"import_file/{self.user.username}")
        self.assertEqual("1.xlsx", data.get("file_name_on_serv"))
        self.assertEqual(data["count_elements_in_line"], 20)
        self.assertEqual(data["count"], 2)
        self.assertEqual(len(result), 2)
        self.assertEqual(len(result[0]), 20)
        self.assertEqual(result[0][5], "1")
        self.assertEqual(len(result[1]), 20)
        self.assertEqual(result[1][1], "value 1")
        self.assertEqual(result[1][2], "Значение 2")
        self.assertEqual(1, len(ContactImportFiles.objects.filter(owner=self.user, filename="1.xlsx")))

    def test_2(self):
        url = reverse('import_file_upload')
        os.mkdir(f"import_file/{self.user.username}")
        f = open(f"import_file/{self.user.username}/1.xlsx", "w")
        f.close()
        self.client.force_authenticate(user=self.user, token=self.token)
        response = self.client.post(url,
                                    {'file': open("sender/tests/test_service/contact_import_test_file/1.xlsx", 'rb')})
        data = response.data
        self.assertEqual(200, response.status_code)
        self.assertEqual(True, os.path.exists(f"import_file/{self.user.username}"))
        self.assertEqual(True, os.path.exists(f"import_file/{self.user.username}/11.xlsx"))
        self.assertEqual("11.xlsx", data.get("file_name_on_serv"))
        shutil.rmtree(f"import_file/{self.user.username}")
        self.assertEqual(1, len(ContactImportFiles.objects.filter(owner=self.user, filename="11.xlsx")))
