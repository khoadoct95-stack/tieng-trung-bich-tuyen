from django import forms
from django.contrib import admin
from .models import Curriculum, Lesson, Vocabulary, GameHistory

# --- TẠO FORM TÙY CHỈNH CHO BÀI HỌC ---
class LessonForm(forms.ModelForm):
    # Thêm một ô nhập Text khổng lồ (Không lưu trực tiếp vào CSDL, chỉ dùng để xử lý)
    bulk_vocab = forms.CharField(
        widget=forms.Textarea(attrs={
            'rows': 8, 
            'placeholder': 'Dán danh sách từ vựng từ Excel/Word vào đây...\nVí dụ:\n你好    nǐ hǎo    xin chào\n谢谢    xièxiè    cảm ơn'
        }),
        required=False,
        label="🚀 NHẬP NHANH TỪ VỰNG (TỪ EXCEL)",
        help_text="Copy từ Excel/Sheets dán thẳng vào đây. Hoặc tự gõ theo định dạng: Chữ Hán | Pinyin | Nghĩa (cách nhau bằng phẩy, tab, hoặc gạch ngang)."
    )

    class Meta:
        model = Lesson
        fields = '__all__'

# --- CẤU HÌNH ADMIN ---

class VocabularyInline(admin.TabularInline):
    model = Vocabulary
    extra = 3  # Giảm xuống 3 dòng cho gọn
    fields = ('hanzi', 'pinyin', 'meaning')

@admin.register(Lesson)
class LessonAdmin(admin.ModelAdmin):
    form = LessonForm  # Sử dụng Form tùy chỉnh vừa tạo
    list_display = ('title', 'curriculum', 'order')
    list_filter = ('curriculum',)
    search_fields = ('title',)
    inlines = [VocabularyInline]

    # Hàm can thiệp quá trình Lưu để tách từ vựng từ ô "Nhập nhanh"
    def save_model(self, request, obj, form, change):
        super().save_model(request, obj, form, change) # Lưu Bài học trước
        
        bulk_text = form.cleaned_data.get('bulk_vocab')
        if bulk_text:
            lines = bulk_text.strip().split('\n')
            for line in lines:
                line = line.strip()
                if not line:
                    continue
                
                # Tự động nhận diện dấu phân cách (Tab của Excel, dấu phẩy, gạch đứng, gạch ngang)
                if '\t' in line:
                    parts = line.split('\t')
                elif '|' in line:
                    parts = line.split('|')
                elif ',' in line:
                    parts = line.split(',')
                else:
                    parts = line.split('-')
                
                # Nếu đủ 3 thành phần thì tạo Từ vựng mới
                if len(parts) >= 3:
                    Vocabulary.objects.create(
                        lesson=obj,
                        hanzi=parts[0].strip(),
                        pinyin=parts[1].strip(),
                        meaning=parts[2].strip()
                    )

@admin.register(Curriculum)
class CurriculumAdmin(admin.ModelAdmin):
    list_display = ('name', 'description')
    search_fields = ('name',)

@admin.register(Vocabulary)
class VocabularyAdmin(admin.ModelAdmin):
    list_display = ('hanzi', 'pinyin', 'meaning', 'lesson')
    list_filter = ('lesson__curriculum', 'lesson')
    search_fields = ('hanzi', 'pinyin', 'meaning')

@admin.register(GameHistory)
class GameHistoryAdmin(admin.ModelAdmin):
    list_display = ('user', 'lesson', 'game_type', 'time_taken', 'created_at')
    list_filter = ('game_type', 'created_at')
    search_fields = ('user__username', 'lesson__title')