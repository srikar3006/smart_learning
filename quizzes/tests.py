from django.test import TestCase
from django.urls import reverse

from accounts.models import User
from rhymes.models import Category, Rhyme
from .models import Choice, Question, Quiz


class QuizFlowTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username="quizlearner",
            password="StrongPass123!",
            account_type="learner",
        )
        category = Category.objects.create(name="Numbers", icon_emoji="🔢")
        rhyme = Rhyme.objects.create(
            title="Counting Rhyme",
            slug="counting-rhyme",
            category=category,
            lyrics="One two three",
        )
        self.quiz = Quiz.objects.create(rhyme=rhyme, title="Counting Quiz")
        question = Question.objects.create(quiz=self.quiz, text="What comes after one?", order=1)
        self.correct = Choice.objects.create(question=question, text="Two", is_correct=True, order=1)
        Choice.objects.create(question=question, text="Five", is_correct=False, order=2)

    def test_answer_api_grades_answer(self):
        self.client.force_login(self.user)
        self.client.get(reverse("quizzes:start", args=[self.quiz.rhyme.slug]))
        response = self.client.post(
            reverse("quizzes:api_submit_answer", args=[self.quiz.rhyme.slug]),
            data={"question_id": self.quiz.questions.first().id, "choice_id": self.correct.id},
            content_type="application/json",
        )
        self.assertEqual(response.status_code, 200)
        self.assertTrue(response.json()["correct"])
