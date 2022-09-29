from rest_framework.test import APITestCase
from rest_framework.authtoken.models import Token

from account.models import Author, User
from .models import News, Status, Comment, NewsStatus, CommentStatus


class TestNews(APITestCase):
    def register_get_token(self, username):
        data = {
            "username": username,
            "password": "qweasd!23",
            "password_2": "qweasd!23"
        }
        try:
            Author.objects.get(user__username=username)
        except Author.DoesNotExist:
            self.client.post("/api/account/register/", data)
        finally:
            response = self.client.post("/api/account/token/", data)
            return response.data["token"]

    def test_news_without_auth(self):
        data = {
            "title": "test",
            "content": "test",
        }
        response = self.client.post("/api/news/", data)
        self.assertIn(response.status_code, [401, 403])

        response = self.client.get("/api/news/")
        self.assertEqual(response.status_code, 200)

    def test_news_with_auth(self):
        token = self.register_get_token("test_user")
        self.client.credentials(HTTP_AUTHORIZATION="Token " + token)

        data = {
            "title": "test title",
            "content": "test content",
        }
        response = self.client.post("/api/news/", data)
        self.assertEqual(response.status_code, 201)

        response = self.client.get("/api/news/")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(News.objects.count(), 1)
        self.assertEqual(News.objects.first().title, "test title")
        self.assertEqual(News.objects.first().content, "test content")
        self.assertEqual(News.objects.first().author.user.username, "test_user")

        response = self.client.get("/api/news/1/")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data["title"], "test title")
        self.assertEqual(response.data["content"], "test content")
        self.assertEqual(response.data["author"], Token.objects.get(user__username="test_user").user.author.id)

        data["title"] = "test title changed"
        response = self.client.put("/api/news/1/", data)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data["title"], "test title changed")
        self.assertEqual(response.data["content"], "test content")
        self.assertEqual(response.data["author"], Token.objects.get(user__username="test_user").user.author.id)

        token = self.register_get_token("test_user_another")
        self.client.credentials(HTTP_AUTHORIZATION="Token " + token)
        response = self.client.put("/api/news/1/", data)
        self.assertEqual(response.status_code, 403)

        User.objects.create_user(username="test_user_2", password="qweasd!23")
        token = self.register_get_token("test_user_2")
        self.client.credentials(HTTP_AUTHORIZATION="Token " + token)
        with self.assertRaises(Author.DoesNotExist):
            self.client.post("/api/news/", data)

    def test_comments_without_auth(self):
        news = News.objects.create(title="test", content="test", author=Author.objects.create(
            user=User.objects.create_user(username="test_user", password="qweasd!23")))
        data = {
            "text": "test",
        }
        response = self.client.post(f"/api/news/{news.id}/comments/", data)
        self.assertIn(response.status_code, [401, 403])

        response = self.client.get(f"/api/news/{news.id}/comments/")
        self.assertEqual(response.status_code, 200)

    def test_comments_with_auth(self):
        token = self.register_get_token("test_user")
        self.client.credentials(HTTP_AUTHORIZATION="Token " + token)
        news = News.objects.create(title="test", content="test", author=Author.objects.get(
            user=User.objects.get(username="test_user")))
        data = {
            "text": "test",
        }
        response = self.client.post(f"/api/news/{news.id}/comments/", data)
        self.assertEqual(response.status_code, 201)

        response = self.client.get(f"/api/news/{news.id}/comments/")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(Comment.objects.count(), 1)
        self.assertEqual(Comment.objects.first().text, "test")
        self.assertEqual(Comment.objects.first().author.user.username, "test_user")

        data["text"] = "test changed"
        response = self.client.put(f"/api/news/{news.id}/comments/1/", data)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data["text"], "test changed")
        self.assertEqual(response.data["author"], Token.objects.get(user__username="test_user").user.author.id)

        token = self.register_get_token("test_user_another")
        self.client.credentials(HTTP_AUTHORIZATION="Token " + token)
        response = self.client.put(f"/api/news/{news.id}/comments/1/", data)
        self.assertEqual(response.status_code, 403)

        User.objects.create_user(username="test_user_2", password="qweasd!23")
        token = self.register_get_token("test_user_2")
        self.client.credentials(HTTP_AUTHORIZATION="Token " + token)
        with self.assertRaises(Author.DoesNotExist):
            self.client.post(f"/api/news/{news.id}/comments/", data)

    def test_statuses_no_auth(self):
        response = self.client.get("/api/statuses/")
        self.assertIn(response.status_code, [401, 403])

    def test_statuses_author_auth(self):
        token = self.register_get_token("test_user")
        self.client.credentials(HTTP_AUTHORIZATION="Token " + token)
        response = self.client.get("/api/statuses/")
        self.assertEqual(response.status_code, 403)
        data = {
            "slug": "test",
            "name": "Test",
        }
        response = self.client.post("/api/statuses/", data)
        self.assertEqual(response.status_code, 403)

    def test_statuses_admin_auth(self):
        reg_data = dict(username="test_admin", password="qweasd!23")
        user = User.objects.create_superuser(**reg_data)
        token = self.register_get_token(user.username)
        self.client.credentials(HTTP_AUTHORIZATION="Token " + token)
        response = self.client.get("/api/statuses/")
        self.assertEqual(response.status_code, 200)
        data = {
            "slug": "test",
            "name": "Test",
        }
        response = self.client.post("/api/statuses/", data)
        self.assertEqual(response.status_code, 201)
        data["slug"] = "test_changed"
        response = self.client.put("/api/statuses/1/", data)
        self.assertEqual(response.status_code, 200)

    def test_news_status(self):
        status_like = Status.objects.create(slug="like", name="Like")
        status_dislike = Status.objects.create(slug="dislike", name="Dislike")
        post_author_token = self.register_get_token("test_user")
        status_author_token = self.register_get_token("test_user_2")
        self.client.credentials(HTTP_AUTHORIZATION="Token " + post_author_token)
        news = News.objects.create(title="test", content="test", author=Author.objects.get(
            user=User.objects.get(username="test_user")))
        data = {
            "title": "test title",
            "content": "test content",
        }
        response = self.client.post("/api/news/", data)
        self.client.credentials(HTTP_AUTHORIZATION="Token " + status_author_token)
        response = self.client.get(f"/api/news/{news.id}/like/")
        self.assertIn(response.status_code, [200, 201])
        self.assertEqual(NewsStatus.objects.count(), 1)
        self.assertEqual(NewsStatus.objects.first().status, status_like)
        self.assertEqual(NewsStatus.objects.first().news, news)
        self.assertEqual(NewsStatus.objects.first().author.user.username, "test_user_2")

        self.client.credentials(HTTP_AUTHORIZATION="Token " + post_author_token)
        response = self.client.get(f"/api/news/{news.id}/dislike/")
        self.assertIn(response.status_code, [200, 201])
        self.assertEqual(NewsStatus.objects.count(), 2)
        self.assertEqual(NewsStatus.objects.last().status, status_dislike)
        self.assertEqual(NewsStatus.objects.last().news, news)
        self.assertEqual(NewsStatus.objects.last().author.user.username, "test_user")

        response = self.client.get(f"/api/news/{news.id}/")
        self.assertEqual(response.data["get_status"]["Like"], 1)
        self.assertEqual(response.data["get_status"]["Dislike"], 1)
