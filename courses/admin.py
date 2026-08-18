from django.contrib import admin
from django.urls import path
from django.shortcuts import render, redirect
from django.contrib import messages
import openpyxl

# 1. IMPORT TOÀN BỘ MODEL (Cả cũ và mới)
# Lưu ý: Hãy kiểm tra file models.py của bạn có những model nào (Curriculum, Lesson, Vocabulary...) thì khai báo hết vào đây:
from .models import Exam, ExamQuestion, ExamResult, Curriculum, Lesson, Vocabulary

# ==========================================
# KHU VỰC 1: QUẢN LÝ GIÁO TRÌNH, BÀI HỌC (PHẦN CŨ CỦA BẠN)
# ==========================================
# Bạn hãy chép lại các đoạn code đăng ký admin.site.register() cũ của bạn vào đây. 
# Nếu không nhớ code cũ, bạn có thể dùng tạm các dòng đăng ký mặc định này:
admin.site.register(Curriculum)
admin.site.register(Lesson)
admin.site.register(Vocabulary)


# ==========================================
# KHU VỰC 2: QUẢN LÝ ĐỀ THI HSK (PHẦN MỚI CẬP NHẬT)
# ==========================================
@admin.register(Exam)
class ExamAdmin(admin.ModelAdmin):
    list_display = ('title', 'hsk_level', 'duration_minutes', 'created_at')
    list_filter = ('hsk_level',)
    search_fields = ('title',)
    
    def get_urls(self):
        urls = super().get_urls()
        custom_urls = [
            path('import-excel/', self.admin_site.admin_view(self.import_excel_view), name='import_exam_excel'),
        ]
        return custom_urls + urls

    def import_excel_view(self, request):
        if request.method == 'POST':
            excel_file = request.FILES.get('excel_file')
            exam_title = request.POST.get('exam_title')
            hsk_level = request.POST.get('hsk_level')
            duration = request.POST.get('duration', 60)

            if not excel_file:
                messages.error(request, "Vui lòng chọn file Excel!")
                return redirect('.')

            try:
                wb = openpyxl.load_workbook(excel_file)
                sheet = wb.active

                exam = Exam.objects.create(
                    title=exam_title,
                    hsk_level=int(hsk_level),
                    duration_minutes=int(duration)
                )

                for row in sheet.iter_rows(min_row=2, values_only=True):
                    if not row[0]: continue
                    
                    q_num, section, group, p_text, p_pinyin, content, c_pinyin, opt_a, a_pin, opt_b, b_pin, opt_c, c_pin, correct = row[:14]
                    
                    ExamQuestion.objects.create(
                        exam=exam,
                        question_number=int(q_num),
                        section_type=section,
                        question_group=group,
                        passage_text=p_text,
                        passage_pinyin=p_pinyin,
                        content=content,
                        content_pinyin=c_pinyin,
                        option_a=opt_a,
                        option_a_pinyin=a_pin,
                        option_b=opt_b,
                        option_b_pinyin=b_pin,
                        option_c=opt_c,
                        option_c_pinyin=c_pin,
                        correct_answer=str(correct).strip().upper()
                    )

                messages.success(request, f"Đã nhập thành công đề thi: {exam_title}!")
                return redirect('/admin/courses/exam/')
            
            except Exception as e:
                messages.error(request, f"Lỗi xử lý file Excel: {e}")
                return redirect('.')

        return render(request, 'admin/import_excel.html')

@admin.register(ExamQuestion)
class ExamQuestionAdmin(admin.ModelAdmin):
    list_display = ('exam', 'question_number', 'section_type', 'question_group')
    list_filter = ('exam', 'section_type', 'question_group')
    ordering = ('exam', 'question_number')

@admin.register(ExamResult)
class ExamResultAdmin(admin.ModelAdmin):
    list_display = ('user', 'exam', 'score', 'total_correct', 'completed_at')
    list_filter = ('exam', 'completed_at')
    search_fields = ('user__username', 'exam__title')