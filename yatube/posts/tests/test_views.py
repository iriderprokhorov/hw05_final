import shutil
import tempfile

from django import forms
from django.conf import settings
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import Client, TestCase, override_settings
from django.urls import reverse
from posts.models import Comment, Group, Post, User

from . import constants

TEMP_MEDIA_ROOT = tempfile.mkdtemp(dir=settings.BASE_DIR)


@override_settings(MEDIA_ROOT=TEMP_MEDIA_ROOT)
class PostModelTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.posts_obj = []
        cls.user = User.objects.create_user(username="auth")
        cls.user2 = User.objects.create_user(username="auth2")
        cls.user3 = User.objects.create_user(username="auth3")
        # test-group1
        cls.group1 = Group.objects.create(
            title="test-group1",
            slug="test-slug1",
            description="test-description1",
        )
        # group-test2
        cls.group2 = Group.objects.create(
            title="test-group2",
            slug="test-slug2",
            description="test-description2",
        )

        # add 15 posts group1
        for i in range(1, 15):
            cls.posts_obj.append(
                Post(
                    author=cls.user,
                    text="test-text" + str(i),
                    group=cls.group1,
                )
            )
        # add 15 posts group2
        for i in range(15, 30):
            cls.posts_obj.append(
                Post(
                    author=cls.user,
                    text="test-text" + str(i),
                    group=cls.group2,
                )
            )
        # without group
        cls.posts_obj.append(
            Post(author=cls.user, text="test-text-without_group")
        )
        cls.posts = Post.objects.bulk_create(cls.posts_obj)

        # create comment in last post
        post_amount = Post.objects.all().count()
        cls.comment1 = Comment.objects.create(
            text="test-comment1",
            post=Post.objects.get(pk=post_amount),
            author=cls.user,
        )

    @classmethod
    def tearDownClass(cls):
        super().tearDownClass()
        # Модуль shutil - библиотека Python с удобными инструментами
        # для управления файлами и директориями:
        # создание, удаление, копирование, перемещение, изменение папок и файл
        # Метод shutil.rmtree удаляет директорию и всё её содержимое
        shutil.rmtree(TEMP_MEDIA_ROOT, ignore_errors=True)

    def setUp(self):
        # Create unauthorized_client
        self.guest_client = Client()
        # Create authorized_client
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)
        self.authorized_client2 = Client()
        self.authorized_client2.force_login(self.user2)
        self.authorized_client3 = Client()
        self.authorized_client3.force_login(self.user3)

    # Check using template
    def test_pages_uses_correct_template(self):
        """URL-адрес использует соответствующий шаблон."""
        templates_pages_names = {
            reverse("posts:index"): "posts/index.html",
            reverse(
                "posts:group_list", kwargs={"slug": "test-slug1"}
            ): "posts/group_list.html",
            reverse(
                "posts:profile", kwargs={"username": "auth"}
            ): "posts/profile.html",
            reverse(
                "posts:post_detail", kwargs={"post_id": "1"}
            ): "posts/post_detail.html",
            reverse(
                "posts:post_edit", kwargs={"pk": "1"}
            ): "posts/create_post.html",
            reverse("posts:post_create"): "posts/create_post.html",
        }
        for reverse_name, template in templates_pages_names.items():
            with self.subTest(reverse_name=reverse_name):
                response = self.authorized_client.get(reverse_name)
                self.assertTemplateUsed(response, template)

    # Check page context
    def test_home_page_show_correct_context(self):
        """Шаблон home сформирован с правильным контекстом."""
        response = self.guest_client.get(reverse("posts:index"))
        first_object = response.context["page_obj"][0]
        self.assertEqual(str(first_object.text), "test-text1")

    def test_group_list_page_show_correct_context(self):
        """Шаблон group_list сформирован с правильным контекстом."""
        response = self.guest_client.get(
            reverse("posts:group_list", kwargs={"slug": "test-slug1"})
        )
        first_object = response.context["page_obj"][0]
        self.assertEqual(str(first_object.text), "test-text1")
        self.assertEqual(str(first_object.group), "test-group1")

    def test_profile_page_show_correct_context(self):
        """Шаблон profile сформирован с правильным контекстом."""
        response = self.guest_client.get(
            reverse("posts:profile", kwargs={"username": "auth"})
        )
        first_object = response.context["page_obj"][0]
        self.assertEqual(str(first_object.text), "test-text1")
        self.assertEqual(str(first_object.author), "auth")
        self.assertEqual(str(first_object.group), "test-group1")

    def test_post_detail_page_show_correct_context(self):
        """Шаблон post_detail сформирован с правильным контекстом."""
        response = self.guest_client.get(
            reverse("posts:post_detail", kwargs={"post_id": "1"})
        )
        self.assertEqual(str(response.context["post"]), "test-text1")
        self.assertEqual(str(response.context["post"].pk), "1")

    def test_post_edit_show_correct_context(self):
        """Шаблон post_edit с правильным контекстом."""
        response = self.authorized_client.get(
            reverse("posts:post_edit", kwargs={"pk": "1"})
        )
        self.assertEqual(str(response.context["post"]), "test-text1")
        self.assertEqual(str(response.context["is_edit"]), "True")
        self.assertEqual(str(response.context["post"].pk), "1")
        form_fields = {
            # При создании формы поля модели типа TextField
            # преобразуются в CharField с виджетом forms.Textarea
            "text": forms.fields.CharField,
            "group": forms.fields.ChoiceField,
        }
        for value, expected in form_fields.items():
            with self.subTest(value=value):
                form_field = response.context["form"].fields[value]
                self.assertIsInstance(form_field, expected)

    def test_post_create_show_correct_context(self):
        """Шаблон post_create с правильным контекстом."""
        response = self.authorized_client.get(reverse("posts:post_create"))
        form_fields = {
            "text": forms.fields.CharField,
            "group": forms.fields.ChoiceField,
        }
        for value, expected in form_fields.items():
            with self.subTest(value=value):
                form_field = response.context["form"].fields[value]
                self.assertIsInstance(form_field, expected)

    # Check paginator
    def test_index_page_contains_31(self):
        """На страницу index выводится по 10 постов"""
        response = self.client.get(reverse("posts:index"))
        self.assertEqual(
            len(response.context["page_obj"]), settings.DEFAULT_POSTS_ON_PAGE
        )

    def test_group_list_page_contains_15(self):
        """На страницу group_list выводится 10 постов"""
        response = self.client.get(
            reverse("posts:group_list", kwargs={"slug": "test-slug1"})
        )
        self.assertEqual(
            len(response.context["page_obj"]), settings.DEFAULT_POSTS_ON_PAGE
        )

    def test_profile_page_contains_31(self):
        """На страницу profile выводится 10 постов"""
        response = self.guest_client.get(
            reverse("posts:profile", kwargs={"username": "auth"})
        )
        self.assertEqual(
            len(response.context["page_obj"]), settings.DEFAULT_POSTS_ON_PAGE
        )

    # Check post. is not other group
    def test_post_create_with_group_show_correct_context(self):
        """Создание поста с указанием группы."""
        response = self.guest_client.get(
            reverse("posts:group_list", kwargs={"slug": "test-slug2"})
        )
        for i in range(0, len(response.context["post_list"])):
            self.assertEqual(
                str(response.context["post_list"][i].group), "test-group2"
            )

    # check post with pic.uploaded can't many times.all test in one function
    def test_pages_show_correct_picture(self):
        """Шаблоны сформированы с правильным контекстом и картинкой."""
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
            "group": self.group2.pk,
            "image": uploaded,
        }

        # send POST with picture
        self.authorized_client.post(
            reverse("posts:post_create"), data=form_data, follow=True
        )
        # check last post on home page
        response = self.guest_client.get(reverse("posts:index"))
        post_count = Post.objects.all().count()
        first_object = response.context["post_list"][post_count - 1]
        self.assertEqual(first_object.image, "posts/small.gif")
        # check last post on group page test-group2
        response = self.guest_client.get(
            reverse("posts:group_list", kwargs={"slug": "test-slug2"})
        )
        post_count = Post.objects.filter(group=self.group2).count()
        first_object = response.context["post_list"][post_count - 1]
        self.assertEqual(first_object.image, "posts/small.gif")
        # check last posts on profile page
        response = self.guest_client.get(
            reverse("posts:profile", kwargs={"username": "auth"})
        )
        post_count = Post.objects.filter(author=self.user).count()
        first_object = response.context["post_list"][post_count - 1]
        self.assertEqual(first_object.image, "posts/small.gif")
        # check last post on post_detail page
        post_count = Post.objects.all().count()
        response = self.guest_client.get(
            reverse("posts:post_detail", kwargs={"post_id": post_count})
        )
        first_object = response.context["post"]
        self.assertEqual(first_object.image, "posts/small.gif")

    # Check context post with comment
    def test_post_detail_page_show_comment_context(self):
        """Шаблон home сформирован с правильным контекстом."""
        post_count = Post.objects.all().count()
        response = self.authorized_client.get(
            reverse("posts:post_detail", kwargs={"post_id": post_count})
        )
        first_object = response.context["comments"][0]
        self.assertEqual(first_object.text, "test-comment1")

    # test cache
    def test_cache_home_page(self):
        """Тестируем удаление одной записи и отображение кеша"""
        response_before_del = self.authorized_client.get(
            reverse("posts:index")
        )
        content_before_del = response_before_del.content
        Post.objects.get(pk=1).delete()
        response_after_del = self.authorized_client.get(reverse("posts:index"))
        content_after_del = response_after_del.content
        self.assertEqual(content_before_del, content_after_del)

    # test 404 custom page
    def test_castom_page_not_found(self):
        """Тестируем отображение кастомной страницы ошибки 404"""
        response = self.authorized_client.get(constants.UNEXISTING_PAGE)
        self.assertIn("Custom 404", response.content.decode())

    def test_follow_author(self):
        """Авторизованный пользователь может подписаться и отписаться"""
        # check that user have not follow
        response_before_follow = self.authorized_client2.get(
            reverse("posts:follow_index")
        )
        self.assertNotIn("test-text", response_before_follow.content.decode())
        self.authorized_client2.get(
            reverse("posts:profile_follow", kwargs={"username": self.user})
        )
        # check follow
        response_after_follow = self.authorized_client2.get(
            reverse("posts:follow_index")
        )
        self.assertIn("test-text", response_after_follow.content.decode())
        self.authorized_client2.get(
            reverse("posts:profile_unfollow", kwargs={"username": self.user})
        )
        # check unfollow
        response_after_unfollow = self.authorized_client2.get(
            reverse("posts:follow_index")
        )
        self.assertNotIn("test-text", response_after_unfollow.content.decode())

    def test_follow_page(self):
        """Новая запись пользователя появляется в ленте тех, кто на него
        подписан и не появляется в ленте тех, кто не подписан"""
        # check that user have not follow author
        response_before_follow = self.authorized_client.get(
            reverse("posts:follow_index")
        )
        self.assertNotIn("test-text", response_before_follow.content.decode())
        # check that user2 have not follow author
        response_before_follow2 = self.authorized_client2.get(
            reverse("posts:follow_index")
        )
        self.assertNotIn("test-text", response_before_follow2.content.decode())
        # auth follow the author auth3
        self.authorized_client.get(
            reverse("posts:profile_follow", kwargs={"username": self.user3})
        )
        # auth2 follow the author auth3
        self.authorized_client2.get(
            reverse("posts:profile_follow", kwargs={"username": self.user3})
        )
        # user3 created new post
        Post.objects.create(
            author=self.user3,
            text="test-text-follow-me",
            group=self.group1,
        )
        # check content index follow for auth2
        response_after_follow2 = self.authorized_client2.get(
            reverse("posts:follow_index")
        )
        self.assertIn(
            "test-text-follow-me", response_after_follow2.content.decode()
        )
        # check content index follow for auth3
        response_after_follow3 = self.authorized_client3.get(
            reverse("posts:follow_index")
        )
        self.assertNotIn("test-text", response_after_follow3.content.decode())
