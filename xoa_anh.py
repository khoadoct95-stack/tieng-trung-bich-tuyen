import os
from PIL import Image

# ================= CẤU HÌNH =================
# Thay đổi đường dẫn tới thư mục chứa ảnh giải nén của bạn
FOLDER_PATH = r"C:\Users\Khoa\Downloads\Tat_ca_anh_tu_Word" 

# Đặt kích thước tối thiểu (tính bằng pixel)
# Các nét chữ, pinyin rác thường nhỏ hơn 50x50 pixels
MIN_WIDTH = 80   
MIN_HEIGHT = 80 
# ============================================

def clean_up_images(folder_path, min_w, min_h):
    print(f"🔍 Đang quét thư mục: {folder_path}...\n")
    deleted_count = 0
    error_count = 0
    
    # Kiểm tra xem thư mục có tồn tại không
    if not os.path.exists(folder_path):
        print("❌ Lỗi: Không tìm thấy thư mục. Vui lòng kiểm tra lại đường dẫn!")
        return

    # Duyệt qua tất cả các file trong thư mục
    for filename in os.listdir(folder_path):
        file_path = os.path.join(folder_path, filename)
        
        # Chỉ xử lý nếu nó là file (bỏ qua thư mục con)
        if os.path.isfile(file_path):
            try:
                # Mở ảnh bằng block 'with' để đảm bảo file được đóng sau khi đọc
                with Image.open(file_path) as img:
                    width, height = img.size
                
                # Kiểm tra điều kiện kích thước
                if width < min_w or height < min_h:
                    os.remove(file_path) # Tiến hành xóa file
                    print(f"🗑️ Đã xóa: {filename} (Kích thước: {width}x{height})")
                    deleted_count += 1
                    
            except Exception as e:
                # Bỏ qua các file không thể mở (file rác, file ẩn của hệ điều hành, document...)
                error_count += 1
                pass

    print("\n" + "="*40)
    print(f"✅ DỌN DẸP HOÀN TẤT!")
    print(f"🔥 Đã xóa thành công {deleted_count} ảnh rác.")
    if error_count > 0:
        print(f"⚠️ Đã bỏ qua {error_count} file không phải định dạng ảnh.")
    print("="*40)

# Thực thi chương trình
if __name__ == "__main__":
    clean_up_images(FOLDER_PATH, MIN_WIDTH, MIN_HEIGHT)