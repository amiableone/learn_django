from django.shortcuts import render
from django.http import HttpResponse, Http404, HttpResponseRedirect
from django.template import loader
from django.shortcuts import render, get_object_or_404
from django.urls import reverse
from django.views import generic
from django.utils import timezone
from .models import Question, Choice


class IndexView(generic.ListView):
    template_name = "polls/index.html"
    context_object_name = "question_list"

    def get_queryset(self):
        return Question.objects.filter(
            pub_date__lte=timezone.now()).exclude(
            choice__isnull=True,
        ).order_by("-pub_date")


class DetailView(generic.DetailView):
    model = Question
    template_name = "polls/detail.html"

    def get_queryset(self):
        """
        Questions with future `pub_date` and no choice
        are excluded.
        """
        return Question.objects.filter(
            pub_date__lte=timezone.now()).exclude(
            choice__isnull=True,
        ).order_by("-pub_date")


class ResultsView(generic.DetailView):
    model = Question
    template_name = "polls/results.html"

    def get_queryset(self):
        """
        Questions with future `pub_date` and no choice
        are excluded.
        """
        return Question.objects.filter(
            pub_date__lte=timezone.now()).exclude(
            choice__isnull=True,
        ).order_by("-pub_date")


def vote(request, question_id):
    question = get_object_or_404(Question, pk=question_id)
    try:
        selected_choice = question.choice_set.get(pk=request.POST["choice"])
    except (KeyError, Choice.DoesNotExist):
        # Redisplay the question voting form
        return render(
            request,
            "polls/detail.html",
            {
                "question": question,
                "error_message": "You didn't make a choice",
            },
        )
    else:
        selected_choice.votes += 1
        selected_choice.save()
        # Always return HttpResponseRedirect after successfully
        # dealing with POST data. This prevents data from being
        # posted twice if a user hits the Back button. This is
        # good web development practice in general
        return HttpResponseRedirect(reverse("polls:results", args=(question.id,)))
