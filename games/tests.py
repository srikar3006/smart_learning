from django.test import TestCase
from django.urls import reverse


class GamesPageTests(TestCase):
    def test_games_page_requires_login(self):
        response = self.client.get(reverse("games:list"))
        self.assertEqual(response.status_code, 302)

    def test_games_page_loads_for_authenticated_user(self):
        from accounts.models import User
        user = User.objects.create_user(username="game_test", password="TestPass123!")
        self.client.force_login(user)
        response = self.client.get(reverse("games:list"))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Let's Play & Learn!")
        self.assertContains(response, "Coloring Fun")
        self.assertContains(response, "Maze Adventure")
