import os
from PIL import Image

# ================= CẤU HÌNH =================
# Đường dẫn thư mục chứa ảnh (sau khi đã gắp "rổ ảnh" ra ngoài)
FOLDER_PATH = r"C:\Users\Khoa\Desktop\TiengTrungBichTuyen\Tat_ca_anh_tu_Word"
# ============================================

def doi_ten_tuong_tac(folder_path):
    if not os.path.exists(folder_path):
        print("❌ Không tìm thấy thư mục!")
        return

    valid_exts = ('.png', '.jpg', '.jpeg')
    files = [f for f in os.listdir(folder_path) if f.lower().endswith(valid_exts)]
    files.sort() # Sắp xếp theo thứ tự Word xuất ra

    print("="*60)
    print("💡 MẸO: Hãy mở thư mục ảnh ở chế độ 'Large Icons' để nhìn ảnh,")
    print("sau đó gõ số câu tương ứng vào màn hình này.")
    print("="*60 + "\n")
    
    for index, filename in enumerate(files):
        old_path = os.path.join(folder_path, filename)
        
        # Màn hình chờ bạn gõ số
        cau_so = input(f"[{index+1}/{len(files)}] Ảnh '{filename}' thuộc CÂU SỐ MẤY? (Bấm Enter để bỏ qua): ")
        
        # Nếu bạn có gõ số (VD: 4, 15, 23...)
        if cau_so.strip() != "":
            new_name = f"q{cau_so.strip()}.jpg"
            new_path = os.path.join(folder_path, new_name)
            
            try:
                # Ép kiểu sang JPG cho chuẩn Web
                with Image.open(old_path) as img:
                    rgb_im = img.convert('RGB')
                    rgb_im.save(new_path, 'JPEG', quality=95)
                
                # Xóa file cũ
                if old_path != new_path:
                    os.remove(old_path)
                    
                print(f"  -> ✅ Xong! Đã lưu thành {new_name}\n")
                
            except Exception as e:
                print(f"  -> ❌ Lỗi khi xử lý ảnh: {e}\n")
        
        # Nếu bạn không gõ gì mà bấm Enter luôn (Ảnh rác sót lại)
        else:
            print("  -> ⏭️ Đã bỏ qua.\n")

    print("🎉 HOÀN TẤT ĐỔI TÊN TOÀN BỘ ẢNH LẺ!")

if __name__ == "__main__":
    doi_ten_tuong_tac(FOLDER_PATH)