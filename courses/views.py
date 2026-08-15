import json
from django.shortcuts import render, get_object_or_404, redirect
from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
from django.contrib.auth.views import PasswordChangeView
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import login, logout
from django.urls import reverse_lazy
from django.db.models import Min
from .models import Curriculum, Lesson, Vocabulary, GameHistory

# 1. Trang chủ: Chọn giáo trình
@login_required
def home(request):
    curriculums = Curriculum.objects.all()
    return render(request, 'courses/home.html', {'curriculums': curriculums})

# 2. Trang danh sách bài học
@login_required
def lesson_list(request, curriculum_id):
    curriculum = get_object_or_404(Curriculum, id=curriculum_id)
    lessons = curriculum.lessons.all().order_by('order')
    return render(request, 'courses/lesson_list.html', {'curriculum': curriculum, 'lessons': lessons})

# 3. Trang bảng từ vựng 
@login_required
def vocab_list(request, lesson_id):
    lesson = get_object_or_404(Lesson, id=lesson_id)
    vocabularies = lesson.vocabularies.all()
    return render(request, 'courses/vocab_list.html', {'lesson': lesson, 'vocabularies': vocabularies})

# View cho trang Flashcard
@login_required
def flashcard_view(request, lesson_id):
    lesson = get_object_or_404(Lesson, id=lesson_id)
    vocabularies = lesson.vocabularies.all()
    return render(request, 'courses/flashcard.html', {'lesson': lesson, 'vocabularies': vocabularies})

# Các View cho Trò chơi (Quiz 1 -> 4)
@login_required
def quiz_1_view(request, lesson_id):
    lesson = get_object_or_404(Lesson, id=lesson_id)
    vocabularies = lesson.vocabularies.all()
    return render(request, 'courses/quiz_1.html', {'lesson': lesson, 'vocabularies': vocabularies})

@login_required
def quiz_2_view(request, lesson_id):
    lesson = get_object_or_404(Lesson, id=lesson_id)
    vocabularies = lesson.vocabularies.all()
    return render(request, 'courses/quiz_2.html', {'lesson': lesson, 'vocabularies': vocabularies})

@login_required
def quiz_3_view(request, lesson_id):
    lesson = get_object_or_404(Lesson, id=lesson_id)
    vocabularies = lesson.vocabularies.all()
    return render(request, 'courses/quiz_3.html', {'lesson': lesson, 'vocabularies': vocabularies})

@login_required
def quiz_4_view(request, lesson_id):
    lesson = get_object_or_404(Lesson, id=lesson_id)
    vocabularies = lesson.vocabularies.all()
    return render(request, 'courses/quiz_4.html', {'lesson': lesson, 'vocabularies': vocabularies})

@login_required
def game_zone_view(request, lesson_id):
    lesson = get_object_or_404(Lesson, id=lesson_id)
    return render(request, 'courses/game_zone.html', {'lesson': lesson})

# API Lưu điểm số Game
@login_required
def save_score(request):
    if request.method == 'POST':
        data = json.loads(request.body)
        lesson_id = data.get('lesson_id')
        game_type = data.get('game_type')
        time_taken = data.get('time_taken')

        lesson = get_object_or_404(Lesson, id=lesson_id)
        
        GameHistory.objects.create(
            user=request.user,
            lesson=lesson,
            game_type=game_type,
            time_taken=time_taken
        )
        return JsonResponse({'status': 'success', 'message': 'Đã lưu điểm'})
    return JsonResponse({'status': 'error'}, status=400)

# Bảng xếp hạng và Lịch sử cá nhân
@login_required
def dashboard_view(request):
    history = GameHistory.objects.filter(user=request.user).order_by('-created_at')[:15]
    
    selected_game = request.GET.get('game', 'quiz_1')
    valid_games = ['quiz_1', 'quiz_2', 'quiz_3', 'quiz_4']
    if selected_game not in valid_games:
        selected_game = 'quiz_1'
        
    game_names = {
        'quiz_1': 'Nối từ',
        'quiz_2': 'Lật thẻ',
        'quiz_3': 'Viết chữ',
        'quiz_4': 'Phát âm'
    }
    selected_game_name = game_names[selected_game]
    
    leaderboard = GameHistory.objects.filter(game_type=selected_game)\
        .values('user__username', 'lesson__title')\
        .annotate(best_time=Min('time_taken'))\
        .order_by('best_time')[:10]
        
    active_tab = request.GET.get('tab', 'history')
    
    return render(request, 'courses/dashboard.html', {
        'history': history,
        'leaderboard': leaderboard,
        'selected_game': selected_game,
        'selected_game_name': selected_game_name,
        'active_tab': active_tab
    })

# Trang Hồ sơ cá nhân
@login_required
def profile_view(request):
    total_games = GameHistory.objects.filter(user=request.user).count()
    return render(request, 'courses/profile.html', {'total_games': total_games})

# Đổi mật khẩu
class MyPasswordChangeView(PasswordChangeView):
    template_name = 'courses/change_password.html'
    success_url = reverse_lazy('profile')

# Đăng ký & Đăng xuất (Không cần chặn @login_required)
def register_view(request):
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect('home')
    else:
        form = UserCreationForm()
    return render(request, 'courses/register.html', {'form': form})

def logout_view(request):
    logout(request)
    return redirect('login')