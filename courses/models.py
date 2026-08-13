from django.db import models

class Curriculum(models.Model):
    name = models.CharField(max_length=100, verbose_name="Tên giáo trình (VD: HSK 1, Msutong)")
    description = models.TextField(blank=True, verbose_name="Mô tả")

    def __str__(self):
        return self.name

class Lesson(models.Model):
    curriculum = models.ForeignKey(Curriculum, on_delete=models.CASCADE, related_name='lessons')
    title = models.CharField(max_length=100, verbose_name="Tên bài học (VD: Bài 1: Xin chào)")
    order = models.IntegerField(verbose_name="Thứ tự bài học", default=1)

    def __str__(self):
        return f"{self.curriculum.name} - {self.title}"

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