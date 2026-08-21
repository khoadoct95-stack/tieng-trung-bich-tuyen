import os
import shutil
from PIL import Image

# ================= CẤU HÌNH =================
# Thay đổi đường dẫn tới thư mục chứa ảnh giải nén của bạn
FOLDER_PATH = r"C:\Users\Khoa\Desktop\TiengTrungBichTuyen\Tat_ca_anh_tu_Word" 

# Kích thước ngưỡng để nghi ngờ là rác (bạn có thể để cao lên một chút cũng không sợ mất ảnh)
MIN_WIDTH = 60   
MIN_HEIGHT = 60 

# Tên thư mục chứa rác (tự động tạo bên trong thư mục ảnh của bạn)
TRASH_FOLDER = "Thung_Rac_Nghi_Ngo"
# ============================================

def smart_clean_up(folder_path, min_w, min_h):
    print(f"🔍 Đang quét thư mục: {folder_path}...\n")
    moved_count = 0
    error_count = 0
    
    if not os.path.exists(folder_path):
        print("❌ Lỗi: Không tìm thấy thư mục gốc!")
        return

    # Tạo thư mục thùng rác nếu chưa có
    trash_path = os.path.join(folder_path, TRASH_FOLDER)
    if not os.path.exists(trash_path):
        os.makedirs(trash_path)

    for filename in os.listdir(folder_path):
        file_path = os.path.join(folder_path, filename)
        
        # Bỏ qua nếu nó là thư mục (như cái Thung_Rac_Nghi_Ngo vừa tạo)
        if os.path.isdir(file_path):
            continue
            
        try:
            with Image.open(file_path) as img:
                width, height = img.size
            
            # Tính tỷ lệ khung hình (phát hiện đường kẻ chỉ ngang/dọc)
            aspect_ratio = width / height if height > 0 else 0
            
            is_junk = False
            
            # Điều kiện 1: Quá bé
            if width < min_w or height < min_h:
                is_junk = True
                ly_do = f"Quá bé ({width}x{height})"
                
            # Điều kiện 2: Quá méo mó (Ví dụ: rộng gấp 10 lần chiều cao -> đường kẻ ngang)
            elif aspect_ratio > 10 or aspect_ratio < 0.1:
                is_junk = True
                ly_do = f"Đường kẻ/Méo mó ({width}x{height})"

            if is_junk:
                # DI CHUYỂN thay vì XÓA
                shutil.move(file_path, os.path.join(trash_path, filename))
                print(f"📦 Cách ly: {filename} - Lý do: {ly_do}")
                moved_count += 1
                
        except Exception:
            error_count += 1
            pass

    print("\n" + "="*50)
    print(f"✅ DỌN DẸP HOÀN TẤT!")
    print(f"🔥 Đã cách ly {moved_count} ảnh vào thư mục: '{TRASH_FOLDER}'")
    print(f"💡 Lời khuyên: Hãy vào thư mục đó kiểm tra lại, nếu không có ảnh bị bắt nhầm thì có thể xóa hẳn (Ctrl+A -> Delete)!")
    print("="*50)

if __name__ == "__main__":
    smart_clean_up(FOLDER_PATH, MIN_WIDTH, MIN_HEIGHT)