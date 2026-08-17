from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("quizzes", "0001_initial"),
    ]

    operations = [
        migrations.AddConstraint(
            model_name="question",
            constraint=models.UniqueConstraint(fields=("quiz", "order"), name="unique_quiz_question_order"),
        ),
        migrations.AddConstraint(
            model_name="choice",
            constraint=models.UniqueConstraint(fields=("question", "order"), name="unique_question_choice_order"),
        ),
        migrations.AddConstraint(
            model_name="quizanswer",
            constraint=models.UniqueConstraint(fields=("attempt", "question"), name="unique_attempt_question_answer"),
        ),
        migrations.AddIndex(
            model_name="quizattempt",
            index=models.Index(fields=["user", "completed_at"], name="quizzes_attempt_user_comp_idx"),
        ),
        migrations.AddIndex(
            model_name="quizattempt",
            index=models.Index(fields=["quiz", "completed_at"], name="quizzes_attempt_quiz_comp_idx"),
        ),
    ]
