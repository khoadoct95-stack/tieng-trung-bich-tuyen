from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.db.models import Min
from .models import GameHistory, Lesson
# (Nếu bạn có các import khác ở trên cùng thì cứ giữ lại nhé)

@login_required
def dashboard_view(request):
    # 1. Xử lý Bảng xếp hạng
    selected_game = request.GET.get('game', 'quiz_1')
    game_names = {'quiz_1': 'Nối từ', 'quiz_2': 'Lật thẻ', 'quiz_3': 'Viết chữ', 'quiz_4': 'Phát âm'}
    selected_game_name = game_names.get(selected_game, 'Nối từ')
    
    # Lấy danh sách Top 100 (Đã có lesson__id để làm link chuyển hướng)
    leaderboard_query = GameHistory.objects.filter(game_type=selected_game)\
        .values('user__username', 'user__first_name', 'lesson__id', 'lesson__title_vietnamese')\
        .annotate(best_time=Min('time_taken'))\
        .order_by('best_time')
        
    leaderboard = list(leaderboard_query[:100])
    top_3 = leaderboard[:3] # Lấy riêng Top 3
    
    # 2. Tính toán thứ hạng và thành tích của chính User
    user_rank = None
    personal_best = None
    
    for index, entry in enumerate(leaderboard):
        if entry['user__username'] == request.user.username:
            user_rank = index + 1
            personal_best = entry['best_time']
            break
            
    # Nếu không lọt Top 100 nhưng đã từng chơi
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