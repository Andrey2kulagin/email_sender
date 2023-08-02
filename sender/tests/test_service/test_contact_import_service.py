from django.core.files.uploadedfile import SimpleUploadedFile
from unittest import TestCase
from ...services.contact_import_service import get_start_data_from_imp, get_cure_filename
import os
import shutil
current_path = os.path.abspath(__file__)




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
        cure_filenames = ["test.xlsx", "test1.xlsx"]
        for filename in cure_filenames:
            f = open(f"test/{filename}", 'w')
            f.close()
        result = get_cure_filename("test", "test.xlsx")
        shutil.rmtree("test")
        self.assertEqual("test12.xlsx", result)
