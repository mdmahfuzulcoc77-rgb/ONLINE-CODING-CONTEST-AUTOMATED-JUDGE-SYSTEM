import os
import sys
from pathlib import Path

# প্রজেক্টের নাম
PROJECT_NAME = 'contest_site'
APP_NAME = 'core'

# ফোল্ডার তৈরির ফাংশন
def create_file(path, content):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, 'w', encoding='utf-8') as f:
        f.write(content.strip())
    print(f"Created: {path}")

def main():
    base_dir = Path.cwd() / PROJECT_NAME
    
    # ১. manage.py তৈরি
    manage_py_code = f"""
#!/usr/bin/env python
import os
import sys

def main():
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', '{PROJECT_NAME}.settings')
    try:
        from django.core.management import execute_from_command_line
    except ImportError as exc:
        raise ImportError(
            "Couldn't import Django. Are you sure it's installed?"
        ) from exc
    execute_from_command_line(sys.argv)

if __name__ == '__main__':
    main()
"""
    create_file(base_dir / 'manage.py', manage_py_code)

    # ২. settings.py তৈরি
    settings_code = f"""
from pathlib import Path
import os

BASE_DIR = Path(__file__).resolve().parent.parent
SECRET_KEY = 'django-insecure-magic-script-key'
DEBUG = True
ALLOWED_HOSTS = []

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    '{APP_NAME}',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = '{PROJECT_NAME}.urls'

TEMPLATES = [
    {{
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [],
        'APP_DIRS': True,
        'OPTIONS': {{
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        }},
    }},
]

WSGI_APPLICATION = '{PROJECT_NAME}.wsgi.application'

DATABASES = {{
    'default': {{
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }}
}}

AUTH_PASSWORD_VALIDATORS = []
LANGUAGE_CODE = 'en-us'
TIME_ZONE = 'UTC'
USE_I18N = True
USE_TZ = True
STATIC_URL = 'static/'
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'
LOGIN_REDIRECT_URL = 'home'
LOGOUT_REDIRECT_URL = 'login'
LOGIN_URL = 'login'
"""
    create_file(base_dir / PROJECT_NAME / 'settings.py', settings_code)

    # ৩. urls.py (Main) তৈরি
    urls_code = f"""
from django.contrib import admin
from django.urls import path
from django.contrib.auth import views as auth_views
from {APP_NAME} import views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('register/', views.register, name='register'),
    path('login/', auth_views.LoginView.as_view(template_name='login.html'), name='login'),
    path('logout/', auth_views.LogoutView.as_view(next_page='login'), name='logout'),
    path('', views.home, name='home'),
    path('submit/<int:question_id>/', views.submit_answer, name='submit_answer'),
]
"""
    create_file(base_dir / PROJECT_NAME / 'urls.py', urls_code)

    # ৪. wsgi.py এবং asgi.py (Standard)
    create_file(base_dir / PROJECT_NAME / '__init__.py', "")
    create_file(base_dir / PROJECT_NAME / 'wsgi.py', f"import os; from django.core.wsgi import get_wsgi_application; os.environ.setdefault('DJANGO_SETTINGS_MODULE', '{PROJECT_NAME}.settings'); application = get_wsgi_application()")
    create_file(base_dir / PROJECT_NAME / 'asgi.py', f"import os; from django.core.asgi import get_asgi_application; os.environ.setdefault('DJANGO_SETTINGS_MODULE', '{PROJECT_NAME}.settings'); application = get_asgi_application()")

    # ৫. অ্যাপ তৈরি (Models, Views, Admin)
    create_file(base_dir / APP_NAME / '__init__.py', "")
    create_file(base_dir / APP_NAME / 'apps.py', f"from django.apps import AppConfig\nclass CoreConfig(AppConfig):\n    default_auto_field = 'django.db.models.BigAutoField'\n    name = '{APP_NAME}'")

    # Models.py
    models_code = """
from django.db import models
from django.contrib.auth.models import User

class Question(models.Model):
    title = models.CharField(max_length=200)
    description = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title

class Submission(models.Model):
    student = models.ForeignKey(User, on_delete=models.CASCADE)
    question = models.ForeignKey(Question, on_delete=models.CASCADE)
    answer = models.TextField()
    submitted_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.student.username} - {self.question.title}"
"""
    create_file(base_dir / APP_NAME / 'models.py', models_code)

    # Admin.py
    admin_code = """
from django.contrib import admin
from .models import Question, Submission

class SubmissionAdmin(admin.ModelAdmin):
    list_display = ('student', 'question', 'submitted_at')

admin.site.register(Question)
admin.site.register(Submission, SubmissionAdmin)
"""
    create_file(base_dir / APP_NAME / 'admin.py', admin_code)

    # Views.py
    views_code = """
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.decorators import login_required
from .models import Question, Submission

def register(request):
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('login')
    else:
        form = UserCreationForm()
    return render(request, 'register.html', {'form': form})

@login_required
def home(request):
    questions = Question.objects.all()
    # Find which questions this user specifically has answered
    my_submissions = Submission.objects.filter(student=request.user).values_list('question_id', flat=True)
    return render(request, 'home.html', {'questions': questions, 'my_submissions': my_submissions})

@login_required
def submit_answer(request, question_id):
    question = get_object_or_404(Question, id=question_id)
    if request.method == 'POST':
        answer_text = request.POST.get('answer')
        Submission.objects.create(student=request.user, question=question, answer=answer_text)
        return redirect('home')
    return render(request, 'submit_answer.html', {'question': question})
"""
    create_file(base_dir / APP_NAME / 'views.py', views_code)

    # ৬. টেমপ্লেট (HTML Files)
    templates_dir = base_dir / APP_NAME / 'templates'
    
    # Base HTML
    base_html = """
<!DOCTYPE html>
<html>
<head>
    <title>Contest Portal</title>
    <style>
        body { font-family: sans-serif; max-width: 800px; margin: 0 auto; padding: 20px; background-color: #f4f4f4; }
        nav { background: #333; padding: 10px; color: white; border-radius: 5px; }
        nav a { color: white; text-decoration: none; margin-right: 15px; }
        .container { background: white; padding: 20px; margin-top: 20px; border-radius: 5px; box-shadow: 0 0 10px rgba(0,0,0,0.1); }
        button { background: #28a745; color: white; padding: 10px 15px; border: none; cursor: pointer; border-radius: 3px; }
        button:hover { background: #218838; }
        textarea { width: 100%; padding: 10px; margin-bottom: 10px; }
        .badge { background: #007bff; color: white; padding: 2px 6px; border-radius: 4px; font-size: 0.8em; }
    </style>
</head>
<body>
    <nav>
        {% if user.is_authenticated %}
            <strong>Contest Portal</strong> | 
            <a href="{% url 'home' %}">Questions</a>
            <span style="float:right">
                User: {{ user.username }} | 
                <form action="{% url 'logout' %}" method="post" style="display:inline;">
                    {% csrf_token %}
                    <button type="submit" style="background:red; padding: 5px 10px; font-size: 12px;">Logout</button>
                </form>
            </span>
        {% else %}
            <a href="{% url 'login' %}">Login</a> | <a href="{% url 'register' %}">Register</a>
        {% endif %}
    </nav>
    <div class="container">
        {% block content %}{% endblock %}
    </div>
</body>
</html>
"""
    create_file(templates_dir / 'base.html', base_html)

    # Register HTML
    create_file(templates_dir / 'register.html', """
{% extends 'base.html' %}
{% block content %}
<h2>Student Registration</h2>
<form method="post">
    {% csrf_token %}
    {{ form.as_p }}
    <button type="submit">Sign Up</button>
</form>
{% endblock %}
""")

    # Login HTML
    create_file(templates_dir / 'login.html', """
{% extends 'base.html' %}
{% block content %}
<h2>Login</h2>
<form method="post">
    {% csrf_token %}
    {{ form.as_p }}
    <button type="submit">Login</button>
</form>
{% endblock %}
""")

    # Home HTML
    create_file(templates_dir / 'home.html', """
{% extends 'base.html' %}
{% block content %}
<h2>Problem Set</h2>
{% if questions %}
    <ul>
    {% for q in questions %}
        <li style="margin-bottom: 10px; padding: 10px; border-bottom: 1px solid #ddd;">
            <strong>{{ q.title }}</strong>
            {% if q.id in my_submissions %}
                <span class="badge">Solved/Submitted</span>
            {% endif %}
            <br>
            <a href="{% url 'submit_answer' q.id %}">View Problem & Submit Code</a>
        </li>
    {% endfor %}
    </ul>
{% else %}
    <p>No questions added by Admin yet.</p>
{% endif %}
{% endblock %}
""")

    # Submit Answer HTML
    create_file(templates_dir / 'submit_answer.html', """
{% extends 'base.html' %}
{% block content %}
<h2>Problem: {{ question.title }}</h2>
<div style="background: #eee; padding: 15px; border-radius: 5px; margin-bottom: 20px;">
    <strong>Description:</strong><br>
    {{ question.description|linebreaks }}
</div>

<h3>Submit Your Solution</h3>
<form method="post">
    {% csrf_token %}
    <label>Paste your code below:</label><br>
    <textarea name="answer" rows="10" placeholder="# Write your python code here..."></textarea>
    <button type="submit">Submit Solution</button>
</form>
<br>
<a href="{% url 'home' %}">Back to Problem List</a>
{% endblock %}
""")

    print("\n[SUCCESS] Project files generated successfully!")
    print(f"Now enter the folder: cd {PROJECT_NAME}")
    print("Then run: python manage.py makemigrations")
    print("Then run: python manage.py migrate")
    print("Then run: python manage.py createsuperuser")
    print("Finally: python manage.py runserver")

if __name__ == '__main__':
    main()