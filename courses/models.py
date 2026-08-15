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