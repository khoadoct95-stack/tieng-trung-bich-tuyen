from django.shortcuts import render, get_object_or_404, redirect
from .models import Curriculum, Lesson, Vocabulary
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import login, logout
from django.contrib.auth.views import LoginView
import json
from django.http import JsonResponse
from .models import Curriculum, Lesson, Vocabulary, GameHistory
from django.contrib.auth.decorators import login_required
from django.contrib.auth.views import PasswordChangeView
from django.urls import reverse_lazy

# 1. Trang chủ: Chọn giáo trình
def home(request):
    curriculums = Curriculum.objects.all()
    return render(request, 'courses/home.html', {'curriculums': curriculums})

# 2. Trang danh sách bài học
def lesson_list(request, curriculum_id):
    curriculum = get_object_or_404(Curriculum, id=curriculum_id)
    lessons = curriculum.lessons.all().order_by('order')
    return render(request, 'courses/lesson_list.html', {'curriculum': curriculum, 'lessons': lessons})

# 3. Trang bảng từ vựng (Trọng tâm)
def vocab_list(request, lesson_id):
    lesson = get_object_or_404(Lesson, id=lesson_id)
    vocabularies = lesson.vocabularies.all()
    return render(request, 'courses/vocab_list.html', {'lesson': lesson, 'vocabularies': vocabularies})

# Thêm logic cho trang Flashcard
def flashcard_view(request, lesson_id):
    lesson = get_object_or_404(Lesson, id=lesson_id)
    vocabularies = lesson.vocabularies.all()
    return render(request, 'courses/flashcard.html', {'lesson': lesson, 'vocabularies': vocabularies})

# Thêm logic cho Bài kiểm tra 1 (Nối từ)
def quiz_1_view(request, lesson_id):
    lesson = get_object_or_404(Lesson, id=lesson_id)
    vocabularies = lesson.vocabularies.all()
    return render(request, 'courses/quiz_1.html', {'lesson': lesson, 'vocabularies': vocabularies})

# Thêm logic cho Bài kiểm tra 2 (Lật thẻ nhớ Pikachu/Pokemon)
def quiz_2_view(request, lesson_id):
    lesson = get_object_or_404(Lesson, id=lesson_id)
    vocabularies = lesson.vocabularies.all()
    return render(request, 'courses/quiz_2.html', {'lesson': lesson, 'vocabularies': vocabularies})

# Thêm logic cho Bài kiểm tra 3 (Kiểm tra nét viết)
def quiz_3_view(request, lesson_id):
    lesson = get_object_or_404(Lesson, id=lesson_id)
    vocabularies = lesson.vocabularies.all()
    return render(request, 'courses/quiz_3.html', {'lesson': lesson, 'vocabularies': vocabularies})

# Thêm logic cho Bài kiểm tra 4 (Ghi âm phát âm)
def quiz_4_view(request, lesson_id):
    lesson = get_object_or_404(Lesson, id=lesson_id)
    vocabularies = lesson.vocabularies.all()
    return render(request, 'courses/quiz_4.html', {'lesson': lesson, 'vocabularies': vocabularies})

# View cho Khu vực Game
def game_zone_view(request, lesson_id):
    lesson = get_object_or_404(Lesson, id=lesson_id)
    return render(request, 'courses/game_zone.html', {'lesson': lesson})

# Đăng ký tài khoản
def register_view(request):
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user) # Đăng ký xong tự động đăng nhập luôn
            return redirect('home')
    else:
        form = UserCreationForm()
    return render(request, 'courses/register.html', {'form': form})

# Đăng xuất
def logout_view(request):
    logout(request)
    return redirect('home')

# API Lưu điểm số Game
def save_score(request):
    if request.method == 'POST' and request.user.is_authenticated:
        data = json.loads(request.body)
        lesson_id = data.get('lesson_id')
        game_type = data.get('game_type')
        time_taken = data.get('time_taken')

        lesson = get_object_or_404(Lesson, id=lesson_id)
        
        # Lưu vào Database
        GameHistory.objects.create(
            user=request.user,
            lesson=lesson,
            game_type=game_type,
            time_taken=time_taken
        )
        return JsonResponse({'status': 'success', 'message': 'Đã lưu điểm'})
    return JsonResponse({'status': 'error'}, status=400)
from django.db.models import Min

# Bảng xếp hạng và Lịch sử cá nhân
# Bảng xếp hạng và Lịch sử cá nhân
def dashboard_view(request):
    if not request.user.is_authenticated:
        return redirect('login') # Bắt buộc đăng nhập
    
    # 1. Lấy lịch sử 15 lần chơi gần nhất của user này
    history = GameHistory.objects.filter(user=request.user).order_by('-created_at')[:15]
    
    # 2. Xử lý bộ lọc Game cho Bảng xếp hạng
    selected_game = request.GET.get('game', 'quiz_1') # Mặc định lấy quiz_1
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
    
    # 3. Truy vấn Top 10 cao thủ cho game được chọn
    leaderboard = GameHistory.objects.filter(game_type=selected_game)\
        .values('user__username', 'lesson__title')\
        .annotate(best_time=Min('time_taken'))\
        .order_by('best_time')[:10]
        
    # Giữ trạng thái Tab (đang xem Lịch sử hay Bảng xếp hạng)
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
    # Đếm tổng số lần đã chơi game của user này
    total_games = GameHistory.objects.filter(user=request.user).count()
    return render(request, 'courses/profile.html', {'total_games': total_games})

# Trang Đổi mật khẩu
class MyPasswordChangeView(PasswordChangeView):
    template_name = 'courses/change_password.html'
    success_url = reverse_lazy('profile') # Đổi xong quay về trang hồ sơ