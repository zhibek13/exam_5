from rest_framework.test import APITestCase

from .models import User, Author


class AuthorRegisterTestCase(APITestCase):
    def setUp(self) -> None:
        self.data = {
            "username": "test_user",
            "password": "qweasd!23",
            "password_2": "qweasd!23"
        }

    def test_register(self):
        response = self.client.post("/api/account/register/", self.data)
        self.assertEqual(response.status_code, 201)
        self.assertEqual(User.objects.count(), 1)
        self.assertEqual(Author.objects.count(), 1)
        self.assertEqual(User.objects.first().username, "test_user")
        self.assertEqual(Author.objects.first().user.username, "test_user")

    def test_obtain_token(self):
        self.client.post("/api/account/register/", self.data)
        response = self.client.post("/api/account/token/", self.data)
        self.assertEqual(response.status_code, 200)
        self.assertTrue("token" in response.data)
