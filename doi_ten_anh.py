import os
from PIL import Image

# ================= CẤU HÌNH =================
# Đường dẫn thư mục chứa ảnh của bạn
FOLDER_PATH = r"C:\Users\Khoa\Desktop\TiengTrungBichTuyen\Tat_ca_anh_tu_Word"

# Đánh số bắt đầu từ số mấy? (Ví dụ: 1 -> q1.jpg, q2.jpg)
START_NUMBER = 1
# ============================================

def rename_to_q_jpg(folder_path, start_idx):
    if not os.path.exists(folder_path):
        print("❌ Không tìm thấy thư mục!")
        return

    # Lọc các file ảnh hiện có
    valid_exts = ('.png', '.jpg', '.jpeg')
    files = [f for f in os.listdir(folder_path) if f.lower().endswith(valid_exts)]
    
    # Sắp xếp file theo tên để giữ đúng thứ tự từ trên xuống của Word
    files.sort()

    print(f"🔄 Đang xử lý {len(files)} ảnh thành định dạng q*.jpg...\n")
    
    for index, filename in enumerate(files):
        old_path = os.path.join(folder_path, filename)
        
        # Tên file mới (luôn là .jpg)
        new_name = f"q{start_idx + index}.jpg"
        new_path = os.path.join(folder_path, new_name)
        
        try:
            # Dùng thư viện PIL mở ảnh và chuyển đổi bắt buộc sang RGB (chuẩn JPG)
            with Image.open(old_path) as img:
                rgb_im = img.convert('RGB')
                rgb_im.save(new_path, 'JPEG', quality=95) # quality=95 giữ độ nét cực cao
            
            # Xóa file cũ đi (nếu file cũ khác tên/đuôi file mới)
            if old_path != new_path:
                os.remove(old_path)
                
            print(f"✅ {filename}  -->  {new_name}")
        except Exception as e:
            print(f"⚠️ Bỏ qua {filename}: {e}")

    print("\n" + "="*40)
    print("🎉 HOÀN TẤT ĐỔI TÊN VÀ CHUYỂN SANG JPG!")
    print("="*40)

if __name__ == "__main__":
    rename_to_q_jpg(FOLDER_PATH, START_NUMBER)