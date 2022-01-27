from django.test import TestCase

from ..models import Group, Post, User, Comment, Follow


class PostModelTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username="auth")
        cls.group = Group.objects.create(
            title="Тестовая группа",
            slug="Тестовый слаг",
            description="Тестовое описание",
        )
        cls.post = Post.objects.create(
            author=cls.user,
            text="Тестовая группа",
        )

    def test_post_models_have_correct_object_names(self):
        """Проверяем, что у post модели корректно работает __str__."""
        post = PostModelTest.post
        expected_object_name = post.text
        self.assertEqual(expected_object_name, str(post))

    def test_group_models_have_correct_object_names(self):
        """Проверяем, что у group модели корректно работает __str__."""
        group = PostModelTest.group
        expected_object_name = group.title
        self.assertEqual(expected_object_name, str(group))


class CommentModelTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username="auth2")
        cls.group = Group.objects.create(
            title="Тестовая группа2",
            slug="Тестовый слаг2",
            description="Тестовое описание2",
        )
        cls.post = Post.objects.create(
            author=cls.user,
            text="Тестовая группа2",
        )

        cls.comment = Comment.objects.create(
            author=cls.user,
            post=cls.post,
            text="test-comment",
        )

    def test_comment_models_have_correct_text(self):
        """Проверяем, что у group модели корректно работает __str__."""
        comment = CommentModelTest.comment
        expected_object_name = comment.text
        self.assertEqual(expected_object_name, str(comment))


class FollowModelTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username="auth3")
        cls.user2 = User.objects.create_user(username="auth4")
        cls.group = Group.objects.create(
            title="Тестовая группа3",
            slug="Тестовый слаг3",
            description="Тестовое описание3",
        )
        cls.post = Post.objects.create(
            author=cls.user,
            text="Тестовая группа3",
        )
        cls.follow = Follow.objects.create(user=cls.user2, author=cls.user)

    def test_verbose_name(self):
        """verbose_name в полях совпадает с ожидаемым."""
        follow = FollowModelTest.follow
        field_verboses = {
            "user": "кто подписывается",
            "author": "на кого подписываютс",
        }
        for value, expected in field_verboses.items():
            with self.subTest(value=value):
                self.assertEqual(
                    follow._meta.get_field(value).verbose_name, expected
                )
