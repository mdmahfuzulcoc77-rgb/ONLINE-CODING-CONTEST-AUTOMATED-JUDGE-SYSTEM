from django.db import models
from django.contrib.auth.models import User


class ContestSetting(models.Model):
    title = models.CharField(max_length=100, default="My Contest")
    end_time = models.DateTimeField(help_text="Global Contest End Time")

    def __str__(self):
        return self.title

class Question(models.Model):
    title = models.CharField(max_length=200)
    description = models.TextField()
    input_data = models.TextField(blank=True, null=True, help_text="Ex: 5 10 (Optional)")
    expected_output = models.TextField(default="", help_text="Ex: 15 (Must match exactly)")
    time_limit_minutes = models.IntegerField(default=10, help_text="Duration in minutes") 
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title


class QuestionTimer(models.Model):
    student = models.ForeignKey(User, on_delete=models.CASCADE)
    question = models.ForeignKey(Question, on_delete=models.CASCADE)
    start_time = models.DateTimeField(auto_now_add=True) 

class Submission(models.Model):
    student = models.ForeignKey(User, on_delete=models.CASCADE)
    question = models.ForeignKey(Question, on_delete=models.CASCADE)
    answer = models.TextField()
    submitted_at = models.DateTimeField(auto_now_add=True)
    status = models.CharField(max_length=20, default='Pending') 

    def __str__(self):
        return f"{self.student.username} - {self.question.title}"