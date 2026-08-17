from django.test import TestCase
from django.urls import reverse

from accounts.models import User
from .models import Category, Rhyme


class RhymeFlowTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username="learner",
            password="StrongPass123!",
            first_name="Learner",
            account_type="learner",
        )
        self.category = Category.objects.create(name="Animals", icon_emoji="🐾")
        self.rhyme = Rhyme.objects.create(
            title="Baa Baa Black Sheep",
            slug="baa-baa-black-sheep",
            category=self.category,
            lyrics="Baa baa black sheep",
        )

    def test_rhyme_list_requires_login(self):
        response = self.client.get(reverse("rhymes:list"))
        self.assertEqual(response.status_code, 302)

    def test_mark_complete(self):
        self.client.force_login(self.user)
        response = self.client.post(reverse("rhymes:api_mark_complete", args=[self.rhyme.slug]))
        self.assertEqual(response.status_code, 200)
        self.assertTrue(response.json()["completed"])
