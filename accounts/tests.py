from django.test import TestCase

from .forms import LearnerRegistrationForm, ParentRegistrationForm
from .models import User


class AccountFlowTests(TestCase):
    def test_learner_registration_creates_learner(self):
        form = LearnerRegistrationForm(
            data={
                "username": "littlelearner",
                "first_name": "Mia",
                "email": "mia@example.com",
                "avatar": "cat",
                "age_group": "4-6",
                "parent_email": "",
                "password1": "StrongPass123!",
                "password2": "StrongPass123!",
            }
        )
        self.assertTrue(form.is_valid(), form.errors)
        user = form.save()
        self.assertTrue(user.is_learner)
        self.assertTrue(user.check_password("StrongPass123!"))

    def test_parent_registration_creates_parent(self):
        form = ParentRegistrationForm(
            data={
                "username": "parentone",
                "first_name": "Parent",
                "email": "parent@example.com",
                "password1": "StrongPass123!",
                "password2": "StrongPass123!",
            }
        )
        self.assertTrue(form.is_valid(), form.errors)
        user = form.save()
        self.assertTrue(user.is_parent)
        self.assertFalse(user.is_child_learner)
