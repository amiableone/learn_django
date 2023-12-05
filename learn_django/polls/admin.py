from django.contrib import admin

# Register your models here.
from .models import Question, Choice


class ChoiceInline(admin.TabularInline):
    model = Choice
    extra = 3


class QuestionAdmin(admin.ModelAdmin):
    fieldsets = [
        ("Ask your question", {"fields": ["question_text"]}),
        ("Fill date info", {
            "fields": ["pub_date"],
            "classes": ["collapse"]
        })
    ]
    inlines = [ChoiceInline]
    list_display = ["question_text", "pub_date", "is_new"]
    list_filter = ["pub_date"]
    search_fields = ["question_text"]


admin.site.register(Question, QuestionAdmin)
