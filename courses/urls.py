from django.urls import path
from . import views
from django.contrib.auth import views as auth_views

urlpatterns = [
    # ==========================================
    # CÁC ĐƯỜNG DẪN HIỆN TẠI CỦA BẠN (GIỮ NGUYÊN)
    # ==========================================
    path('', views.home, name='home'),
    path('curriculum/<int:curriculum_id>/', views.lesson_list, name='lesson_list'),
    path('lesson/<int:lesson_id>/', views.vocab_list, name='vocab_list'),
    path('lesson/<int:lesson_id>/flashcard/', views.flashcard_view, name='flashcard_view'),
    path('lesson/<int:lesson_id>/quiz-1/', views.quiz_1_view, name='quiz_1'),
    path('lesson/<int:lesson_id>/quiz-2/', views.quiz_2_view, name='quiz_2'),
    path('lesson/<int:lesson_id>/quiz-3/', views.quiz_3_view, name='quiz_3'),
    path('lesson/<int:lesson_id>/quiz-4/', views.quiz_4_view, name='quiz_4'),
    path('lesson/<int:lesson_id>/games/', views.game_zone_view, name='game_zone'),
    
    path('register/', views.register_view, name='register'),
    path('login/', auth_views.LoginView.as_view(template_name='courses/login.html'), name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('save-score/', views.save_score, name='save_score'),
    
    path('leaderboard/', views.dashboard_view, name='leaderboard'),
    path('profile/', views.profile_view, name='profile'),
    path('github_webhook/', views.github_webhook, name='github_webhook'),
    
    path('exams/', views.exam_list, name='exam_list'),
    path('exam/<int:exam_id>/', views.take_exam, name='take_exam'),
    path('exam-result/<int:result_id>/', views.exam_result, name='exam_result'),
    path('exam-review/<int:result_id>/', views.review_exam, name='review_exam'),
    path('import-excel/', views.import_excel, name='import_excel'),
    path('upload-zip/', views.upload_exam_images_zip, name='upload_exam_images_zip'),

    # ==========================================
    # ĐƯỜNG DẪN MỚI CHO KHU VỰC GIẢI TRÍ (GAMES)
    # ==========================================
    # 1. Đường dẫn mở giao diện Game 1
    path('games/ngu-kiem/', views.game_shooter_view, name='game_shooter'),
    
    # 2. Đường dẫn API để Game lấy từ vựng (ẩn dưới nền)
    path('api/get-vocab-game/', views.api_get_vocab_for_game, name='api_get_vocab_game'),
    
    # 3. Đường dẫn API để lưu kỷ lục điểm số (ẩn dưới nền)
    path('api/save-game-record/', views.api_save_game_record, name='api_save_game_record'),
]