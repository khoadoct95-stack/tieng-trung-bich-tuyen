from django.contrib import admin
from django.urls import path
from django.shortcuts import render, redirect
from django.contrib import messages
from django.http import HttpResponse
from django.core.files.base import ContentFile
from django import forms
import openpyxl
import zipfile
import io
import re

# IMPORT TOÀN BỘ MODEL
from .models import Exam, ExamQuestion, ExamResult, Curriculum, Lesson, Vocabulary

# ==========================================
# KHU VỰC 1: QUẢN LÝ GIÁO TRÌNH
# ==========================================
admin.site.register(Curriculum)
admin.site.register(Vocabulary)

# ==========================================
# KHU VỰC 2: QUẢN LÝ BÀI HỌC (CÓ TÍNH NĂNG DÁN TỪ VỰNG HÀNG LOẠT)
# ==========================================
class LessonAdminForm(forms.ModelForm):
    bulk_vocab = forms.CharField(
        label="⚡ Dán nhanh nhiều từ vựng (Tự động tách)",
        widget=forms.Textarea(attrs={
            'rows': 8, 
            'placeholder': 'Định dạng: Chữ Hán | Pinyin | Nghĩa (Mỗi từ 1 dòng)\nVí dụ:\n你好 | nǐ hǎo | Xin chào\n谢谢 | xièxie | Cảm ơn'
        }),
        required=False,
        help_text="Mỗi từ vựng 1 dòng. Ngăn cách nhau bằng dấu gạch đứng ( | ) hoặc dấu Tab."
    )

    class Meta:
        model = Lesson
        fields = '__all__'

@admin.register(Lesson)
class LessonAdmin(admin.ModelAdmin):
    form = LessonAdminForm
    
    # Hiển thị các trường trong giao diện Admin
    fieldsets = (
        ('Thông tin Bài học', {
            # Giả định tên các cột trong model Lesson của bạn. 
            # (Nếu model Lesson của bạn có tên cột khác, hãy sửa lại cho khớp nhé)
            'fields': ('curriculum', 'order', 'title_hanzi', 'title_pinyin', 'title_vietnamese', 'description') 
        }),
        ('Thêm Từ vựng nhanh', {
            'fields': ('bulk_vocab',),
            'classes': ('collapse',), # Làm cho phần này có thể thu gọn lại cho gọn gàng
        }),
    )

    def save_model(self, request, obj, form, change):
        # Lưu đối tượng Lesson trước
        super().save_model(request, obj, form, change)

        # Lấy dữ liệu từ ô bulk_vocab
        bulk_text = form.cleaned_data.get('bulk_vocab')
        
        if bulk_text:
            lines = bulk_text.strip().split('\n')
            count = 0
            for line in lines:
                if not line.strip():
                    continue
                
                # Cắt bằng dấu | hoặc Tab
                parts = line.split('|') if '|' in line else line.split('\t')
                
                if len(parts) >= 3:
                    # Chú ý: Đảm bảo 'chinese', 'pinyin', 'meaning' khớp với models.py của Vocabulary
                    Vocabulary.objects.create(
                        lesson=obj,
                        chinese=parts[0].strip(),
                        pinyin=parts[1].strip(),
                        meaning=parts[2].strip()
                    )
                    count += 1
            if count > 0:
                messages.success(request, f"Đã tự động thêm thành công {count} từ vựng vào bài học này!")


# ==========================================
# KHU VỰC 3: QUẢN LÝ ĐỀ THI HSK
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
            path('extract-images/', self.admin_site.admin_view(self.extract_images_view), name='extract_word_images'),
            path('bulk-upload-images/', self.admin_site.admin_view(self.bulk_image_upload_view), name='bulk_upload_images'),
        ]
        return custom_urls + urls

    # ... (Các hàm bulk_image_upload_view, extract_images_view, import_excel_view của bạn được giữ nguyên y hệt bên dưới)
    def bulk_image_upload_view(self, request):
        if request.method == 'POST':
            exam_id = request.POST.get('exam_id')
            zip_file = request.FILES.get('zip_file')

            if not exam_id or not zip_file:
                messages.error(request, "Vui lòng chọn đề thi và tải lên file ZIP!")
                return redirect('.')

            try:
                exam = Exam.objects.get(id=exam_id)
                success_count = 0

                with zipfile.ZipFile(zip_file, 'r') as z:
                    for filename in z.namelist():
                        if '__MACOSX' in filename or filename.startswith('.'):
                            continue
                        
                        match = re.search(r'q(\d+)\.(jpg|jpeg|png)', filename.lower().split('/')[-1])
                        if match:
                            q_num = int(match.group(1))
                            try:
                                question = ExamQuestion.objects.get(exam=exam, question_number=q_num)
                                image_data = z.read(filename)
                                file_name_to_save = filename.split('/')[-1]
                                question.image.save(file_name_to_save, ContentFile(image_data), save=True)
                                success_count += 1
                            except ExamQuestion.DoesNotExist:
                                pass

                messages.success(request, f"Thành công! Đã gắn tự động {success_count} bức ảnh vào đề thi: {exam.title}.")
                return redirect('/admin/courses/exam/')
            
            except Exception as e:
                messages.error(request, f"Đã xảy ra lỗi khi xử lý file ZIP: {e}")
                return redirect('.')

        exams = Exam.objects.all().order_by('-created_at')
        return render(request, 'admin/bulk_upload_images.html', {'exams': exams})

    def extract_images_view(self, request):
        if request.method == 'POST':
            word_file = request.FILES.get('word_file')
            
            if not word_file or not word_file.name.endswith('.docx'):
                messages.error(request, "Vui lòng tải lên file Word định dạng .docx hợp lệ!")
                return redirect('.')

            try:
                zip_buffer = io.BytesIO()
                with zipfile.ZipFile(word_file, 'r') as docx_zip:
                    with zipfile.ZipFile(zip_buffer, 'w') as out_zip:
                        for item in docx_zip.namelist():
                            if item.startswith('word/media/'):
                                filename = item.split('/')[-1] 
                                if filename: 
                                    image_data = docx_zip.read(item)
                                    out_zip.writestr(filename, image_data) 
                
                response = HttpResponse(zip_buffer.getvalue(), content_type='application/zip')
                response['Content-Disposition'] = 'attachment; filename="Tat_ca_anh_tu_Word.zip"'
                return response

            except Exception as e:
                messages.error(request, f"Lỗi khi vắt ảnh: {e}")
                return redirect('.')

        return render(request, 'admin/extract_images.html')

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
                    
                    correct_ans = str(correct).strip().upper() if correct else ""

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
                        correct_answer=correct_ans
                    )

                messages.success(request, f"Đã nhập thành công đề thi: {exam_title}!")
                return redirect('/admin/courses/exam/')
            
            except Exception as e:
                messages.error(request, f"Lỗi xử lý file Excel: {e}")
                return redirect('.')

        return render(request, 'admin/import_excel.html')


# ==========================================
# KHU VỰC 4: QUẢN LÝ CÂU HỎI VÀ KẾT QUẢ ĐỀ THI
# ==========================================
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