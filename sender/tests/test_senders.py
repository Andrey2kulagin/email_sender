from rest_framework.test import APITestCase
from ..models import User, UserSendersContactStatistic, UserSenders, RecipientContact
from rest_framework.authtoken.models import Token
from django.urls import reverse
from django.utils import timezone


class ContactSenderStatisticTest(APITestCase):

    def setUp(self):
        self.user1 = User.objects.create_user(
            username='testuser1', email='testuser1@mail.com', password='password')
        self.user2 = User.objects.create_user(
            username='testuser2', email='testuser2@mail.com', password='password')
        self.token_1 = Token.objects.create(user=self.user1)
        self.token_1.save()
        self.token_2 = Token.objects.create(user=self.user2)
        self.token_2.save()
        self.first_user_sender1 = UserSenders.objects.create(user=self.user1, text="", type="WhatsApp",
                                                             count_letter=300, comment="qwer", title="title")
        self.first_user_sender2 = UserSenders.objects.create(user=self.user1, text="",
                                                             count_letter=300, comment="qwer", title="title")
        self.second_user_sender1 = UserSenders.objects.create(user=self.user2, text="",
                                                              count_letter=300, comment="qwer", title="title")
        self.second_user_sender2 = UserSenders.objects.create(user=self.user2, text="",
                                                              count_letter=300, comment="qwer", title="title")
        self.first_user_contact_1 = RecipientContact.objects.create(owner=self.user1, name="user1_name",
                                                                    surname="user1_surname", phone="89753412148",
                                                                    email="user1_contat_1@mail.com", comment="comment")
        self.first_user_contact_2 = RecipientContact.objects.create(owner=self.user1, name="user1_name",
                                                                    surname="user1_surname", phone="89753412147",
                                                                    email="user1_contact_2@mail.com", comment="comment")
        self.first_user_contact_3 = RecipientContact.objects.create(owner=self.user1, name="user1_name",
                                                                    surname="user1_surname", phone="89753412146",
                                                                    email="user1_contact_3@mail.com", comment="comment")
        self.second_user_contact_1 = RecipientContact.objects.create(owner=self.user2, name="user1_name",
                                                                     surname="user1_surname", phone="89753412145",
                                                                     email="user2_contact_1@mail.com",
                                                                     comment="comment")
        self.stat1_u1 = UserSendersContactStatistic.objects.create(user=self.user1, sender=self.first_user_sender1,
                                                                   contact=self.first_user_contact_1, is_send=False)
        self.stat2_u1 = UserSendersContactStatistic.objects.create(user=self.user1, sender=self.first_user_sender1,
                                                                   contact=self.first_user_contact_2, is_send=True)

    def test_1(self):
        sender = UserSenders.objects.get(id=1)
        sender.finish_date = timezone.now()
        sender.save()
        url = reverse('sender_get', kwargs={'pk': 1})
        self.client.force_authenticate(user=self.user1, token=self.token_1)
        response = self.client.get(url, format='json')
        res = response.data
        self.assertEqual(200, response.status_code)
        self.assertEqual(res['id'], sender.id)
        self.assertEqual(res["type"], "WhatsApp")
        self.assertEqual(res["title"], sender.title)
        self.assertEqual(len(res["start_date"]) > 0, True)
        self.assertEqual(len(res["finish_date"]) > 0, True)
        self.assertEqual(res["count_letter"], sender.count_letter)

    def test_2(self):
        sender = UserSenders.objects.get(id=1)
        sender.finish_date = timezone.now()
        sender.save()
        url = reverse('sender_list')
        self.client.force_authenticate(user=self.user1, token=self.token_1)
        response = self.client.get(url, format='json')
        res = response.data.get("results")
        self.assertEqual(200, response.status_code)
        self.assertEqual(res[0]['id'], sender.id)
        self.assertEqual(res[0]["type"], "WhatsApp")
        self.assertEqual(res[0]["title"], sender.title)
        self.assertEqual(len(res[0]["start_date"]) > 0, True)
        self.assertEqual(len(res[0]["finish_date"]) > 0, True)
        self.assertEqual(res[0]["count_letter"], sender.count_letter)



class ContactSenderTest(APITestCase):

    def setUp(self):
        self.user1 = User.objects.create_user(
            username='testuser1', email='testuser1@mail.com', password='password')
        self.user2 = User.objects.create_user(
            username='testuser2', email='testuser2@mail.com', password='password')
        self.token_1 = Token.objects.create(user=self.user1)
        self.token_1.save()
        self.token_2 = Token.objects.create(user=self.user2)
        self.token_2.save()
        self.first_user_sender1 = UserSenders.objects.create(user=self.user1, text="",
                                                             count_letter=300, comment="qwer", title="title",
                                                             is_account_validation_pass=False, )
        self.first_user_sender2 = UserSenders.objects.create(user=self.user1, text="",
                                                             count_letter=300, comment="qwer", title="title",
                                                             is_account_validation_pass=True,
                                                             is_error_with_accounts=True)
        self.first_user_sender3 = UserSenders.objects.create(user=self.user1, text="",
                                                             count_letter=300, comment="qwer", title="title",
                                                             is_account_validation_pass=True, )

        self.first_user_contact_1 = RecipientContact.objects.create(owner=self.user1, name="user1_name",
                                                                    surname="user1_surname", phone="89753412148",
                                                                    email="user1_contat_1@mail.com", comment="comment")
        self.first_user_contact_2 = RecipientContact.objects.create(owner=self.user1, name="user1_name",
                                                                    surname="user1_surname", phone="89753412147",
                                                                    email="user1_contact_2@mail.com", comment="comment")
        self.first_user_contact_3 = RecipientContact.objects.create(owner=self.user1, name="user1_name",
                                                                    surname="user1_surname", phone="89753412146",
                                                                    email="user1_contact_3@mail.com", comment="comment")
        self.second_user_contact_1 = RecipientContact.objects.create(owner=self.user2, name="user1_name",
                                                                     surname="user1_surname", phone="89753412145",
                                                                     email="user2_contact_1@mail.com",
                                                                     comment="comment")
        self.stat1_u1 = UserSendersContactStatistic.objects.create(user=self.user1, sender=self.first_user_sender1,
                                                                   contact=self.first_user_contact_1, is_send=False)
        self.stat2_u1 = UserSendersContactStatistic.objects.create(user=self.user1, sender=self.first_user_sender1,
                                                                   contact=self.first_user_contact_2, is_send=True)

    def test_validation_result_1(self):
        url = reverse('WA_sender_is_validation_passed', kwargs={'sender_id': 1})
        self.client.force_authenticate(user=self.user1, token=self.token_1)
        response = self.client.get(url, format='json')
        res = response.data
        self.assertEqual(200, response.status_code)
        self.assertEqual(res['status_code'], 422)

    def test_validation_result_2(self):
        url = reverse('WA_sender_is_validation_passed', kwargs={'sender_id': 2})
        self.client.force_authenticate(user=self.user1, token=self.token_1)
        response = self.client.get(url, format='json')
        res = response.data
        self.assertEqual(200, response.status_code)
        self.assertEqual(res['status_code'], 400)

    def test_validation_result_3(self):
        url = reverse('WA_sender_is_validation_passed', kwargs={'sender_id': 3})
        self.client.force_authenticate(user=self.user1, token=self.token_1)
        response = self.client.get(url, format='json')
        res = response.data
        self.assertEqual(200, response.status_code)
        self.assertEqual(res['status_code'], 200)

    def test_is_success_finished_1(self):
        url = reverse('WA_sender_is_success_finished', kwargs={'sender_id': 1})
        self.client.force_authenticate(user=self.user1, token=self.token_1)
        response = self.client.get(url, format='json')
        res = response.data
        self.assertEqual(200, response.status_code)
        self.assertEqual(res['status_code'], 400)

    def test_is_success_finished_2(self):
        url = reverse('WA_sender_is_success_finished', kwargs={'sender_id': 2})
        self.client.force_authenticate(user=self.user1, token=self.token_1)
        response = self.client.get(url, format='json')
        res = response.data
        self.assertEqual(200, response.status_code)
        self.assertEqual(res['status_code'], 400)

    def test_is_success_finished_3(self):
        sender = UserSenders.objects.get(id=3)
        sender.finish_date = timezone.now()
        sender.save()
        url = reverse('WA_sender_is_success_finished', kwargs={'sender_id': 3})
        self.client.force_authenticate(user=self.user1, token=self.token_1)
        response = self.client.get(url, format='json')
        res = response.data
        self.assertEqual(200, response.status_code)
        self.assertEqual(res['status_code'], 200)

    def test_statistic(self):
        url = reverse('sender_statistic', kwargs={'id': 1})
        self.client.force_authenticate(user=self.user1, token=self.token_1)
        response = self.client.get(url, format='json')
        res = response.data.get("results")
        self.assertEqual(200, response.status_code)
        self.assertEqual(res[0]["contact"], 1)
        self.assertEqual(res[0]["contact_str"], "user1_name - user1_surname - 89753412148 - user1_contat_1@mail.com")
        self.assertEqual(res[0]["is_send"], False)
        self.assertEqual(res[0]["comment"], None)
