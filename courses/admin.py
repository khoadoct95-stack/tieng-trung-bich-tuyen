from django.contrib import admin
from django.urls import path
from django.shortcuts import render, redirect
from django.contrib import messages
from django.http import HttpResponse
from django.core.files.base import ContentFile
import openpyxl
import zipfile
import io
import re

# 1. IMPORT TOÀN BỘ MODEL
from .models import Exam, ExamQuestion, ExamResult, Curriculum, Lesson, Vocabulary

# ==========================================
# KHU VỰC 1: QUẢN LÝ GIÁO TRÌNH, BÀI HỌC
# ==========================================
admin.site.register(Curriculum)
admin.site.register(Lesson)
admin.site.register(Vocabulary)


# ==========================================
# KHU VỰC 2: QUẢN LÝ ĐỀ THI HSK
# ==========================================
@admin.register(Exam)
class ExamAdmin(admin.ModelAdmin):
    list_display = ('title', 'hsk_level', 'duration_minutes', 'created_at')
    list_filter = ('hsk_level',)
    search_fields = ('title',)
    
    # Đăng ký các đường dẫn tùy chỉnh trong Admin
    def get_urls(self):
        urls = super().get_urls()
        custom_urls = [
            path('import-excel/', self.admin_site.admin_view(self.import_excel_view), name='import_exam_excel'),
            path('extract-images/', self.admin_site.admin_view(self.extract_images_view), name='extract_word_images'),
            path('bulk-upload-images/', self.admin_site.admin_view(self.bulk_image_upload_view), name='bulk_upload_images'),
        ]
        return custom_urls + urls

    # ---------------------------------------------------------
    # CHỨC NĂNG 1: GẮN ẢNH HÀNG LOẠT TỪ FILE ZIP (TÍNH NĂNG MỚI)
    # ---------------------------------------------------------
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

                # Đọc file ZIP trong bộ nhớ
                with zipfile.ZipFile(zip_file, 'r') as z:
                    for filename in z.namelist():
                        # Bỏ qua các thư mục hoặc file ẩn của macOS/Windows
                        if '__MACOSX' in filename or filename.startswith('.'):
                            continue

                        # Dùng Regex tìm các file có dạng q1.jpg, q15.png...
                        match = re.search(r'q(\d+)\.(jpg|jpeg|png)', filename.lower().split('/')[-1])
                        if match:
                            q_num = int(match.group(1)) # Lấy số câu hỏi
                            try:
                                # Tìm câu hỏi tương ứng trong CSDL
                                question = ExamQuestion.objects.get(exam=exam, question_number=q_num)
                                image_data = z.read(filename)
                                
                                # Lưu ảnh vào field 'image' của câu hỏi
                                file_name_to_save = filename.split('/')[-1]
                                question.image.save(file_name_to_save, ContentFile(image_data), save=True)
                                success_count += 1
                            except ExamQuestion.DoesNotExist:
                                pass # Bỏ qua nếu câu hỏi không tồn tại

                messages.success(request, f"Thành công! Đã gắn tự động {success_count} bức ảnh vào đề thi: {exam.title}.")
                return redirect('/admin/courses/exam/')
            
            except Exception as e:
                messages.error(request, f"Đã xảy ra lỗi khi xử lý file ZIP: {e}")
                return redirect('.')

        exams = Exam.objects.all().order_by('-created_at')
        return render(request, 'admin/bulk_upload_images.html', {'exams': exams})

    # ---------------------------------------------------------
    # CHỨC NĂNG 2: VẮT ẢNH TỪ FILE WORD (.DOCX)
    # ---------------------------------------------------------
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

    # ---------------------------------------------------------
    # CHỨC NĂNG 3: IMPORT DỮ LIỆU ĐỀ THI TỪ FILE EXCEL
    # ---------------------------------------------------------
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
                    
                    # An toàn xử lý đáp án bị rỗng
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
# KHU VỰC 3: QUẢN LÝ CÂU HỎI VÀ KẾT QUẢ
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