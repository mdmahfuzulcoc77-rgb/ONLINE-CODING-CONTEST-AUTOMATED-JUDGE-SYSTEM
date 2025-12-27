import sys
import io
import datetime 
from django.utils import timezone 
from django.contrib.auth.models import User
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.decorators import login_required
from .models import Question, Submission, ContestSetting, QuestionTimer


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
    my_submissions = Submission.objects.filter(student=request.user).values_list('question_id', flat=True)
    return render(request, 'home.html', {'questions': questions, 'my_submissions': my_submissions})


@login_required
def my_results(request):
    submissions = Submission.objects.filter(student=request.user).order_by('-submitted_at')
    return render(request, 'results.html', {'submissions': submissions})


@login_required
def submit_answer(request, question_id):
    question = get_object_or_404(Question, id=question_id)
    
    timer, created = QuestionTimer.objects.get_or_create(student=request.user, question=question)
    
    end_time = timer.start_time + datetime.timedelta(minutes=question.time_limit_minutes)
    

    if timezone.now() > end_time:
        return render(request, 'time_over.html')

    if request.method == 'POST':
        user_code = request.POST.get('answer')
        
        
        if timezone.now() > end_time:
             return render(request, 'time_over.html')

 
        old_stdout = sys.stdout
        new_stdout = io.StringIO()
        sys.stdout = new_stdout
        
        old_stdin = sys.stdin
        if question.input_data:
            sys.stdin = io.StringIO(question.input_data)

        submission_status = "Pending"
        
        try:
            exec(user_code, {}) 
            actual_output = new_stdout.getvalue().strip()
            expected_output = question.expected_output.strip()
            
            if actual_output == expected_output:
                submission_status = "Accepted"
            else:
                submission_status = "Rejected"       
        except Exception as e:
            submission_status = f"Error: {e}" 
        finally:
            sys.stdout = old_stdout
            sys.stdin = old_stdin

        Submission.objects.create(
            student=request.user, 
            question=question, 
            answer=user_code, 
            status=submission_status
        )
        return redirect('my_results')

   
    return render(request, 'submit_answer.html', {
        'question': question,
        'deadline': end_time.isoformat() 
    })


def leaderboard(request):
    users = User.objects.all()
    data = []
    for user in users:
        solved_count = Submission.objects.filter(student=user, status='Accepted').values('question').distinct().count()
        if solved_count > 0:
            data.append({'username': user.username, 'solved': solved_count})
    data.sort(key=lambda x: x['solved'], reverse=True)
    return render(request, 'leaderboard.html', {'leaders': data})