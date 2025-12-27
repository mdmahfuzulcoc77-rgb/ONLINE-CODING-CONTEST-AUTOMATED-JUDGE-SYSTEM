# contest_site/urls.py
from django.contrib import admin
from django.urls import path
from django.contrib.auth import views as auth_views
from core import views

urlpatterns = [
    path('admin/', admin.site.urls),
    
    path('register/', views.register, name='register'),
    path('login/', auth_views.LoginView.as_view(template_name='login.html'), name='login'),
    path('logout/', auth_views.LogoutView.as_view(next_page='login'), name='logout'),
    

    path('', views.home, name='home'),
    
    path('submit/<int:question_id>/', views.submit_answer, name='submit_answer'),
    
    path('my-results/', views.my_results, name='my_results'),
    path('leaderboard/', views.leaderboard, name='leaderboard'),

]