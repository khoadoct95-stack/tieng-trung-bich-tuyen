import os
import json
import subprocess
from django.shortcuts import render, get_object_or_404, redirect
from django.http import JsonResponse, HttpResponse
from django.contrib.auth.decorators import login_required
from django.contrib.auth.views import PasswordChangeView
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import login, logout
from django.urls import reverse_lazy
from django.db.models import Min
from django.views.decorators.csrf import csrf_exempt
from django.contrib import messages
from .models import Curriculum, Lesson, Vocabulary, GameHistory
from .models import Exam, ExamQuestion, ExamResult

# ==========================================
# 1. CÁC HÀM CƠ BẢN CỦA WEB
# ==========================================
@login_required
def home(request):
    curriculums = Curriculum.objects.all()
    return render(request, 'courses/home.html', {'curriculums': curriculums})

@login_required
def lesson_list(request, curriculum_id):
    curriculum = get_object_or_404(Curriculum, id=curriculum_id)
    lessons = curriculum.lessons.all().order_by('order')
    return render(request, 'courses/lesson_list.html', {'curriculum': curriculum, 'lessons': lessons})

@login_required
def vocab_list(request, lesson_id):
    lesson = get_object_or_404(Lesson, id=lesson_id)
    vocabularies = lesson.vocabularies.all()
    return render(request, 'courses/vocab_list.html', {'lesson': lesson, 'vocabularies': vocabularies})

@login_required
def flashcard_view(request, lesson_id):
    lesson = get_object_or_404(Lesson, id=lesson_id)
    vocabularies = lesson.vocabularies.all()
    return render(request, 'courses/flashcard.html', {'lesson': lesson, 'vocabularies': vocabularies})

# ==========================================
# 2. CÁC HÀM TRÒ CHƠI
# ==========================================
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

# ==========================================
# 3. ĐĂNG KÝ & ĐĂNG XUẤT
# ==========================================
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

# ==========================================
# 4. BẢNG XẾP HẠNG & HỒ SƠ CÁ NHÂN (MỚI)
# ==========================================
@login_required
def dashboard_view(request):
    selected_game = request.GET.get('game', 'quiz_1')
    game_names = {'quiz_1': 'Nối từ', 'quiz_2': 'Lật thẻ', 'quiz_3': 'Viết chữ', 'quiz_4': 'Phát âm'}
    selected_game_name = game_names.get(selected_game, 'Nối từ')
    
    leaderboard_query = GameHistory.objects.filter(game_type=selected_game)\
        .values('user__username', 'user__first_name', 'lesson__id', 'lesson__title_vietnamese')\
        .annotate(best_time=Min('time_taken'))\
        .order_by('best_time')
        
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
        'leaderboard': leaderboard,
        'top_3': top_3,
        'selected_game': selected_game,
        'selected_game_name': selected_game_name,
        'personal_best': personal_best,
        'user_rank': user_rank,
        'active_tab': active_tab,
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
        'history_records': history_records,
        'best_scores': best_scores,
    })

# ==========================================
# 5. WEBHOOK GITHUB (BẢN CHỐNG KẸT LỖI)
# ==========================================
@csrf_exempt
def github_webhook(request):
    if request.method == 'POST':
        project_dir = '/home/xuehanyu/tieng-trung-bich-tuyen'
        wsgi_file = '/var/www/xuehanyu_pythonanywhere_com_wsgi.py'
        try:
            # Tải toàn bộ bản cập nhật mới nhất từ GitHub
            subprocess.run(['git', 'fetch', '--all'], cwd=project_dir, check=True)
            # Ép máy chủ xóa bỏ các chỉnh sửa thủ công, đồng bộ 100% theo nhánh main
            subprocess.run(['git', 'reset', '--hard', 'origin/main'], cwd=project_dir, check=True)
            
            # Khởi động lại web
            subprocess.run(['touch', wsgi_file], check=True)
            return HttpResponse("Updated code successfully")
        except subprocess.CalledProcessError as e:
            return HttpResponse(f"Error: {str(e)}", status=500)
    return HttpResponse("Invalid request", status=400)

# Hàm hiển thị trang làm bài thi HSK
# Bổ sung json vào thư viện nếu cần (thường Django tự hiểu JSONField)
@login_required(login_url='login')
def take_exam(request, exam_id):
    exam = get_object_or_404(Exam, id=exam_id)
    questions = ExamQuestion.objects.filter(exam=exam).order_by('question_number')

    if request.method == 'POST':
        total_correct = 0
        user_answers_dict = {} # <-- TẠO CUỐN SỔ TAY LƯU ĐÁP ÁN

        for q in questions:
            submitted_answer = request.POST.get(f'q_{q.id}', '').strip().upper()
            
            # Ghi chép lại học viên đã chọn gì cho câu này
            user_answers_dict[str(q.id)] = submitted_answer 
            
            correct_ans = str(q.correct_answer).strip().upper()
            if submitted_answer and submitted_answer == correct_ans:
                total_correct += 1

        score = total_correct * 5

        # LƯU KẾT QUẢ KÈM THEO CUỐN SỔ TAY ĐÁP ÁN
        result = ExamResult.objects.create(
            user=request.user,
            exam=exam,
            score=score,
            total_correct=total_correct,
            user_answers=user_answers_dict, # <-- Đưa vào DB
            time_spent=0  # <--- BỔ SUNG DÒNG NÀY ĐỂ TRÁNH LỖI NOT NULL
        )

        messages.success(request, "🎉 Chúc mừng bạn đã hoàn thành bài thi!")
        return redirect('exam_result', result_id=result.id)

    return render(request, 'courses/take_exam.html', {'exam': exam, 'questions': questions})

# ==========================================
# HÀM MỚI: XEM LẠI CHI TIẾT BÀI LÀM
# ==========================================
@login_required(login_url='login')
def review_exam(request, result_id):
    result = get_object_or_404(ExamResult, id=result_id, user=request.user)
    exam = result.exam
    questions = ExamQuestion.objects.filter(exam=exam).order_by('question_number')

    # Bơm thêm dữ liệu (Đúng/Sai) vào từng câu hỏi để giao diện dễ bôi màu
    for q in questions:
        q.user_ans = result.user_answers.get(str(q.id), '')
        q.correct_ans = str(q.correct_answer).strip().upper()
        q.is_correct = (q.user_ans == q.correct_ans)

    return render(request, 'courses/review_exam.html', {
        'exam': exam,
        'questions': questions,
        'result': result
    })


# HÀM HIỂN THỊ KẾT QUẢ ĐIỂM SỐ
@login_required(login_url='login')
def exam_result(request, result_id):
    # Chỉ cho phép học viên xem điểm của chính mình
    result = get_object_or_404(ExamResult, id=result_id, user=request.user)
    
    # Tính tỉ lệ phần trăm làm đúng
    total_questions = ExamQuestion.objects.filter(exam=result.exam).count()
    percentage = int((result.total_correct / total_questions) * 100) if total_questions > 0 else 0
    
    # Đánh giá Đỗ / Trượt (Chuẩn HSK 1: >= 120 điểm là Đỗ)
    is_passed = result.score >= 120

    return render(request, 'courses/exam_result.html', {
        'result': result,
        'total_questions': total_questions,
        'percentage': percentage,
        'is_passed': is_passed
    })

# Hàm hiển thị danh sách các đề thi
def exam_list(request):
    # Lấy tất cả đề thi, sắp xếp theo đề mới nhất lên đầu
    exams = Exam.objects.all().order_by('-created_at')
    return render(request, 'courses/exam_list.html', {'exams': exams})