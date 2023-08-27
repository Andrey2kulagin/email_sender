from django.core.files.uploadedfile import SimpleUploadedFile
from unittest import TestCase
from django.test import TestCase as DjTestKeys
from ...services.contact_import_service import get_start_data_from_imp, get_cure_filename, get_errors_headers, \
    get_error_row, import_contact_create_validate_error_check, import_contact_update_validate_errors_check
import os
import shutil
from ...models import RecipientContact, User, ContactGroup

current_path = os.path.abspath(__file__)


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
        self.first_user_group3 = ContactGroup.objects.create(user=self.user, title="Группа3 1 юзера")  # 3
        self.second_user_group1 = ContactGroup.objects.create(user=self.second_user, title="Группа1 2 юзера")  # 4
        self.second_user_group2 = ContactGroup.objects.create(user=self.second_user, title="Группа2 2 юзера")  # 5
        self.second_user_group3 = ContactGroup.objects.create(user=self.second_user, title="Группа3 2 юзера")  # 6
        # Создание писем
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

    def test_import_contact_create_validate_1(self):
        cure_values = {
            "id": None,
            "name": None,
            "surname": None,
            "email": None,
            "phone": "79853411006",
            "contact_group": "Группа1 1 юзера; Группа2 1 юзера; Группа3 1 юзера",
            "comment": None,
        }
        res = import_contact_create_validate_error_check(cure_values, self.user)
        self.assertEqual(res["status"], "OK")

    def test_import_contact_create_validate_2(self):
        # у пользователя нет такой группы
        cure_values = {
            "id": None,
            "name": None,
            "surname": None,
            "email": None,
            "phone": "79853411006",
            "contact_group": "Группа1 1 юзера; Группа2 1 юзера; Групп31314а3 1 юзера",
            "comment": None,
        }
        res = import_contact_create_validate_error_check(cure_values, self.user)

        self.assertEqual(res["status"], "PF")
        self.assertEqual(res["errors"], {'group : Групп31314а3 1 юзера': 'У вас нет группы: "Групп31314а3 1 юзера"'})

    def test_import_contact_create_validate_3(self):
        cure_values = {
            "id": None,
            "name": None,
            "surname": None,
            "email": None,
            "phone": "79812353411006",
            "contact_group": "Группа1 1 юзера; Группа2 1 юзера; Группа3 1 юзера",
            "comment": None,
        }
        res = import_contact_create_validate_error_check(cure_values, self.user)
        self.assertEqual(res["status"], "FF")
        self.assertEqual(res["errors"], {
            'phone': "[ErrorDetail(string='Неправильный номер телефона. Должно быть 11 цифр и начинаться должен с 8 или +7', code='invalid')]"})

    def test_import_contact_create_validate_4(self):
        cure_values = {
            "id": None,
            "name": None,
            "surname": None,
            "email": "qwr@yandex.ru",
            "phone": "79812353411006",
            "contact_group": "Группа1 1 юзера; Группа2 1 юзера; Группа3 1 юзера",
            "comment": None,
        }
        res = import_contact_create_validate_error_check(cure_values, self.user)
        self.assertEqual(res["status"], "PF")
        self.assertEqual(res["errors"], {
            'phone': "[ErrorDetail(string='Неправильный номер телефона. Должно быть 11 цифр и начинаться должен с 8 или +7', code='invalid')]"})

    def test_import_contact_create_validate_5(self):
        cure_values = {
            "id": None,
            "name": None,
            "surname": None,
            "email": "qwryandex.ru",
            "phone": "79812353411006",
            "contact_group": "Группа1 1 юзера; Группа2 1 юзера; Группа3 1 юзера",
            "comment": None,
        }
        res = import_contact_create_validate_error_check(cure_values, self.user)
        self.assertEqual(res["status"], "FF")

        self.assertEqual(res["errors"], {
            'phone': "[ErrorDetail(string='Неправильный номер телефона. Должно быть 11 цифр и начинаться должен с 8 или +7', code='invalid')]",
            'email': "[ErrorDetail(string='Введите правильный email', code='invalid')]"})

    def test_import_contact_update_validate_1(self):
        cure_values = {
            "id": "1",
            "name": None,
            "surname": None,
            "email": None,
            "phone": "79853411006",
            "contact_group": "Группа1 1 юзера; Группа2 1 юзера; Группа3 1 юзера",
            "comment": None,
        }
        res = import_contact_update_validate_errors_check(cure_values, '1', self.user)
        self.assertEqual(res["status"], "OK")

    def test_import_contact_update_validate_2(self):
        cure_values = {
            "id": "1",
            "name": None,
            "surname": None,
            "email": None,
            "phone": "79853411006",
            "contact_group": "Группа1 1 юзера; Группа2 1 юзера; Групп31314а3 1 юзера",
            "comment": None,
        }
        res = import_contact_update_validate_errors_check(cure_values, '1', self.user)
        self.assertEqual(res["status"], "PF")
        self.assertEqual(res["errors"],
                         {'group : Групп31314а3 1 юзера': 'У вас нет группы: "Групп31314а3 1 юзера"'})

    def test_import_contact_update_validate_3(self):
        cure_values = {
            "id": "1",
            "name": None,
            "surname": None,
            "email": None,
            "phone": "79812353411006",
            "contact_group": "Группа1 1 юзера; Группа2 1 юзера; Группа3 1 юзера",
            "comment": None,
        }
        res = import_contact_update_validate_errors_check(cure_values, '1', self.user)
        self.assertEqual(res["status"], "PF")
        self.assertEqual(res["errors"], {
            'phone': "[ErrorDetail(string='Неправильный номер телефона. Должно быть 11 цифр и начинаться должен с 8 или +7', code='invalid')]"})

    def test_import_contact_update_validate_4(self):
        cure_values = {
            "id": "1",
            "name": None,
            "surname": None,
            "email": "qwr@yandex.ru",
            "phone": "79812353411006",
            "contact_group": "Группа1 1 юзера; Группа2 1 юзера; Группа3 1 юзера",
            "comment": None,
        }
        res = import_contact_update_validate_errors_check(cure_values, '1', self.user)
        self.assertEqual(res["status"], "PF")
        self.assertEqual(res["errors"], {
            'phone': "[ErrorDetail(string='Неправильный номер телефона. Должно быть 11 цифр и начинаться должен с 8 или +7', code='invalid')]"})

    def test_import_contact_update_validate_5(self):
        cure_values = {
            "id": None,
            "name": None,
            "surname": None,
            "email": "qwryandex.ru",
            "phone": "79812353411006",
            "contact_group": "Группа1 1 юзера; Группа2 1 юзера; Группа3 1 юзера",
            "comment": None,
        }
        res = import_contact_update_validate_errors_check(cure_values, '1', self.user)
        self.assertEqual(res["status"], "PF")
        self.assertEqual(res["errors"], {
            'phone': "[ErrorDetail(string='Неправильный номер телефона. Должно быть 11 цифр и начинаться должен с 8 или +7', code='invalid')]",
            'email': "[ErrorDetail(string='Введите правильный email', code='invalid')]"})

    def test_import_contact_update_validate_6(self):
        cure_values = {
            "id": None,
            "name": None,
            "surname": None,
            "email": "qwryandex.ru",
            "phone": "79812353411006",
            "contact_group": None,
            "comment": None,
        }
        res = import_contact_update_validate_errors_check(cure_values, '1', self.user)
        self.assertEqual(res["status"], "PF")
        self.assertEqual(res["errors"], {
            'phone': "[ErrorDetail(string='Неправильный номер телефона. Должно быть 11 цифр и начинаться должен с 8 или +7', code='invalid')]",
            'email': "[ErrorDetail(string='Введите правильный email', code='invalid')]"})

    def test_import_contact_update_validate_7(self):
        cure_values = {
            "id": "92",
            "name": None,
            "surname": None,
            "email": None,
            "phone": "79853411006",
            "contact_group": "Группа1 1 юзера; Группа2 1 юзера; Группа3 1 юзера",
            "comment": None,
        }
        res = import_contact_update_validate_errors_check(cure_values, '92', self.user)
        self.assertEqual(res["status"], "FF")


class TestErrorsCase(TestCase):

    def test_get_errors_header_1(self):
        mask = {
            "id": 0,
            "name": None,
            "surname": None,
            "email": 3,
            "phone": 1,
            "contact_group": 4,
            "comment": None,
        }
        result = get_errors_headers(mask)
        self.assertEqual('Критическая ошибка(создать не удалось)', result[0])
        self.assertEqual('Некритическая ошибка (удалось создать частично)', result[1])
        self.assertEqual("id", result[2])
        self.assertEqual("phone", result[3])
        self.assertEqual("", result[4])
        self.assertEqual("email", result[5])
        self.assertEqual("contact_group", result[6])

    def test_get_errors_row_1(self):
        errors = {'group : невалидная': 'У вас нет группы: "невалидная"'}
        row = (2, None, None, 'Группа1 1 юзера; Группа2 1 юзера; невалидная', None, None, None, None, None,
               'одна невалидная группа, статус PF')
        comment = None
        contact_id = "2"
        id_index = 0
        status = "PF"
        result = get_error_row(errors, row, comment, contact_id, id_index, status)
        self.assertEqual(result[0], "")
        self.assertEqual(result[1].strip().replace("\n", ""),
                         'errors:1. У вас нет группы: "невалидная"')
        self.assertEqual(result[2], 2)
        self.assertEqual(result[3], None)
        self.assertEqual(result[4], None)
        self.assertEqual(result[5], 'Группа1 1 юзера; Группа2 1 юзера; невалидная')

    def test_get_errors_row_2(self):
        errors = {'group : невалидная': 'У вас нет группы: "невалидная"'}
        row = (2, None, None, 'Группа1 1 юзера; Группа2 1 юзера; невалидная', None, None, None, None, None,
               'одна невалидная группа, статус PF')
        comment = None
        contact_id = "2"
        id_index = None
        status = "PF"
        result = get_error_row(errors, row, comment, contact_id, id_index, status)
        self.assertEqual(result[0], "")
        self.assertEqual(result[1].strip().replace("\n", ""),
                         'errors:1. У вас нет группы: "невалидная"')
        self.assertEqual(result[2], "2")
        self.assertEqual(result[3], 2)
        self.assertEqual(result[4], None)
        self.assertEqual(result[5], None)
        self.assertEqual(result[6], 'Группа1 1 юзера; Группа2 1 юзера; невалидная')

    def test_get_errors_row_3(self):
        errors = {
            'phone': "[ErrorDetail(string='Неправильный номер телефона. Должно быть 11 цифр и начинаться должен с 8 или +7', code='invalid')]"}
        row = (
            None, 283873287, None, 'Группа1 1 юзера; Группа2 1 юзера;', None, None, None, None, None,
            'невалидный номер')
        comment = "Добавьте хотя бы 1 валидный контакт"
        contact_id = None
        id_index = 0
        status = "FF"
        result = get_error_row(errors, row, comment, contact_id, id_index, status)

        self.assertEqual(result[0].strip().replace("\n", ""),
                         'Добавьте хотя бы 1 валидный контактerrors:1. [ErrorDetail(string=\'Неправильный номер телефона. Должно быть 11 цифр и начинаться должен с 8 или +7\', code=\'invalid\')]')
        self.assertEqual(result[1], "")
        self.assertEqual(result[2], "")
        self.assertEqual(result[3], 283873287)
        self.assertEqual(result[4], None)
        self.assertEqual(result[5], 'Группа1 1 юзера; Группа2 1 юзера;')

    class GetStartDataTestCase(TestCase):
        def test_get_start_data_from_imp_1(self):
            relative_path = os.path.join(os.path.dirname(current_path), 'contact_import_test_file/1.xlsx')
            # Создание фиктивного файла
            with open(relative_path, 'rb') as file:
                uploaded_file = SimpleUploadedFile(relative_path, file.read(),
                                                   content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
            # Вызов функции с фиктивным файлом
            result_func = get_start_data_from_imp(uploaded_file)
            result = result_func["results"]

            # Проверка ожидаемого результата
            self.assertEqual(result_func["count_elements_in_line"], 20)
            self.assertEqual(result_func["count"], 2)
            self.assertEqual(len(result), 2)
            self.assertEqual(len(result[0]), 20)
            self.assertEqual(result[0][5], "1")
            self.assertEqual(len(result[1]), 20)
            self.assertEqual(result[1][1], "value 1")
            self.assertEqual(result[1][2], "Значение 2")

        def test_get_start_data_from_imp_2(self):
            relative_path = os.path.join(os.path.dirname(current_path), 'contact_import_test_file/2.xlsx')
            # Создание фиктивного файла
            with open(relative_path, 'rb') as file:
                uploaded_file = SimpleUploadedFile(relative_path, file.read(),
                                                   content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
            # Вызов функции с фиктивным файлом
            result_func = get_start_data_from_imp(uploaded_file)
            result = result_func["results"]
            # Проверка ожидаемого результата
            self.assertEqual(result_func["count_elements_in_line"], 12)
            self.assertEqual(result_func["count"], 10)
            self.assertEqual(len(result), 10)
            self.assertEqual(len(result[0]), 12)
            self.assertEqual(result[0][5], "1")
            self.assertEqual(len(result[1]), 12)
            self.assertEqual(result[1][1], "value 1")
            self.assertEqual(result[1][3], "Значение 2")


class GetFilenameTestCase(TestCase):
    def test_get_filename_1(self):
        os.mkdir("test")
        cure_filenames = ["test.xlsx", "test(1).xlsx", "test ( 1 ).xlsx", "test(23).xlsx"]
        for filename in cure_filenames:
            f = open(f"test/{filename}", 'w')
            f.close()
        result = get_cure_filename("test", "test.xlsx")
        self.assertEqual("test(2).xlsx", result)
        result = get_cure_filename("test", "test ( 1 ).xlsx")
        self.assertEqual("test ( 1 )(1).xlsx", result)
        result = get_cure_filename("test", "test(23).xlsx")
        self.assertEqual("test(24).xlsx", result)
        shutil.rmtree("test")
