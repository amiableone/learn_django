import datetime

from django.test import TestCase
from django.utils import timezone
from django.urls import reverse
from django.core.exceptions import MultipleObjectsReturned
from .models import Question


class QuestionModelTests(TestCase):
    def test_is_new_with_future_question(self):
        """
        `is_new` returns False for questions which `pub_date`
        is in the future.
        """
        time = timezone.now() + datetime.timedelta(days=30)
        future_question = Question(pub_date=time)
        self.assertIs(future_question.is_new, False)

    def test_is_new_with_old_question(self):
        """
        `is_new` returns False for questions which `pub_date`
        is more than a day ago.
        """
        time = timezone.now() - datetime.timedelta(days=1, microseconds=1)
        old_question = Question(pub_date=time)
        self.assertIs(old_question.is_new, False)

    def test_is_new_with_recent_question(self):
        """
        `is_new` returns True for questions which `pub_date`
        is within the last day.
        """
        time = timezone.now() - datetime.timedelta(hours=23, minutes=59, seconds=59, milliseconds=999)
        recent_question = Question(pub_date=time)
        self.assertIs(recent_question.is_new, True)


def create_question(question_text, days_offset):
    """
    Create a question with a pub_date `days_offset` days offset
    to now (negative for questions published in the past).
    """
    time = timezone.now() + datetime.timedelta(days=days_offset)
    return Question.objects.create(question_text=question_text, pub_date=time)


class QuestionIndexViewTest(TestCase):
    def test_no_questions(self):
        """
        If no questions exist, an appropriate message is displayed.
        """
        response = self.client.get(reverse("polls:index"))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "No polls are available.")
        self.assertQuerySetEqual(response.context["question_list"], [])

    def test_past_question_no_choice(self):
        """
        If a question published in the past doesn't have choices,
        it's not displayed.
        """
        create_question("Past question", -1)
        response = self.client.get(reverse("polls:index"))
        self.assertEqual(response.status_code, 200)
        self.assertQuerySetEqual(
            response.context["question_list"],
            []
        )

    def test_past_question_with_choice(self):
        """
        If a question published in the past does have choices,
        it's displayed.
        """
        question = create_question("Past question", -1)
        question.choice_set.create(choice_text="Choice")
        response = self.client.get(reverse("polls:index"))
        self.assertEqual(response.status_code, 200)
        self.assertQuerySetEqual(
            response.context["question_list"],
            [question]
        )

    def test_future_question(self):
        """
        A question that is yet to be published will not be displayed.
        """
        create_question("Future question", 1)
        response = self.client.get(reverse("polls:index"))
        self.assertQuerySetEqual(response.context["question_list"], [])

    def test_past_question_no_choice_and_future_question(self):
        """
        If a past question with no choice and a future question exist,
        both are not displayed.
        """
        create_question("Past question", -1)
        create_question("Future question", 1)
        response = self.client.get(reverse("polls:index"))
        self.assertQuerySetEqual(
            response.context["question_list"],
            []
        )

    def test_past_question_with_choice_and_future_question(self):
        """
        If a past question with a choice and a future question exist,
        only the past one is displayed.
        """
        question = create_question("Past question", -1)
        create_question("Future question", 1)
        question.choice_set.create(choice_text="Choice")
        response = self.client.get(reverse("polls:index"))
        self.assertQuerySetEqual(
            response.context["question_list"],
            [question]
        )

    def test_two_past_questions_no_choice_and_two_past_questions_with_choice(self):
        """
        Only past questions with choice are displayed.
        """
        create_question("Past question 0", -1)
        question1 = create_question("Past question 1", -5)
        question2 = create_question("Past question 2", -10)
        create_question("Past question 3", -15)
        question1.choice_set.create(choice_text="Choice")
        question2.choice_set.create(choice_text="Choice")
        response = self.client.get(reverse("polls:index"))
        self.assertQuerySetEqual(
            response.context["question_list"],
            [
                question1,
                question2
            ]
        )

    def test_displayed_question_is_displayed_once(self):
        """
        Any past question with choice is displayed once
        (no matter the number of choices).
        """
        # Past questions with choices
        question1 = create_question("Past question 1", -5)
        question2 = create_question("Past question 2", -10)
        question1.choice_set.create(choice_text="Choice 1-1")
        question1.choice_set.create(choice_text="Choice 1-2")
        question2.choice_set.create(choice_text="Choice 2-1")
        question2.choice_set.create(choice_text="Choice 2-2")

        # Past question without choice
        create_question("Past question 3", -15)

        # Future question
        create_question("Future question", 1)

        response = self.client.get(reverse("polls:index"))
        self.assertQuerySetEqual(
            response.context["question_list"],
            [
                question1,
                question2
            ]
        )


class QuestionDetailViewTest(TestCase):
    def test_past_question_with_choice(self):
        """
        The detail view of a published question with choice
        displays the question text.
        """
        question = create_question("Past question", -1)
        question.choice_set.create(choice_text="Choice")
        url = reverse("polls:detail", args=(question.id,))
        response = self.client.get(url)
        self.assertContains(response, question.question_text)

    def test_past_question_no_choice(self):
        """
        The detail view of a published question without choices
        returns a 404 page.
        """
        question = create_question("Past question", -1)
        url = reverse("polls:detail", args=(question.id,))
        response = self.client.get(url)
        self.assertEqual(response.status_code, 404)

    def test_future_question(self):
        """
        The detail view of a question that is yet to be published
        returns a 404 page.
        """
        question = create_question("Future question", 1)
        url = reverse("polls:detail", args=(question.id,))
        response = self.client.get(url)
        self.assertEqual(response.status_code, 404)

    def test_number_of_objects_view_returns(self):
        """
        `get()` returns a single `Question` object from a queryset.
        """
        question = create_question("Past question", -1)
        question.choice_set.create(choice_text="Choice 1-1")
        question.choice_set.create(choice_text="Choice 1-2")
        url = reverse("polls:detail", args=(question.id,))
        try:
            response = self.client.get(url)
            self.assertContains(response, question.question_text)
            self.assertEqual(
                response.context["question"],
                question
            )
        except MultipleObjectsReturned:
            self.fail("MultipleObjectsReturned exception was raised")


class QuestionResultsViewTest(TestCase):
    def test_past_question_with_choice(self):
        """
        The results view of a published question with choices
        displays the text of the question and number of votes
        for each choice.
        """
        question = create_question("Past question", -1)
        question.choice_set.create(choice_text="Choice")
        url = reverse("polls:results", args=(question.id,))
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, question.question_text)

    def test_past_question_no_choice(self):
        """
        The results view of a published question without choices
        returns a 404 page.
        """
        question = create_question("Past question.", -1)
        url = reverse("polls:results", args=(question.id,))
        response = self.client.get(url)
        self.assertEqual(response.status_code, 404)

    def test_future_question(self):
        """
        The results view of a question that is yet to be published
        returns a 404 page.
        """
        question = create_question("Future question.", 1)
        url = reverse("polls:results", args=(question.id,))
        response = self.client.get(url)
        self.assertEqual(response.status_code, 404)

    def test_number_of_objects_view_returns(self):
        """
        `get()` returns a single `Question` object from a queryset.
        """
        question = create_question("Past question", -1)
        question.choice_set.create(choice_text="Choice 1-1")
        question.choice_set.create(choice_text="Choice 1-2")
        url = reverse("polls:results", args=(question.id,))
        try:
            response = self.client.get(url)
            self.assertContains(response, question.question_text)
            self.assertEqual(
                response.context["question"],
                question
            )
        except MultipleObjectsReturned:
            self.fail("MultipleObjectsReturned exception was raised")
