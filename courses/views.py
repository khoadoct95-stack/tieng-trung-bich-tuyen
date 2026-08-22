import os
import json
import subprocess
import pandas as pd
import zipfile
import re
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
from django.db.models import Min
from django.views.decorators.csrf import csrf_exempt
from django.contrib import messages
from .models import Curriculum, Lesson, Vocabulary, GameHistory
from .models import Exam, ExamQuestion, ExamResult
from django.db.models import Max, Q

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
# 4. BẢNG XẾP HẠNG & HỒ SƠ CÁ NHÂN
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

    highest_hsk = 0
    passed_exams = ExamResult.objects.filter(user=request.user, score__gte=120)
    if passed_exams.exists():
        highest_hsk = passed_exams.aggregate(Max('exam__hsk_level'))['exam__hsk_level__max']

    context['highest_hsk'] = highest_hsk
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
        project_dir = '/home/xuehanyu/tieng-trung-bich-tuyen'
        wsgi_file = '/var/www/xuehanyu_pythonanywhere_com_wsgi.py'
        try:
            subprocess.run(['git', 'fetch', '--all'], cwd=project_dir, check=True)
            subprocess.run(['git', 'reset', '--hard', 'origin/main'], cwd=project_dir, check=True)
            subprocess.run(['touch', wsgi_file], check=True)
            return HttpResponse("Updated code successfully")
        except subprocess.CalledProcessError as e:
            return HttpResponse(f"Error: {str(e)}", status=500)
    return HttpResponse("Invalid request", status=400)

# ==========================================
# 6. LÀM BÀI THI & TRẠM PHÂN LUỒNG TEMPLATE
# ==========================================
@login_required(login_url='login')
def take_exam(request, exam_id):
    exam = get_object_or_404(Exam, id=exam_id)
    questions = ExamQuestion.objects.filter(exam=exam).order_by('question_number')

    if request.method == 'POST':
        total_correct = 0
        user_answers_dict = {}

        for q in questions:
            submitted_answer = request.POST.get(f'q_{q.id}', '').strip().upper()
            user_answers_dict[str(q.id)] = submitted_answer 
            
            correct_ans = str(q.correct_answer).strip().upper()
            if submitted_answer and submitted_answer == correct_ans:
                total_correct += 1

        score = total_correct * 5

        result = ExamResult.objects.create(
            user=request.user,
            exam=exam,
            score=score,
            total_correct=total_correct,
            user_answers=user_answers_dict,
            time_spent=0
        )

        messages.success(request, "🎉 Chúc mừng bạn đã hoàn thành bài thi!")
        return redirect('exam_result', result_id=result.id)

    context = {
        'exam': exam, 
        'questions': questions
    }

    if exam.hsk_level == 1:
        if exam.exam_type == 'old':
            return render(request, 'courses/take_exam_hsk1_old.html', context)
        else:
            return render(request, 'courses/take_exam_hsk1_new.html', context)
            
    elif exam.hsk_level == 2:
        if exam.exam_type == 'old':
            return render(request, 'courses/take_exam_hsk2_old.html', context)
        else:
            return render(request, 'courses/take_exam_hsk2_new.html', context)
            
    elif exam.hsk_level == 3:
        if exam.exam_type == 'old':
            return render(request, 'courses/take_exam_hsk3_old.html', context)
        else:
            return render(request, 'courses/take_exam_hsk3_new.html', context)

    return render(request, 'courses/take_exam_hsk1_new.html', context)

# ==========================================
# 7. XEM LẠI CHI TIẾT BÀI LÀM
# ==========================================
@login_required(login_url='login')
def review_exam(request, result_id):
    result = get_object_or_404(ExamResult, id=result_id, user=request.user)
    exam = result.exam
    questions = ExamQuestion.objects.filter(exam=exam).order_by('question_number')

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
    
    total_questions = ExamQuestion.objects.filter(exam=result.exam).count()
    percentage = int((result.total_correct / total_questions) * 100) if total_questions > 0 else 0
    
    is_passed = result.score >= 120

    return render(request, 'courses/exam_result.html', {
        'result': result,
        'total_questions': total_questions,
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
# 9. UPLOAD ĐỀ THI (IMPORT EXCEL) - BẢN ĐỌC THEO VỊ TRÍ
# ==========================================
@login_required
def import_excel(request):
    if request.method == 'POST' and request.FILES.get('excel_file'):
        excel_file = request.FILES['excel_file']
        
        exam_type_form = request.POST.get('exam_type', 'new')
        exam_title_form = request.POST.get('exam_title', 'Đề thi HSK')
        hsk_level_form = request.POST.get('hsk_level', 1)
        duration_form = request.POST.get('duration', 40)
        
        exam = Exam.objects.create(
            title=exam_title_form, 
            hsk_level=hsk_level_form,
            duration_minutes=duration_form,
            exam_type=exam_type_form 
        )
        
        # Đọc file Excel và lấp đầy ô trống
        df = pd.read_excel(excel_file).fillna('')
        
        # Đảm bảo file có ít nhất 14 cột để không bị lỗi
        if len(df.columns) < 14:
            messages.error(request, "❌ File Excel của bạn không đủ 14 cột chuẩn! Vui lòng kiểm tra lại.")
            exam.delete()
            return redirect('import_excel')
        
        for index, row in df.iterrows():
            # Bỏ qua nếu dòng đó trống (không có số thứ tự)
            if str(row.iloc[0]).strip() == '':
                continue
                
            try:
                ExamQuestion.objects.create(
                    exam=exam,
                    question_number=row.iloc[0],              # Cột 1 (Vị trí 0)
                    section_type=str(row.iloc[1]).strip(),    # Cột 2
                    group_name=str(row.iloc[2]).strip(),      # Cột 3
                    passage_text=str(row.iloc[3]).strip(),    # Cột 4
                    passage_pinyin=str(row.iloc[4]).strip(),  # Cột 5
                    content=str(row.iloc[5]).strip(),         # Cột 6
                    content_pinyin=str(row.iloc[6]).strip(),  # Cột 7
                    option_a=str(row.iloc[7]).strip(),        # Cột 8
                    option_pinyin_a=str(row.iloc[8]).strip(), # Cột 9
                    option_b=str(row.iloc[9]).strip(),        # Cột 10
                    option_pinyin_b=str(row.iloc[10]).strip(),# Cột 11
                    option_c=str(row.iloc[11]).strip(),       # Cột 12
                    option_pinyin_c=str(row.iloc[12]).strip(),# Cột 13
                    correct_answer=str(row.iloc[13]).strip().upper() # Cột 14
                )
            except Exception as e:
                # Nếu có dòng nào bị lỗi, báo ngay ra màn hình để biết đường sửa
                messages.error(request, f"❌ Lỗi ở dòng {index + 2} trong Excel: {str(e)}")
                exam.delete() # Xóa đề thi vừa tạo dở dang
                return redirect('import_excel')
            
        messages.success(request, f"🎉 Đã Import thành công: {exam_title_form}!")
        return redirect('exam_list')
    
    return render(request, 'admin/import_excel.html')

# ==========================================
# 10. UPLOAD ZIP GHÉP ẢNH HÀNG LOẠT
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

        try:
            with zipfile.ZipFile(zip_file, 'r') as z:
                for filename in z.namelist():
                    if filename.lower().endswith(('.png', '.jpg', '.jpeg')):
                        # Bỏ qua các file ẩn của Mac/Windows
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

                # Lưu ảnh đơn
                for q_num, file_data in single_images.items():
                    question = ExamQuestion.objects.filter(exam=exam, question_number=int(q_num)).first()
                    if question:
                        question.image.save(f'q{q_num}_{exam.id}.jpg', ContentFile(file_data), save=True)

                # Tự động ghép ảnh nhóm
                for q_num, letters_dict in image_groups.items():
                    question = ExamQuestion.objects.filter(exam=exam, question_number=int(q_num)).first()
                    if not question:
                        continue

                    if 'A' in letters_dict and 'B' in letters_dict and 'C' in letters_dict and 'D' not in letters_dict:
                        imgA = Image.open(BytesIO(letters_dict['A'])).convert('RGB')
                        imgB = Image.open(BytesIO(letters_dict['B'])).convert('RGB')
                        imgC = Image.open(BytesIO(letters_dict['C'])).convert('RGB')
                        
                        w, h = imgA.size
                        imgB = imgB.resize((w, h))
                        imgC = imgC.resize((w, h))
                        
                        composite = Image.new('RGB', (w * 3, h), (255, 255, 255))
                        composite.paste(imgA, (0, 0))
                        composite.paste(imgB, (w, 0))
                        composite.paste(imgC, (w * 2, 0))
                        
                        img_io = BytesIO()
                        composite.save(img_io, format='JPEG', quality=90)
                        question.image.save(f'q{q_num}_composite_{exam.id}.jpg', ContentFile(img_io.getvalue()), save=True)

                    elif all(k in letters_dict for k in ['A', 'B', 'C', 'D', 'E', 'F']):
                        imgs = {k: Image.open(BytesIO(letters_dict[k])).convert('RGB') for k in ['A','B','C','D','E','F']}
                        w, h = imgs['A'].size
                        for k in imgs:
                            imgs[k] = imgs[k].resize((w, h))
                            
                        composite = Image.new('RGB', (w * 2, h * 3), (255, 255, 255))
                        composite.paste(imgs['A'], (0, 0))
                        composite.paste(imgs['B'], (w, 0))
                        composite.paste(imgs['C'], (0, h))
                        composite.paste(imgs['D'], (w, h))
                        composite.paste(imgs['E'], (0, h * 2))
                        composite.paste(imgs['F'], (w, h * 2))
                        
                        img_io = BytesIO()
                        composite.save(img_io, format='JPEG', quality=90)
                        question.image.save(f'q{q_num}_composite_{exam.id}.jpg', ContentFile(img_io.getvalue()), save=True)

            messages.success(request, "🎉 Đã gắn và tự động ghép ảnh thành công từ file ZIP!")
            return redirect('exam_list')
            
        except Exception as e:
            messages.error(request, f"Lỗi xử lý file ZIP: {str(e)}")
            return redirect('upload_exam_images_zip')

    exams = Exam.objects.all().order_by('-id')
    return render(request, 'admin/upload_zip.html', {'exams': exams})