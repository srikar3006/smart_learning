from django.core.management.base import BaseCommand
from django.utils.text import slugify

from progress.models import Badge
from quizzes.models import Choice, Question, Quiz
from rhymes.models import Category, Rhyme


RHYME_DATA = [
    {
        "category": ("Animals", "🐾"),
        "title": "Baa Baa Black Sheep",
        "description": "A cheerful sheep shares wool with everyone in the village.",
        "difficulty": "easy",
        "lyrics": "Baa, baa, black sheep,\nHave you any wool?\nYes sir, yes sir,\nThree bags full.\nOne for the master,\nOne for the dame,\nAnd one for the little boy\nWho lives down the lane.",
        "questions": [
            ("What animal is in this rhyme?", [("🐑", "Sheep", True), ("🐶", "Dog", False), ("🐱", "Cat", False)]),
            ("How many bags of wool does the sheep have?", [("", "1", False), ("", "2", False), ("", "3", True)]),
        ],
    },
    {
        "category": ("Night Sky", "🌙"),
        "title": "Twinkle Twinkle Little Star",
        "description": "A gentle lullaby about a shining star in the night sky.",
        "difficulty": "easy",
        "lyrics": "Twinkle, twinkle, little star,\nHow I wonder what you are.\nUp above the world so high,\nLike a diamond in the sky.\nTwinkle, twinkle, little star,\nHow I wonder what you are.",
        "questions": [
            ("What is twinkling in the sky?", [("⭐", "Star", True), ("🌙", "Moon", False), ("☁️", "Cloud", False)]),
            ("The star is compared to what?", [("💎", "Diamond", True), ("🍬", "Candy", False), ("🚗", "Car", False)]),
        ],
    },
    {
        "category": ("Numbers", "🔢"),
        "title": "1, 2, Buckle My Shoe",
        "description": "A playful counting rhyme from one all the way to ten.",
        "difficulty": "medium",
        "lyrics": "One, two, buckle my shoe;\nThree, four, knock at the door;\nFive, six, pick up sticks;\nSeven, eight, lay them straight;\nNine, ten, a big fat hen.",
        "questions": [
            ("What do you knock at, at three and four?", [("🚪", "The door", True), ("🪟", "The window", False), ("🌳", "The tree", False)]),
            ("What is nine and ten?", [("🐔", "A big fat hen", True), ("🐷", "A pig", False), ("🐮", "A cow", False)]),
        ],
    },
    {
        "category": ("Alphabets", "🔤"),
        "title": "ABC Song",
        "description": "The classic alphabet song set to a fun sing-along tune.",
        "difficulty": "easy",
        "lyrics": "A B C D E F G,\nH I J K L M N O P,\nQ R S, T U V,\nW X, Y and Z.\nNow I know my ABCs,\nNext time won't you sing with me?",
        "questions": [
            ("What comes right after A B C?", [("", "D", True), ("", "Z", False), ("", "Q", False)]),
            ("What is the last letter in the song?", [("", "Z", True), ("", "Y", False), ("", "A", False)]),
        ],
    },
]


BADGE_DATA = [
    ("First Steps", "Completed your very first rhyme!", "🌟", "rhymes_completed", 1),
    ("Rhyme Explorer", "Completed 5 rhymes.", "🧭", "rhymes_completed", 5),
    ("Quiz Whiz", "Scored a perfect quiz result.", "🧠", "quiz_score_perfect", 1),
    ("Repeat Champion", "Used Smart Repeat 10 times.", "🔁", "repeat_master", 10),
    ("Quiz Master", "Completed 5 quizzes.", "🏆", "quizzes_taken", 5),
]


class Command(BaseCommand):
    help = "Create the sample learning library, quizzes and gamification badges."

    def handle(self, *args, **options):
        categories = {}
        for order, item in enumerate(RHYME_DATA):
            name, icon = item["category"]
            category, _ = Category.objects.update_or_create(
                name=name,
                defaults={"icon_emoji": icon, "order": order},
            )
            categories[name] = category

            rhyme, created = Rhyme.objects.update_or_create(
                slug=slugify(item["title"]),
                defaults={
                    "title": item["title"],
                    "category": category,
                    "description": item["description"],
                    "lyrics": item["lyrics"],
                    "difficulty": item["difficulty"],
                    "duration_seconds": 60,
                    "is_published": True,
                    "order": order,
                },
            )

            quiz, _ = Quiz.objects.get_or_create(
                rhyme=rhyme,
                defaults={"title": f"{rhyme.title} Quiz", "passing_score_pct": 60},
            )

            if quiz.questions.count() == 0:
                for q_order, (question_text, choices) in enumerate(item["questions"], start=1):
                    question = Question.objects.create(
                        quiz=quiz,
                        text=question_text,
                        order=q_order,
                    )
                    for c_order, (emoji, text, correct) in enumerate(choices, start=1):
                        Choice.objects.create(
                            question=question,
                            text=text,
                            emoji=emoji,
                            is_correct=correct,
                            order=c_order,
                        )

            self.stdout.write(
                self.style.SUCCESS(
                    f"{'Created' if created else 'Ready'}: {rhyme.title}"
                )
            )

        for name, description, emoji, criteria_type, criteria_value in BADGE_DATA:
            Badge.objects.update_or_create(
                name=name,
                defaults={
                    "description": description,
                    "icon_emoji": emoji,
                    "criteria_type": criteria_type,
                    "criteria_value": criteria_value,
                },
            )

        self.stdout.write(self.style.SUCCESS("Seed data is ready."))
