from django.test import TestCase
from ..service import phone_normalize, is_valid_phone_number


class ServiceTestCase(TestCase):
    def test_phone_normalize_1(self):
        result = phone_normalize("8 916 412 28-60")
        self.assertEqual("79164122860", result)

    def test_phone_normalize_2(self):
        result = phone_normalize("8 (916) 412 28-60")
        self.assertEqual("79164122860", result)

    def test_phone_normalize_3(self):
        result = phone_normalize("8 916 412-28-60")
        self.assertEqual("79164122860", result)

    def test_phone_normalize_4(self):
        result = phone_normalize("8(916)4122860")
        self.assertEqual("79164122860", result)

    def test_phone_normalize_5(self):
        result = phone_normalize("+79164122860")
        self.assertEqual("79164122860", result)

    def test_phone_normalize_6(self):
        result = phone_normalize("+7 (916) 412-28-60")
        self.assertEqual("79164122860", result)

    def test_phone_normalize_7(self):
        result = phone_normalize("+9 (916) 412-28-60")
        self.assertEqual("+99164122860", result)

    # тестирование валидации

    def test_is_valid_phone_number_1(self):
        result = is_valid_phone_number("+7 (916) 412-28-60")
        self.assertEqual(True, result)

    def test_is_valid_phone_number_2(self):
        result = is_valid_phone_number("+7 (91) 412-28-60")
        self.assertEqual(False, result)

    def test_is_valid_phone_number_3(self):
        result = is_valid_phone_number("+8 (916) 412-28-60")
        self.assertEqual(False, result)

    def test_is_valid_phone_number_4(self):
        result = is_valid_phone_number("89164712860")
        self.assertEqual(True, result)

    def test_is_valid_phone_number_5(self):
        result = is_valid_phone_number("+79164112860")
        self.assertEqual(True, result)

    def test_is_valid_phone_number_6(self):
        result = is_valid_phone_number("79164112860")
        self.assertEqual(True, result)
