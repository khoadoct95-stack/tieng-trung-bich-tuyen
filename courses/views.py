import os
import json
import subprocess
import pandas as pd
import zipfile
import re
import random 
from io import BytesIO
from PIL import Image
from django.core.files.base import ContentFile
from django.shortcuts import render, get_object_or_404, redirect
from django.http import JsonResponse, HttpResponse
from django.contrib.auth.decorators import login_required
from django.contrib.auth.views import PasswordChangeView
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import login, logout
from django.urls import reverse_lazy
from django.db.models import Min, Max, Q
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
# 2. CÁC HÀM TRÒ CHƠI BÀI HỌC
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
# 4. BẢNG XẾP HẠNG & HỒ SƠ CÁ NHÂN
# ==========================================
@login_required
def dashboard_view(request):
    selected_game = request.GET.get('game', 'quiz_1')
    game_names = {'quiz_1': 'Nối từ', 'quiz_2': 'Lật thẻ', 'quiz_3': 'Viết chữ', 'quiz_4': 'Phát âm'}
    selected_game_name = game_names.get(selected_game, 'Nối từ')
    
    curriculums = Curriculum.objects.prefetch_related('lessons').all()
    selected_curriculum = request.GET.get('curriculum', '')
    selected_lesson = request.GET.get('lesson', '')

    query_filter = Q(game_type=selected_game)
    
    if selected_curriculum:
        query_filter &= Q(lesson__curriculum_id=selected_curriculum)
    if selected_lesson:
        query_filter &= Q(lesson_id=selected_lesson)

    leaderboard_query = GameHistory.objects.filter(query_filter)\
        .values('user__username', 'user__first_name', 'lesson__id', 'lesson__title_vietnamese', 'lesson__curriculum__title')\
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
        pb_query = GameHistory.objects.filter(query_filter & Q(user=request.user)).aggregate(best=Min('time_taken'))['best']
        if pb_query:
            personal_best = pb_query
            better_count = GameHistory.objects.filter(query_filter).values('user', 'lesson').annotate(best=Min('time_taken')).filter(best__lt=personal_best).count()
            user_rank = better_count + 1

    active_tab = request.GET.get('tab', 'leaderboard')

    highest_hsk = 0
    passed_exams = ExamResult.objects.filter(user=request.user, score__gte=120)
    if passed_exams.exists():
        highest_hsk = passed_exams.aggregate(Max('exam__hsk_level'))['exam__hsk_level__max']

    context = {
        'curriculums': curriculums,
        'selected_curriculum_id': int(selected_curriculum) if selected_curriculum.isdigit() else '',
        'selected_lesson_id': int(selected_lesson) if selected_lesson.isdigit() else '',
        'leaderboard': leaderboard,
        'top_3': top_3,
        'selected_game': selected_game,
        'selected_game_name': selected_game_name,
        'personal_best': personal_best,
        'user_rank': user_rank,
        'active_tab': active_tab,
        'highest_hsk': highest_hsk,
    }
    return render(request, 'courses/dashboard.html', context)

@login_required
def profile_view(request):
    if request.method == 'POST':
        display_name = request.POST.get('display_name', '').strip()
        if display_name:
            request.user.first_name = display_name
            request.user.save()
            return redirect('profile')

    try:
        recent_history = GameHistory.objects.filter(user=request.user).order_by('-id')[:10]
    except Exception:
        recent_history = []

    best_quiz_1 = GameHistory.objects.filter(user=request.user, game_type='quiz_1').aggregate(Min('time_taken'))['time_taken__min']
    best_quiz_2 = GameHistory.objects.filter(user=request.user, game_type='quiz_2').aggregate(Min('time_taken'))['time_taken__min']
    best_quiz_3 = GameHistory.objects.filter(user=request.user, game_type='quiz_3').aggregate(Min('time_taken'))['time_taken__min']
    best_quiz_4 = GameHistory.objects.filter(user=request.user, game_type='quiz_4').aggregate(Min('time_taken'))['time_taken__min']

    highest_hsk = 0
    passed_exams = ExamResult.objects.filter(user=request.user, score__gte=120)
    if passed_exams.exists():
        highest_hsk = passed_exams.aggregate(Max('exam__hsk_level'))['exam__hsk_level__max']

    context = {
        'recent_history': recent_history,
        'best_quiz_1': best_quiz_1,
        'best_quiz_2': best_quiz_2,
        'best_quiz_3': best_quiz_3,
        'best_quiz_4': best_quiz_4,
        'highest_hsk': highest_hsk,
    }
    
    return render(request, 'courses/profile.html', context)

# ==========================================
# 5. WEBHOOK GITHUB 
# ==========================================
@csrf_exempt
def github_webhook(request):
    if request.method == 'POST':
        subprocess.call(['git', 'pull'], cwd='/home/khoadoct95/tieng-trung-bich-tuyen')
        wsgi_file = '/var/www/khoadoct95_pythonanywhere_com_wsgi.py'
        os.utime(wsgi_file, None)
        return HttpResponse('Cập nhật thành công!', status=200)
    return HttpResponse('Chỉ nhận lệnh POST', status=405)

# ==========================================
# 6. LÀM BÀI THI CẬP NHẬT CHẤM ĐIỂM CHUẨN
# ==========================================
@login_required(login_url='login')
def take_exam(request, exam_id):
    exam = get_object_or_404(Exam, id=exam_id)
    questions = ExamQuestion.objects.filter(exam=exam).order_by('question_number')
    total_questions = questions.count()

    if request.method == 'POST':
        total_correct = 0
        user_answers_dict = {}

        # Chấm điểm chi tiết từng câu
        for q in questions:
            submitted_answer = request.POST.get(f'q_{q.id}', '').strip().upper()
            user_answers_dict[str(q.id)] = submitted_answer 
            
            correct_ans = str(q.correct_answer).strip().upper()
            if submitted_answer and submitted_answer == correct_ans:
                total_correct += 1

        # CÔNG THỨC CHẤM ĐIỂM TƯƠNG ĐỐI
        # HSK 1,2 quy chuẩn 200 điểm tối đa. Nếu số câu khác, chia tỷ lệ.
        score_per_question = 200 / total_questions if total_questions > 0 else 0
        score = int(total_correct * score_per_question)

        result = ExamResult.objects.create(
            user=request.user,
            exam=exam,
            score=score,
            total_correct=total_correct,
            total_questions=total_questions,
            user_answers=user_answers_dict,
            time_spent=0 # Có thể dùng JS lưu thời gian thực tế sau
        )

        messages.success(request, "🎉 Chúc mừng bạn đã hoàn thành bài thi!")
        return redirect('exam_result', result_id=result.id)

    personal_best = ExamResult.objects.filter(exam=exam, user=request.user).aggregate(Max('score'))['score__max']
    global_best = ExamResult.objects.filter(exam=exam).aggregate(Max('score'))['score__max']

    context = {
        'exam': exam, 
        'questions': questions,
        'personal_best': personal_best if personal_best is not None else "--",
        'global_best': global_best if global_best is not None else "--"
    }

    # Phân luồng Template dựa trên HSK Level
    if exam.hsk_level == 1:
        if exam.exam_type == 'old':
            return render(request, 'courses/take_exam_hsk1_old.html', context)
        else:
            return render(request, 'courses/take_exam_hsk1_new.html', context)
    elif exam.hsk_level == 2:
        # Template mới dành riêng cho HSK 2
        return render(request, 'courses/take_exam_hsk2_new.html', context)
            
    return render(request, 'courses/take_exam_hsk1_new.html', context)

# ==========================================
# 7. XEM LẠI CHI TIẾT BÀI LÀM (REVIEW)
# ==========================================
@login_required(login_url='login')
def review_exam(request, result_id):
    # NÂNG CẤP BẢO MẬT: Nếu là Admin/Giáo viên thì được xem tất cả. Nếu là Học viên thì chỉ xem được bài của mình.
    if request.user.is_staff or request.user.is_superuser:
        result = get_object_or_404(ExamResult, id=result_id)
    else:
        result = get_object_or_404(ExamResult, id=result_id, user=request.user)
        
    exam = result.exam
    questions = ExamQuestion.objects.filter(exam=exam).order_by('question_number')

    # Trích xuất và so sánh đáp án của từng câu từ DB
    for q in questions:
        raw_user = result.user_answers.get(str(q.id), '')
        q.user_ans = str(raw_user).strip().upper() if raw_user else ''
        
        raw_correct = q.correct_answer
        q.correct_ans = str(raw_correct).strip().upper() if raw_correct else ''
        
        q.is_correct = (q.user_ans == q.correct_ans and q.user_ans != '')

    return render(request, 'courses/review_exam.html', {
        'exam': exam,
        'questions': questions,
        'result': result
    })

# ==========================================
# 8. KẾT QUẢ VÀ DANH SÁCH BÀI THI
# ==========================================
@login_required(login_url='login')
def exam_result(request, result_id):
    result = get_object_or_404(ExamResult, id=result_id, user=request.user)
    
    # Tính tỷ lệ phần trăm
    total = result.total_questions
    percentage = int((result.total_correct / total) * 100) if total > 0 else 0
    is_passed = result.score >= 120

    return render(request, 'courses/exam_result.html', {
        'result': result,
        'total_questions': total,
        'percentage': percentage,
        'is_passed': is_passed
    })

def exam_list(request):
    search_query = request.GET.get('q', '').strip()
    level_filter = request.GET.get('level', '')
    exams = Exam.objects.all().order_by('-id')

    if search_query:
        exams = exams.filter(title__icontains=search_query)
    if level_filter.isdigit():
        exams = exams.filter(hsk_level=int(level_filter))

    context = {
        'search_query': search_query,
        'level_filter': level_filter
    }

    if request.user.is_authenticated:
        exams = exams.annotate(
            user_max_score=Max('examresult__score', filter=Q(examresult__user=request.user))
        )
        
        user_results = ExamResult.objects.filter(user=request.user).order_by('-completed_at')
        total_exams = user_results.count()
        passed_exams = user_results.filter(score__gte=120).count()
        
        context['total_exams'] = total_exams
        context['passed_exams'] = passed_exams
        context['recent_results'] = user_results[:5]

        highest_scores = {}
        for level in range(1, 7):
            max_score = user_results.filter(exam__hsk_level=level).aggregate(Max('score'))['score__max']
            if max_score is not None:
                highest_scores[level] = max_score
        context['highest_scores_by_level'] = highest_scores

        badges = []
        if total_exams >= 1:
            badges.append({'name': 'Tân binh chăm chỉ', 'icon': 'fa-seedling', 'color': '#10B981', 'desc': 'Hoàn thành bài thi đầu tiên'})
        if passed_exams >= 3:
            badges.append({'name': 'Bậc thầy HSK', 'icon': 'fa-graduation-cap', 'color': '#8B5CF6', 'desc': 'Thi đỗ từ 3 bài trở lên'})
            
        has_perfect_score = user_results.filter(score=200).exists()
        if has_perfect_score:
            badges.append({'name': 'Vua điểm tuyệt đối', 'icon': 'fa-crown', 'color': '#F59E0B', 'desc': 'Đạt điểm tối đa 200/200'})
        elif user_results.filter(score__gte=180).exists():
            badges.append({'name': 'Cao thủ Hán ngữ', 'icon': 'fa-fire', 'color': '#EF4444', 'desc': 'Đạt trên 180 điểm'})
        context['badges'] = badges

        chrono_results = ExamResult.objects.filter(user=request.user).order_by('completed_at')
        chart_data = {}
        for res in chrono_results:
            lvl = f"HSK {res.exam.hsk_level}"
            if lvl not in chart_data:
                chart_data[lvl] = {'labels': [], 'scores': []}
            
            attempt_num = len(chart_data[lvl]['labels']) + 1
            chart_data[lvl]['labels'].append(f"Lần {attempt_num}")
            chart_data[lvl]['scores'].append(res.score)
            
        context['chart_data_json'] = json.dumps(chart_data)

    context['exams'] = exams 
    return render(request, 'courses/exam_list.html', context)

@login_required(login_url='login')
def student_dashboard(request):
    user_results = ExamResult.objects.filter(user=request.user).order_by('-completed_at')
    total_exams = user_results.count()
    highest_score = user_results.aggregate(Max('score'))['score__max'] or 0
    passed_exams = user_results.filter(score__gte=120).count()
    
    context = {
        'results': user_results,
        'total_exams': total_exams,
        'highest_score': highest_score,
        'passed_exams': passed_exams,
    }
    return render(request, 'courses/dashboard.html', context)

# ==========================================
# HÀM HỖ TRỢ XỬ LÝ FILE ZIP ẢNH DÙNG CHUNG
# ==========================================
def process_exam_zip_helper(exam, zip_file):
    image_groups = {}
    single_images = {}
    processed_groups = []
    single_count = 0

    with zipfile.ZipFile(zip_file, 'r') as z:
        for filename in z.namelist():
            if filename.lower().endswith(('.png', '.jpg', '.jpeg')):
                if '__MACOSX' in filename or filename.startswith('.'):
                    continue
                clean_name = filename.split('/')[-1]

                match_group = re.match(r'^q(\d+)_([A-F])\.(png|jpg|jpeg)$', clean_name, re.IGNORECASE)
                if match_group:
                    q_num = match_group.group(1)
                    letter = match_group.group(2).upper()
                    if q_num not in image_groups:
                        image_groups[q_num] = {}
                    image_groups[q_num][letter] = z.read(filename)
                    continue

                match_single = re.match(r'^q(\d+)\.(png|jpg|jpeg)$', clean_name, re.IGNORECASE)
                if match_single:
                    q_num = match_single.group(1)
                    single_images[q_num] = z.read(filename)

    # 1. Lưu ảnh đơn
    for q_num, file_data in single_images.items():
        question = ExamQuestion.objects.filter(exam=exam, question_number=int(q_num)).first()
        if question:
            question.image.save(f'q{q_num}_{exam.id}.jpg', ContentFile(file_data), save=True)
            single_count += 1

    # 2. Ghép ảnh rổ chung (3 ảnh A-C hoặc 5-6 ảnh A-F)
    for q_num, letters_dict in image_groups.items():
        question = ExamQuestion.objects.filter(exam=exam, question_number=int(q_num)).first()
        if not question:
            if int(q_num) in range(6, 11): question = ExamQuestion.objects.filter(exam=exam, question_number=6).first()
            elif int(q_num) in range(11, 16): question = ExamQuestion.objects.filter(exam=exam, question_number=11).first()
            elif int(q_num) in range(26, 31): question = ExamQuestion.objects.filter(exam=exam, question_number=26).first()
            elif int(q_num) in range(51, 56): question = ExamQuestion.objects.filter(exam=exam, question_number=51).first()

        if not question:
            continue

        keys = list(letters_dict.keys())
        if not keys:
            continue

        imgs = {}
        for k in keys:
            try:
                imgs[k] = Image.open(BytesIO(letters_dict[k])).convert('RGB')
            except Exception:
                pass

        if not imgs:
            continue

        base_k = list(imgs.keys())[0]
        w, h = imgs[base_k].size
        for k in imgs:
            imgs[k] = imgs[k].resize((w, h))

        if set(keys).issubset({'A', 'B', 'C'}) and len(keys) <= 3:
            composite = Image.new('RGB', (w * 3, h), (255, 255, 255))
            if 'A' in imgs: composite.paste(imgs['A'], (0, 0))
            if 'B' in imgs: composite.paste(imgs['B'], (w, 0))
            if 'C' in imgs: composite.paste(imgs['C'], (w * 2, 0))
        else:
            composite = Image.new('RGB', (w * 2, h * 3), (255, 255, 255))
            positions = {
                'A': (0, 0),       'B': (w, 0),
                'C': (0, h),       'D': (w, h),
                'E': (0, h * 2),   'F': (w, h * 2)
            }
            for k, pos in positions.items():
                if k in imgs:
                    composite.paste(imgs[k], pos)

        img_io = BytesIO()
        composite.save(img_io, format='JPEG', quality=90)
        question.image.save(f'q{q_num}_composite_{exam.id}.jpg', ContentFile(img_io.getvalue()), save=True)
        processed_groups.append(str(q_num))

    return processed_groups, single_count


# ==========================================
# 9. UPLOAD / CẬP NHẬT ĐỀ THI ALL-IN-ONE (EXCEL + AUDIO + ZIP)
# ==========================================
@login_required
def import_excel(request):
    if request.method == 'POST':
        existing_exam_id = request.POST.get('existing_exam_id', '').strip()
        exam_type_form = request.POST.get('exam_type', 'new').strip()
        exam_title_form = request.POST.get('exam_title', '').strip()
        hsk_level_form = int(request.POST.get('hsk_level', 1))
        duration_form = int(request.POST.get('duration', 40))

        excel_file = request.FILES.get('excel_file')
        audio_file = request.FILES.get('listening_audio')
        zip_file = request.FILES.get('zip_file')

        if not excel_file and not audio_file and not zip_file and not existing_exam_id:
            messages.error(request, "⚠️ Vui lòng tải lên ít nhất 1 file (Excel, Audio hoặc ZIP)!")
            return redirect(request.path)

        # 1. TÌM ĐỀ THI CŨ ĐỂ GHI ĐÈ HOẶC TẠO MỚI
        exam = None
        is_updated = False

        if existing_exam_id.isdigit():
            exam = Exam.objects.filter(id=int(existing_exam_id)).first()
            if exam:
                is_updated = True

        if not exam and exam_title_form:
            exam = Exam.objects.filter(title__iexact=exam_title_form, hsk_level=hsk_level_form).first()
            if exam:
                is_updated = True

        if exam:
            if exam_title_form:
                exam.title = exam_title_form
            exam.hsk_level = hsk_level_form
            exam.duration_minutes = duration_form
            if hasattr(exam, 'exam_type'):
                exam.exam_type = exam_type_form
            exam.save()
        else:
            create_kwargs = {
                'title': exam_title_form or 'Đề thi HSK',
                'hsk_level': hsk_level_form,
                'duration_minutes': duration_form,
            }
            if hasattr(Exam, 'exam_type'):
                create_kwargs['exam_type'] = exam_type_form
            exam = Exam.objects.create(**create_kwargs)

        status_notes = []

        # 2. XỬ LÝ FILE EXCEL (CẬP NHẬT ĐÈ TỪNG CÂU, GIỮ NGUYÊN ẢNH CŨ)
        if excel_file:
            try:
                df = pd.read_excel(excel_file).fillna('')
                if len(df.columns) < 14:
                    messages.error(request, "❌ File Excel không đủ 14 cột chuẩn! Vui lòng kiểm tra lại.")
                    if not is_updated:
                        exam.delete()
                    return redirect(request.path)

                q_count = 0
                for index, row in df.iterrows():
                    raw_q_num = str(row.iloc[0]).strip()
                    if not raw_q_num:
                        continue
                    q_num_int = int(float(raw_q_num))

                    ExamQuestion.objects.update_or_create(
                        exam=exam,
                        question_number=q_num_int,
                        defaults={
                            'section_type': str(row.iloc[1]).strip(),
                            'question_group': str(row.iloc[2]).strip(),
                            'passage_text': str(row.iloc[3]).strip(),
                            'passage_pinyin': str(row.iloc[4]).strip(),
                            'content': str(row.iloc[5]).strip(),
                            'content_pinyin': str(row.iloc[6]).strip(),
                            'option_a': str(row.iloc[7]).strip(),
                            'option_a_pinyin': str(row.iloc[8]).strip(),
                            'option_b': str(row.iloc[9]).strip(),
                            'option_b_pinyin': str(row.iloc[10]).strip(),
                            'option_c': str(row.iloc[11]).strip(),
                            'option_c_pinyin': str(row.iloc[12]).strip(),
                            'correct_answer': str(row.iloc[13]).strip().upper(),
                        }
                    )
                    q_count += 1
                status_notes.append(f"{'Cập nhật đè' if is_updated else 'Tạo mới'} {q_count} câu hỏi Excel")
            except Exception as e:
                messages.error(request, f"❌ Lỗi khi đọc file Excel: {str(e)}")
                return redirect(request.path)

        # 3. XỬ LÝ FILE AUDIO (NẾU CÓ)
        if audio_file:
            exam.listening_audio = audio_file
            exam.save()
            status_notes.append("Đã gắn file nghe Audio")

        # 4. XỬ LÝ FILE ZIP ẢNH (NẾU CÓ)
        if zip_file:
            try:
                groups, singles = process_exam_zip_helper(exam, zip_file)
                zip_msg = []
                if groups:
                    zip_msg.append(f"ghép rổ ảnh câu {', '.join(groups)}")
                if singles:
                    zip_msg.append(f"gắn {singles} ảnh đơn")
                status_notes.append("ZIP: " + (", ".join(zip_msg) if zip_msg else "không tìm thấy ảnh hợp lệ"))
            except Exception as e:
                messages.error(request, f"⚠️ Lỗi khi xử lý file ZIP ảnh: {str(e)}")

        summary = " | ".join(status_notes) if status_notes else "Đã cập nhật thông tin đề thi"
        messages.success(request, f"🎉 Hoàn tất [{exam.title}]: {summary}!")

        if request.path.startswith('/admin'):
            return redirect('/admin/courses/exam/')
        return redirect('exam_list')

    exams = Exam.objects.all().order_by('-id')
    return render(request, 'admin/import_excel.html', {'exams': exams})

# ==========================================
# 10. UPLOAD ZIP GHÉP ẢNH HÀNG LOẠT (BẢN BAO LỖI)
# ==========================================
@login_required
def upload_exam_images_zip(request):
    if request.method == 'POST':
        exam_id = request.POST.get('exam_id')
        zip_file = request.FILES.get('zip_file')
        
        if not exam_id or not zip_file:
            messages.error(request, "Vui lòng chọn đề thi và file ZIP.")
            return redirect('upload_exam_images_zip')
            
        exam = get_object_or_404(Exam, id=exam_id)
        image_groups = {}
        single_images = {}
        processed_groups = [] # Lưu danh sách các nhóm đã ghép thành công

        try:
            with zipfile.ZipFile(zip_file, 'r') as z:
                for filename in z.namelist():
                    if filename.lower().endswith(('.png', '.jpg', '.jpeg')):
                        if '__MACOSX' in filename or filename.startswith('.'):
                            continue
                            
                        clean_name = filename.split('/')[-1]
                        
                        match_group = re.match(r'^q(\d+)_([A-F])\.(png|jpg|jpeg)$', clean_name, re.IGNORECASE)
                        if match_group:
                            q_num = match_group.group(1)
                            letter = match_group.group(2).upper()
                            if q_num not in image_groups:
                                image_groups[q_num] = {}
                            image_groups[q_num][letter] = z.read(filename)
                            continue
                            
                        match_single = re.match(r'^q(\d+)\.(png|jpg|jpeg)$', clean_name, re.IGNORECASE)
                        if match_single:
                            q_num = match_single.group(1)
                            single_images[q_num] = z.read(filename)

            # 1. Xử lý ảnh lẻ
            for q_num, file_data in single_images.items():
                question = ExamQuestion.objects.filter(exam=exam, question_number=int(q_num)).first()
                if question:
                    question.image.save(f'q{q_num}_{exam.id}.jpg', ContentFile(file_data), save=True)

            # 2. Xử lý ghép ảnh rổ chung (BAO LỖI, THIẾU ẢNH VẪN GHÉP)
            for q_num, letters_dict in image_groups.items():
                question = ExamQuestion.objects.filter(exam=exam, question_number=int(q_num)).first()
                
                # Fallback: Nếu không tìm thấy, đưa về câu đầu tiên của nhóm
                if not question:
                    if int(q_num) in range(6, 11): question = ExamQuestion.objects.filter(exam=exam, question_number=6).first()
                    elif int(q_num) in range(11, 16): question = ExamQuestion.objects.filter(exam=exam, question_number=11).first()
                    elif int(q_num) in range(26, 31): question = ExamQuestion.objects.filter(exam=exam, question_number=26).first()
                    elif int(q_num) in range(51, 56): question = ExamQuestion.objects.filter(exam=exam, question_number=51).first()

                if not question:
                    continue

                # Lấy danh sách các chữ cái có trong zip
                keys = list(letters_dict.keys())
                if not keys: continue

                # Đọc các ảnh vào bộ nhớ
                imgs = {}
                for k in keys:
                    try:
                        imgs[k] = Image.open(BytesIO(letters_dict[k])).convert('RGB')
                    except:
                        pass
                
                if not imgs: continue
                
                # Lấy kích thước chuẩn từ ảnh đầu tiên tìm thấy
                base_k = list(imgs.keys())[0]
                w, h = imgs[base_k].size
                for k in imgs:
                    imgs[k] = imgs[k].resize((w, h))

                # Phân loại ghép 3 ảnh hay 6 ảnh
                if set(keys).issubset({'A', 'B', 'C'}) and len(keys) <= 3:
                    # Rổ 3 ảnh (A, B, C nằm ngang)
                    composite = Image.new('RGB', (w * 3, h), (255, 255, 255))
                    if 'A' in imgs: composite.paste(imgs['A'], (0, 0))
                    if 'B' in imgs: composite.paste(imgs['B'], (w, 0))
                    if 'C' in imgs: composite.paste(imgs['C'], (w * 2, 0))
                else:
                    # Rổ 6 ảnh (A,B / C,D / E,F)
                    composite = Image.new('RGB', (w * 2, h * 3), (255, 255, 255))
                    positions = {
                        'A': (0, 0),       'B': (w, 0),
                        'C': (0, h),       'D': (w, h),
                        'E': (0, h * 2),   'F': (w, h * 2)
                    }
                    for k, pos in positions.items():
                        if k in imgs:
                            composite.paste(imgs[k], pos)

                # Lưu vào Database
                img_io = BytesIO()
                composite.save(img_io, format='JPEG', quality=90)
                question.image.save(f'q{q_num}_composite_{exam.id}.jpg', ContentFile(img_io.getvalue()), save=True)
                processed_groups.append(str(q_num)) # Ghi nhận thành công

            if processed_groups:
                messages.success(request, f"🎉 Đã ghép ảnh thành công cho các nhóm câu: {', '.join(processed_groups)}")
            else:
                messages.warning(request, "⚠️ File ZIP hợp lệ nhưng không tìm thấy ảnh nào đúng chuẩn tên (vd: q11_a.jpg)")
            
            return redirect('exam_list')
            
        except Exception as e:
            messages.error(request, f"Lỗi xử lý file ZIP: {str(e)}")
            return redirect('upload_exam_images_zip')

    exams = Exam.objects.all().order_by('-id')
    return render(request, 'admin/upload_zip.html', {'exams': exams})


# ==========================================
# 11. KHU VỰC GIẢI TRÍ (GÓC GAME MỚI)
# ==========================================
@login_required
def game_shooter_view(request):
    curriculums = Curriculum.objects.all()
    lessons = Lesson.objects.all().order_by('curriculum', 'order')
    
    curriculums_data = []
    for c in curriculums:
        count = Vocabulary.objects.filter(level=c.title).count()
        curriculums_data.append({
            'title': c.title,
            'vocab_count': count
        })
        
    lessons_data = []
    for l in lessons:
        count = l.vocabularies.count()
        lessons_data.append({
            'id': l.id,
            'curriculum_title': l.curriculum.title,
            'order': l.order,
            'vocab_count': count
        })
    
    context = {
        'curriculums_data': curriculums_data,
        'lessons_data': lessons_data
    }
    return render(request, 'games/shooter.html', context)


@login_required
def api_get_vocab_for_game(request):
    level = request.GET.get('level')
    lesson_id = request.GET.get('lesson_id')
    
    if lesson_id:
        vocabs = Vocabulary.objects.filter(lesson_id=lesson_id)
    elif level:
        vocabs = Vocabulary.objects.filter(level=level)
    else:
        vocabs = Vocabulary.objects.none()

    vocab_list = list(vocabs.values('hanzi', 'pinyin', 'meaning'))
    random.shuffle(vocab_list)
    
    return JsonResponse({'vocabularies': vocab_list})


@login_required
def api_save_game_record(request):
    if request.method == 'POST':
        data = json.loads(request.body)
        score = data.get('score', 0)
        time_taken = data.get('time_taken', 0)
        level = data.get('level', '')
        lesson_id = data.get('lesson_id', '')
        game_type = data.get('game_type', 'shooter')

        lesson_obj = None
        if lesson_id:
            lesson_obj = Lesson.objects.filter(id=lesson_id).first()
        
        if score > 0:
            GameHistory.objects.create(
                user=request.user,
                game_type=game_type,  
                score=score,
                time_taken=time_taken,
                level=level,
                lesson=lesson_obj
            )
        
        if lesson_obj:
            top_record = GameHistory.objects.filter(game_type=game_type, lesson=lesson_obj).order_by('-score', 'time_taken').first()
        else:
            top_record = GameHistory.objects.filter(game_type=game_type, level=level).order_by('-score', 'time_taken').first()
        
        if top_record:
            top_scorer = top_record.user.first_name if top_record.user.first_name else top_record.user.username
        else:
            top_scorer = "Chưa có"

        top_score = top_record.score if top_record else 0
        top_time = top_record.time_taken if top_record else 0

        return JsonResponse({
            'status': 'success', 
            'top_scorer': top_scorer,
            'top_score': top_score,
            'top_time': top_time
        })
        
    return JsonResponse({'status': 'error'}, status=400)


@login_required
def game_panda_view(request):
    curriculums = Curriculum.objects.all()
    lessons = Lesson.objects.all().order_by('curriculum', 'order')
    
    curriculums_data = []
    for c in curriculums:
        count = Vocabulary.objects.filter(level=c.title).count()
        curriculums_data.append({'title': c.title, 'vocab_count': count})
        
    lessons_data = []
    for l in lessons:
        count = l.vocabularies.count()
        lessons_data.append({
            'id': l.id,
            'curriculum_title': l.curriculum.title,
            'order': l.order,
            'vocab_count': count
        })
    
    context = {
        'curriculums_data': curriculums_data,
        'lessons_data': lessons_data
    }
    return render(request, 'games/panda.html', context)