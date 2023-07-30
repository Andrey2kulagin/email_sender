from rest_framework.test import APITestCase
from ..models import User, ContactGroup
from rest_framework.authtoken.models import Token
from django.urls import reverse


class ContactGroupRestTest(APITestCase):

    def setUp(self):
        self.user1 = User.objects.create_user(
            username='testuser1', email='testuser1@mail.com', password='password')
        self.user2 = User.objects.create_user(
            username='testuser2', email='testuser2@mail.com', password='password')
        self.token_1 = Token.objects.create(user=self.user1)
        self.token_1.save()
        self.token_2 = Token.objects.create(user=self.user2)
        self.token_2.save()


        # first user groups
        self.user_1_group_1 = ContactGroup.objects.create(user=self.user1, title="user_1_group_1")
        self.user_1_group_2 = ContactGroup.objects.create(user=self.user1, title="user_1_group_2")
        self.user_2_group_1 = ContactGroup.objects.create(user=self.user2, title="user_2_group_1")

    def test_contact_group_get_1(self):
        url = reverse('contact_group_get', kwargs={'pk': 1})
        self.client.force_authenticate(user=self.user1, token=self.token_1)
        response = self.client.get(url, format='json')
        data = response.data
        self.assertEqual(200, response.status_code)
        self.assertEqual(self.user_1_group_1.id, data["id"])
        self.assertEqual(self.user_1_group_1.title, data["title"])

    def test_contact_group_get_2(self):
        url = reverse('contact_group_get', kwargs={'pk': 3})
        self.client.force_authenticate(user=self.user1, token=self.token_1)
        response = self.client.get(url, format='json')
        self.assertEqual(404, response.status_code)

    def test_contact_group_list_1(self):
        url = reverse('contact_group_list')
        self.client.force_authenticate(user=self.user1, token=self.token_1)
        response = self.client.get(url,{"page": 1, "page_size": 1}, format='json')
        data = response.data["results"]
        self.assertEqual(200, response.status_code)
        self.assertEqual(self.user_1_group_1.id, data[0]["id"])
        self.assertEqual(self.user_1_group_1.title, data[0]["title"])

    def test_contact_group_create_1(self):
        url = reverse('contact_group_create')
        self.client.force_authenticate(user=self.user1, token=self.token_1)
        request_data = {
            "title": "user_1_group_3",
        }
        response = self.client.post(url,  data=request_data, format='json')
        data = response.data
        self.assertEqual(201, response.status_code)
        self.assertEqual(4, data["id"])
        self.assertEqual(ContactGroup.objects.get(id=4).title, data["title"])

    def test_contact_group_update_1(self):
        url = reverse('contact_group_update', kwargs={'pk': 1})
        self.client.force_authenticate(user=self.user1, token=self.token_1)
        request_data = {
            "title": "user_1_group_1_new_title",
        }
        response = self.client.patch(url,  data=request_data, format='json')
        data = response.data
        self.assertEqual(200, response.status_code)
        self.assertEqual(ContactGroup.objects.get(id=1).title, request_data["title"])
        self.assertEqual(request_data["title"], data["title"])

    def test_contact_group_replace_1(self):
        url = reverse('contact_group_replace', kwargs={'pk': 1})
        self.client.force_authenticate(user=self.user1, token=self.token_1)
        response = self.client.put(url, format='json')
        self.assertEqual(405, response.status_code)

    def test_contact_group_delete_1(self):
        url = reverse('contact_group_delete', kwargs={'pk': 1})
        self.client.force_authenticate(user=self.user1, token=self.token_1)
        response = self.client.delete(url, format='json')
        self.assertEqual(204, response.status_code)
        self.assertEqual(0, len(ContactGroup.objects.filter(id=1)))



