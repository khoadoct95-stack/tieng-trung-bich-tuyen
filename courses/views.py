import subprocess
from django.db.models import Min
from django.views.decorators.csrf import csrf_exempt
from django.http import HttpResponse
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
    # 1. Xử lý Bảng xếp hạng
    selected_game = request.GET.get('game', 'quiz_1')
    game_names = {'quiz_1': 'Nối từ', 'quiz_2': 'Lật thẻ', 'quiz_3': 'Viết chữ', 'quiz_4': 'Phát âm'}
    selected_game_name = game_names.get(selected_game, 'Nối từ')
    
    # Lấy danh sách Top 100 (Kéo thêm trường first_name làm Tên hiển thị)
    leaderboard_query = GameHistory.objects.filter(game_type=selected_game)\
        .values('user__username', 'user__first_name', 'lesson__title_vietnamese')\
        .annotate(best_time=Min('time_taken'))\
        .order_by('best_time')
        
    leaderboard = list(leaderboard_query[:100])
    top_3 = leaderboard[:3] # Lấy riêng Top 3
    
    # 2. Tính toán thứ hạng và thành tích của chính User
    user_rank = None
    personal_best = None
    
    # Tìm xem user có trong Top 100 không
    for index, entry in enumerate(leaderboard):
        if entry['user__username'] == request.user.username:
            user_rank = index + 1
            personal_best = entry['best_time']
            break
            
    # Nếu không lọt Top 100 nhưng đã từng chơi (Tính rank thực tế)
    if not user_rank:
        pb_query = GameHistory.objects.filter(user=request.user, game_type=selected_game).aggregate(best=Min('time_taken'))['best']
        if pb_query:
            personal_best = pb_query
            # Đếm xem có bao nhiêu người điểm cao hơn
            better_count = GameHistory.objects.filter(game_type=selected_game).values('user').annotate(best=Min('time_taken')).filter(best__lt=personal_best).count()
            user_rank = better_count + 1

    active_tab = request.GET.get('tab', 'leaderboard')

    context = {
        'leaderboard': leaderboard,
        'top_3': top_3,
        'selected_game': selected_game,
        'selected_game_name': selected_game_name,
        'personal_best': personal_best,
        'user_rank': user_rank,
        'active_tab': active_tab,
    }
    return render(request, 'courses/dashboard.html', context)

# Trang Hồ sơ cá nhân
@login_required
def profile_view(request):
    # Xử lý cập nhật Tên hiển thị
    if request.method == 'POST':
        display_name = request.POST.get('display_name', '').strip()
        if display_name:
            request.user.first_name = display_name
            request.user.save()

    # Lịch sử hoạt động
    history_records = GameHistory.objects.filter(user=request.user).order_by('-created_at')
    
    # Thành tích cao nhất các game
    games = {'quiz_1': 'Nối từ', 'quiz_2': 'Lật thẻ', 'quiz_3': 'Viết chữ', 'quiz_4': 'Phát âm'}
    best_scores = []
    for code, name in games.items():
        best = GameHistory.objects.filter(user=request.user, game_type=code).aggregate(b=Min('time_taken'))['b']
        best_scores.append({'name': name, 'score': best})
        
    return render(request, 'courses/profile.html', {
        'history_records': history_records,
        'best_scores': best_scores,
    })

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

import os
import subprocess
from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt

@csrf_exempt
def github_webhook(request):
    # Chỉ xử lý khi GitHub gửi tín hiệu (POST request)
    if request.method == 'POST':
        # Đường dẫn tuyệt đối trên máy chủ PythonAnywhere của bạn
        project_dir = '/home/xuehanyu/tieng-trung-bich-tuyen'
        venv_python = '/home/xuehanyu/tieng-trung-bich-tuyen/venv/bin/python'
        wsgi_file = '/var/www/xuehanyu_pythonanywhere_com_wsgi.py'
        
        try:
            # 1. Kéo code mới nhất từ nhánh main trên GitHub về
            subprocess.run(['git', 'fetch', '--all'], cwd=project_dir, check=True)
            subprocess.run(['git', 'reset', '--hard', 'origin/main'], cwd=project_dir, check=True)
            
            # 2. Cập nhật cấu trúc Cơ sở dữ liệu (Nếu bạn có thêm/bớt trường dữ liệu trong models.py)
            #
            
            # 3. Gom tất cả file tĩnh mới (CSS, JS, ảnh giao diện)
            subprocess.run([venv_python, 'manage.py', 'collectstatic', '--noinput'], cwd=project_dir, check=True)
            
            # 4. Chạm (touch) vào file WSGI để báo máy chủ PythonAnywhere khởi động lại web
            subprocess.run(['touch', wsgi_file], check=True)
            
            return HttpResponse("✅ Webhook chạy thành công: Code, Database và Giao diện đã được làm mới!")
            
        except subprocess.CalledProcessError as e:
            # Báo lỗi nếu có lệnh nào đó chạy thất bại
            return HttpResponse(f"❌ Có lỗi xảy ra trong quá trình chạy lệnh tự động: {e}", status=500)
            
    # Nếu truy cập bằng trình duyệt thông thường (GET request)
    return HttpResponse("Trang này chỉ dành cho Webhook của GitHub.", status=400)

# ==========================================
# TÍNH NĂNG MỚI THÊM VÀO DƯỚI CÙNG
# ==========================================
@csrf_exempt
def github_webhook(request):
    if request.method == 'POST':
        try:
            subprocess.run(['git', 'pull'], cwd='/home/xuehanyu/tieng-trung-bich-tuyen', check=True)
            return HttpResponse("Updated code successfully")
        except Exception as e:
            return HttpResponse(f"Error: {str(e)}", status=500)
    return HttpResponse("Invalid request", status=400)

@login_required
def dashboard_view(request):
    selected_game = request.GET.get('game', 'quiz_1')
    game_names = {'quiz_1': 'Nối từ', 'quiz_2': 'Lật thẻ', 'quiz_3': 'Viết chữ', 'quiz_4': 'Phát âm'}
    selected_game_name = game_names.get(selected_game, 'Nối từ')
    
    leaderboard_query = GameHistory.objects.filter(game_type=selected_game)\
        .values('user__username', 'user__first_name', 'lesson__id', 'lesson__title_vietnamese')\
        .annotate(best_time=Min('time_taken')).order_by('best_time')
        
    leaderboard = list(leaderboard_query[:100])
    top_3 = leaderboard[:3]
    
    user_rank = None
    personal_best = None
    for index, entry in enumerate(leaderboard):
        if entry['user__username'] == request.user.username:
            user_rank = index + 1
            personal_best = entry['best_time']
            break
            
    if not user_rank:
        pb_query = GameHistory.objects.filter(user=request.user, game_type=selected_game).aggregate(best=Min('time_taken'))['best']
        if pb_query:
            personal_best = pb_query
            better_count = GameHistory.objects.filter(game_type=selected_game).values('user').annotate(best=Min('time_taken')).filter(best__lt=personal_best).count()
            user_rank = better_count + 1

    active_tab = request.GET.get('tab', 'leaderboard')
    context = {
        'leaderboard': leaderboard, 'top_3': top_3, 'selected_game': selected_game,
        'selected_game_name': selected_game_name, 'personal_best': personal_best,
        'user_rank': user_rank, 'active_tab': active_tab,
    }
    return render(request, 'courses/dashboard.html', context)

@login_required
def profile_view(request):
    if request.method == 'POST':
        display_name = request.POST.get('display_name', '').strip()
        if display_name:
            request.user.first_name = display_name
            request.user.save()

    history_records = GameHistory.objects.filter(user=request.user).order_by('-created_at')
    games = {'quiz_1': 'Nối từ', 'quiz_2': 'Lật thẻ', 'quiz_3': 'Viết chữ', 'quiz_4': 'Phát âm'}
    best_scores = []
    for code, name in games.items():
        best = GameHistory.objects.filter(user=request.user, game_type=code).aggregate(b=Min('time_taken'))['b']
        best_scores.append({'name': name, 'score': best})
        
    return render(request, 'courses/profile.html', {
        'history_records': history_records, 'best_scores': best_scores,
    })