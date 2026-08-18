from django.urls import path
from . import views
from django.contrib.auth import views as auth_views

urlpatterns = [
    path('', views.home, name='home'),
    path('curriculum/<int:curriculum_id>/', views.lesson_list, name='lesson_list'),
    path('lesson/<int:lesson_id>/', views.vocab_list, name='vocab_list'),
    path('lesson/<int:lesson_id>/flashcard/', views.flashcard_view, name='flashcard_view'),
    path('lesson/<int:lesson_id>/quiz-1/', views.quiz_1_view, name='quiz_1'),
    path('lesson/<int:lesson_id>/quiz-2/', views.quiz_2_view, name='quiz_2'),
    path('lesson/<int:lesson_id>/quiz-3/', views.quiz_3_view, name='quiz_3'),
    # Thêm dòng này cho Game 4:
    path('lesson/<int:lesson_id>/quiz-4/', views.quiz_4_view, name='quiz_4'),
    # Thêm dòng này:
    path('lesson/<int:lesson_id>/games/', views.game_zone_view, name='game_zone'),
    path('register/', views.register_view, name='register'),
    path('login/', auth_views.LoginView.as_view(template_name='courses/login.html'), name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('save-score/', views.save_score, name='save_score'),
    # Thêm dòng này:
    path('dashboard/', views.dashboard_view, name='dashboard'),
    # Thêm 2 dòng này cho Hồ sơ cá nhân:
    path('profile/', views.profile_view, name='profile'),
    path('github_webhook/', views.github_webhook, name='github_webhook'),
    path('exam/<int:exam_id>/', views.take_exam, name='take_exam'),
]