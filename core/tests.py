from django.test import TestCase
from django.urls import reverse

from accounts.models import User


class ParentDashboardTests(TestCase):
    def test_parent_can_view_dashboard(self):
        parent = User.objects.create_user(
            username="parent",
            password="StrongPass123!",
            account_type="parent",
            is_child_learner=False,
        )
        self.client.force_login(parent)
        response = self.client.get(reverse("parent:dashboard"))
        self.assertEqual(response.status_code, 200)

    def test_learner_is_redirected_from_parent_dashboard(self):
        learner = User.objects.create_user(
            username="learner",
            password="StrongPass123!",
            account_type="learner",
        )
        self.client.force_login(learner)
        response = self.client.get(reverse("parent:dashboard"))
        self.assertEqual(response.status_code, 302)
