from django.contrib import admin
from .models import Question, Submission, ContestSetting

admin.site.register(Question)
admin.site.register(Submission)
admin.site.register(ContestSetting)