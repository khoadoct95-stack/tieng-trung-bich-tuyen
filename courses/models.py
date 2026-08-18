from django.db import models

class Curriculum(models.Model):
    title = models.CharField(max_length=200, verbose_name="Tên giáo trình")
    description = models.TextField(blank=True, null=True, verbose_name="Mô tả")
    image = models.ImageField(upload_to='curriculum_images/', blank=True, null=True, verbose_name="Ảnh bìa")
    
    icon_character = models.CharField(
        max_length=5, 
        default='學', 
        verbose_name='Ký tự Ấn chương', 
        help_text='Nhập 1 chữ Hán (VD: 啓, 練, 達)'
    )
    subtitle = models.CharField(
        max_length=100, 
        default='GIÁO TRÌNH TIÊU CHUẨN', 
        verbose_name='Mục tiêu học tập',
        help_text='VD: NHẬP MÔN CƠ BẢN'
    )

    def __str__(self):
        return self.title

class Lesson(models.Model):
    curriculum = models.ForeignKey(Curriculum, on_delete=models.CASCADE, related_name='lessons')
    order = models.PositiveIntegerField(verbose_name="Số thứ tự bài")
    
    # --- TÁCH 3 TRƯỜNG TIÊU ĐỀ ---
    title_hanzi = models.CharField(max_length=200, verbose_name="Tiêu đề (Chữ Hán)", help_text="VD: AI小语,你好!")
    title_pinyin = models.CharField(max_length=200, verbose_name="Tiêu đề (Pinyin)", help_text="VD: AI Xiǎoyǔ, nǐ hǎo!", blank=True, null=True)
    title_vietnamese = models.CharField(max_length=200, verbose_name="Tiêu đề (Tiếng Việt)", help_text="VD: Xin chào AI Tiểu Ngữ!")
    
    description = models.TextField(blank=True, null=True, verbose_name="Mô tả ngắn")

    def __str__(self):
        return f"Bài {self.order}: {self.title_hanzi}"

class Vocabulary(models.Model):
    lesson = models.ForeignKey(Lesson, on_delete=models.CASCADE, related_name='vocabularies')
    hanzi = models.CharField(max_length=50, verbose_name="Chữ Hán")
    pinyin = models.CharField(max_length=100, verbose_name="Pinyin")
    meaning = models.CharField(max_length=200, verbose_name="Nghĩa Tiếng Việt")

    def __str__(self):
        return f"{self.hanzi} ({self.pinyin})"

from django.contrib.auth.models import User

# Bảng lưu Lịch sử làm bài và Điểm số
class GameHistory(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    lesson = models.ForeignKey(Lesson, on_delete=models.CASCADE)
    game_type = models.CharField(max_length=50) # Tên game: 'quiz_1', 'quiz_2'...
    time_taken = models.IntegerField(help_text="Thời gian hoàn thành (giây)")
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.username} - {self.game_type} - {self.time_taken}s"

    # ==========================================
# CẤU TRÚC ĐỀ THI HSK 3.0 (CÓ HỖ TRỢ PINYIN)
# ==========================================

class Exam(models.Model):
    title = models.CharField(max_length=255, verbose_name="Tên đề thi") 
    hsk_level = models.IntegerField(default=1, verbose_name="Cấp độ HSK") 
    duration_minutes = models.IntegerField(default=60, verbose_name="Thời gian làm bài (phút)")
    
    # 1 Đề thi chỉ có 1 file Audio chạy xuyên suốt
    listening_audio = models.FileField(upload_to='exam_audios/', blank=True, null=True, verbose_name="File Audio phần Nghe") 
    
    description = models.TextField(blank=True, null=True, verbose_name="Mô tả đề thi")
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title

class ExamQuestion(models.Model):
    exam = models.ForeignKey(Exam, on_delete=models.CASCADE, related_name='questions', verbose_name="Thuộc đề thi")
    question_number = models.IntegerField(verbose_name="Số thứ tự câu hỏi")
    section_type = models.CharField(max_length=50, choices=[('listening', 'Nghe hiểu'), ('reading', 'Đọc hiểu')], verbose_name="Phần thi")
    
    # Gom nhóm câu hỏi (Ví dụ: "1-5", "11-15") để Web tự động vẽ đường kẻ phân cách giao diện
    question_group = models.CharField(max_length=50, blank=True, null=True, verbose_name="Nhóm câu hỏi")

    # ================= KHU VỰC DÙNG CHUNG =================
    # Dùng cho các câu 11-15, 21-25 (Có chung 1 rổ 6 bức ảnh A-F)
    shared_image = models.ImageField(upload_to='exam_images/shared/', blank=True, null=True, verbose_name="Ảnh dùng chung (A-F)")
    # Dùng cho các câu 36-40 (Đoạn văn đọc hiểu dài)
    passage_text = models.TextField(blank=True, null=True, verbose_name="Đoạn văn dùng chung (Chữ Hán)")
    passage_pinyin = models.TextField(blank=True, null=True, verbose_name="Đoạn văn dùng chung (Pinyin)")

    # ================= NỘI DUNG CÂU HỎI =================
    content = models.TextField(blank=True, null=True, verbose_name="Câu hỏi (Chữ Hán)")
    content_pinyin = models.TextField(blank=True, null=True, verbose_name="Câu hỏi (Pinyin)")
    image = models.ImageField(upload_to='exam_images/', blank=True, null=True, verbose_name="Hình ảnh đính kèm câu hỏi")
    
    # ================= CÁC ĐÁP ÁN (HỖ TRỢ PINYIN KÉP) =================
    option_a = models.CharField(max_length=255, blank=True, null=True, verbose_name="Đáp án A (Chữ)")
    option_a_pinyin = models.CharField(max_length=255, blank=True, null=True, verbose_name="Đáp án A (Pinyin)")
    
    option_b = models.CharField(max_length=255, blank=True, null=True, verbose_name="Đáp án B (Chữ)")
    option_b_pinyin = models.CharField(max_length=255, blank=True, null=True, verbose_name="Đáp án B (Pinyin)")
    
    option_c = models.CharField(max_length=255, blank=True, null=True, verbose_name="Đáp án C (Chữ)")
    option_c_pinyin = models.CharField(max_length=255, blank=True, null=True, verbose_name="Đáp án C (Pinyin)")
    
    # Các đáp án D, E, F thường dùng cho bài nối chữ/hình nên chỉ cần 1 trường
    option_d = models.CharField(max_length=255, blank=True, null=True, verbose_name="Đáp án D")
    option_e = models.CharField(max_length=255, blank=True, null=True, verbose_name="Đáp án E")
    option_f = models.CharField(max_length=255, blank=True, null=True, verbose_name="Đáp án F")
    
    correct_answer = models.CharField(max_length=5, verbose_name="Đáp án đúng (A/B/C/D/E/F)")
    explanation = models.TextField(blank=True, null=True, verbose_name="Giải thích chi tiết")

    def __str__(self):
        return f"Đề {self.exam.title} - Câu {self.question_number}"

class ExamResult(models.Model):
    user = models.ForeignKey('auth.User', on_delete=models.CASCADE, verbose_name="Học viên")
    exam = models.ForeignKey(Exam, on_delete=models.CASCADE, verbose_name="Đề thi")
    score = models.FloatField(verbose_name="Điểm số đạt được")
    total_correct = models.IntegerField(verbose_name="Số câu đúng")
    time_spent = models.IntegerField(verbose_name="Thời gian làm bài (giây)")
    completed_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.username} - {self.exam.title} - {self.score} điểm"