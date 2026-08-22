import os
from PIL import Image

# ================= CẤU HÌNH ĐƯỜNG DẪN =================
FOLDER_PATH = r"C:\Users\Khoa\Desktop\ANH_EXTRACT"

# ================= CẤU TRÚC CÁC BỘ ĐỀ =================
# 1. Danh sách HSK 1 Bản cũ
HSK1_OLD = [
    "1", "2", "3", "4", "5",
    "6_A", "6_B", "6_C", "7_A", "7_B", "7_C", "8_A", "8_B", "8_C", "9_A", "9_B", "9_C", "10_A", "10_B", "10_C",
    "11_A", "11_B", "11_C", "11_D", "11_E", "11_F",
    "21", "22", "23", "24", "25",
    "26_A", "26_B", "26_C", "26_D", "26_E", "26_F"
]

# 2. Danh sách HSK 1 Bản 3.0 (Bạn có thể thêm bớt tùy theo file PDF thực tế)
HSK1_3_0 = [
    "1", "2", "3", "4", "5",
    "6_A", "6_B", "6_C", "7_A", "7_B", "7_C", "8_A", "8_B", "8_C", "9_A", "9_B", "9_C", "10_A", "10_B", "10_C",
    "11_A", "11_B", "11_C", "11_D", "11_E", "11_F",
    "21_A", "21_B", "21_C", "21_D", "21_E", "21_F",
    "26_A", "26_B", "26_C", "26_D", "26_E", "26_F",
    "31_A", "31_B", "31_C", "31_D", "31_E", "31_F"
]

# Sau này có HSK 2, bạn cứ thêm HSK2_OLD = [...] vào đây
# ======================================================

def chon_cau_truc_de():
    print("\n" + "="*50)
    print("🌟 CHỌN CẤU TRÚC ĐỀ THI CẦN GẮN ẢNH 🌟")
    print("="*50)
    print("  [1]. Đề HSK 1 (Bản cũ - 40 câu)")
    print("  [2]. Đề HSK 1 (Bản 3.0 mới)")
    print("  [0]. Thoát chương trình")
    print("="*50)

    while True:
        lua_chon = input("👉 Nhập số lựa chọn của bạn (1, 2 hoặc 0): ").strip()
        
        if lua_chon == '1':
            return HSK1_OLD, "HSK 1 BẢN CŨ"
        elif lua_chon == '2':
            return HSK1_3_0, "HSK 1 BẢN 3.0"
        elif lua_chon == '0':
            print("👋 Đã thoát chương trình.")
            exit()
        else:
            print("❌ Lựa chọn không hợp lệ, vui lòng nhập lại!")

def doi_ten_theo_cau_hoi(folder_path, expected_names, ten_de):
    if not os.path.exists(folder_path):
        print("❌ Không tìm thấy thư mục ảnh! Vui lòng kiểm tra lại FOLDER_PATH.")
        return

    print("\n" + "="*70)
    print(f"🎯 CHẾ ĐỘ KÉO THẢ TỐC ĐỘ CAO: {ten_de}")
    print(" -> Cầm file ảnh từ thư mục KÉO THẢ thẳng vào cửa sổ này rồi nhấn Enter.")
    print(" -> Nếu câu đó không có ảnh, chỉ cần nhấn Enter để BỎ QUA.")
    print("="*70 + "\n")

    for q_name in expected_names:
        target_name = f"q{q_name}.jpg"
        
        while True:
            # Script gọi tên câu hỏi và chờ bạn kéo thả ảnh vào
            user_input = input(f"👉 Kéo thả ảnh cho câu [ {target_name} ] vào đây (Enter để bỏ qua): ").strip()
            
            # Bỏ qua câu này
            if user_input == "" or user_input.lower() == 's':
                print("  -> ⏭️ Đã bỏ qua.\n")
                break
            
            # Gỡ bỏ dấu ngoặc kép khi kéo thả file trên Windows/Mac
            img_path = user_input.strip('"').strip("'")
            
            # Nếu gõ tên thủ công thay vì kéo thả
            if not os.path.isabs(img_path):
                img_path = os.path.join(folder_path, img_path)

            if not os.path.exists(img_path):
                print("  -> ❌ Không tìm thấy file! Kéo thả lại cho chuẩn xác nhé.\n")
                continue
                
            new_path = os.path.join(folder_path, target_name)
            
            try:
                # Ép kiểu ảnh sang JPG chuẩn Web và lưu đè
                with Image.open(img_path) as img:
                    rgb_im = img.convert('RGB')
                    rgb_im.save(new_path, 'JPEG', quality=95)
                
                # Xóa file rác đi cho gọn thư mục
                if img_path != new_path:
                    os.remove(img_path)
                    
                print(f"  -> ✅ XONG: Đã lưu thành {target_name}\n")
                break # Thành công -> Sang câu kế tiếp!
                
            except Exception as e:
                print(f"  -> ❌ Lỗi khi xử lý ảnh: {e}\n")

    print("\n🎉 HOÀN TẤT TẤT CẢ! Hãy bôi đen các ảnh, nén ZIP và Up lên Web thôi!")

if __name__ == "__main__":
    # 1. Gọi menu cho người dùng chọn
    danh_sach_chon, ten_de_chon = chon_cau_truc_de()
    
    # 2. Chạy hàm xử lý ảnh theo danh sách vừa chọn
    doi_ten_theo_cau_hoi(FOLDER_PATH, danh_sach_chon, ten_de_chon)