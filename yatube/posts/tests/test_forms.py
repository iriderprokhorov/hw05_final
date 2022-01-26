import shutil
import tempfile

from django.conf import settings
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import Client, TestCase, override_settings
from django.urls import reverse
from posts.forms import PostForm
from posts.models import Group, Post, User, Comment


TEMP_MEDIA_ROOT = tempfile.mkdtemp(dir=settings.BASE_DIR)


@override_settings(MEDIA_ROOT=TEMP_MEDIA_ROOT)
class PostFormTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username="auth")
        cls.group = Group.objects.create(
            title="test-group",
            slug="test-slug",
            description="test-descriptipon",
        )
        cls.post = Post.objects.create(
            author=cls.user,
            text="test-post",
            group=cls.group,
        )
        cls.form = PostForm()

    @classmethod
    def tearDownClass(cls):
        super().tearDownClass()
        # Модуль shutil - библиотека Python с удобными инструментами
        # для управления файлами и директориями:
        # создание, удаление, копирование, перемещение, изменение папок и файл
        # Метод shutil.rmtree удаляет директорию и всё её содержимое
        shutil.rmtree(TEMP_MEDIA_ROOT, ignore_errors=True)

    def setUp(self):
        self.guest_client = Client()
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)

    def test_create_post(self):
        """Валидная форма создает запись в Post"""
        # Calculate post amount before add test post
        posts_count = Post.objects.count()
        form_data = {"text": "test-post-create", "group": self.group.pk}
        # Send POST request
        response = self.authorized_client.post(
            reverse("posts:post_create"), data=form_data, follow=True
        )
        # Check redirect
        self.assertRedirects(
            response, reverse("posts:profile", kwargs={"username": "auth"})
        )
        # Calculate post amount after added test post
        self.assertEqual(Post.objects.count(), posts_count + 1)
        # Check save post to database
        self.assertTrue(
            Post.objects.filter(
                text="test-post-create", group=self.group
            ).exists()
        )

    def test_post_edit(self):
        """Валидная форма редактирует запись в Post"""
        form_data = {
            "text": "test-post-edit",
            "group": self.group.pk,
        }
        # Send POST request
        response = self.authorized_client.post(
            reverse("posts:post_edit", kwargs={"pk": self.post.pk}),
            data=form_data,
            follow=True,
            is_edit=True,
        )
        # Check redirect
        self.assertRedirects(
            response,
            reverse("posts:post_detail", kwargs={"post_id": self.post.pk}),
        )
        # Check that post updated
        self.assertTrue(
            Post.objects.filter(
                text="test-post-edit", id="1", group=self.group
            ).exists()
        )

    def test_create_post_with_picture(self):
        """Валидная форма создает пост с картинкой"""
        # Подсчитаем количество записей в Task
        tasks_count = Post.objects.count()
        # Для тестирования загрузки изображений
        # берём байт-последовательность картинки,
        # состоящей из двух пикселей: белого и чёрного
        small_gif = (
            b"\x47\x49\x46\x38\x39\x61\x02\x00"
            b"\x01\x00\x80\x00\x00\x00\x00\x00"
            b"\xFF\xFF\xFF\x21\xF9\x04\x00\x00"
            b"\x00\x00\x00\x2C\x00\x00\x00\x00"
            b"\x02\x00\x01\x00\x00\x02\x02\x0C"
            b"\x0A\x00\x3B"
        )
        uploaded = SimpleUploadedFile(
            name="small.gif", content=small_gif, content_type="image/gif"
        )
        form_data = {
            "text": "test-post-create-with-picture",
            "group": self.group.pk,
            "image": uploaded,
        }
        # Отправляем POST-запрос
        self.authorized_client.post(
            reverse("posts:post_create"), data=form_data, follow=True
        )

        self.assertEqual(Post.objects.count(), tasks_count + 1, "Not created")
        # Проверяем, что создалась запись с нашей картинкой
        self.assertTrue(
            Post.objects.filter(
                image="posts/small.gif",
            ).exists()
        )

    def test_add_comments(self):
        """Авторизованный юзер создает комментарий к посту"""
        posts_count = Comment.objects.all().count()
        form_data = {"text": "test-comment-create"}
        # Send POST request from unauthorized user
        self.guest_client.post(
            reverse("posts:add_comment", kwargs={"post_id": self.post.pk}),
            data=form_data,
            follow=True,
        )
        # Calculate post amount after added test comment
        # from unauthorized user
        self.assertEqual(Comment.objects.count(), posts_count, "created")
        # Send POST request from authorized user
        self.authorized_client.post(
            reverse("posts:add_comment", kwargs={"post_id": self.post.pk}),
            data=form_data,
            follow=True,
        )
        # Calculate post amount after added test comment
        # from unauthorized user
        self.assertEqual(
            Comment.objects.count(), posts_count + 1, "no created"
        )
        # Check save post to database
        self.assertTrue(
            Comment.objects.filter(text="test-comment-create").exists()
        )
