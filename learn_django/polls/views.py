from django.shortcuts import render

# Create your views here.
from django.http import HttpResponse, Http404
from django.template import loader
from django.shortcuts import render
from .models import Question


def index(request):
    latest_questions_list = Question.objects.order_by("-pub_date")[:5]
    output = ' '.join([q.question_text for q in latest_questions_list])
    template = loader.get_template("polls/index.html")
    context = {
        "latest_questions_list": latest_questions_list
    }
    return HttpResponse(template.render(context, request))


def detail(request, question_id):
    try:
        question = Question.objects.get(pk=question_id)
    except Question.DoesNotExist:
        raise Http404("Question does not exist, idiot")
    return render(request, "polls/detail.html", {"question": question})


def results(request, question_id):
    return HttpResponse(f"You're looking at the results of question {question_id}")


def vote(request, question_id):
    return HttpResponse(f"You're voting on question {question_id}")
