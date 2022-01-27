from django.test import TestCase, Client
from django.urls import reverse


class StaticURLTests(TestCase):
    def setUp(self):
        # Create unauthorized_client
        self.guest_client = Client()

    # Check page author
    def test_author_page_show_correct_context(self):
        """Шаблон author сформирован с правильным контекстом."""
        response = self.guest_client.get(reverse("about:author"))
        context = response.content.decode()
        self.assertIn("Тут я размещу информацию", context)

    # Check page tech
    def test_tech_page_show_correct_context(self):
        """Шаблон tech сформирован с правильным контекстом."""
        response = self.guest_client.get(reverse("about:tech"))
        context = response.content.decode()
        self.assertIn("Вот что я умею", context)
