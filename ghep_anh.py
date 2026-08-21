import os
from PIL import Image

# ================= CẤU HÌNH =================
# Thư mục chứa 6 ảnh lẻ (A, B, C, D, E, F) của bạn
FOLDER_PATH = r"C:\Users\Khoa\Desktop\TiengTrungBichTuyen\Tat_ca_anh_tu_Word\Ro_11"

# Tên file xuất ra (Ví dụ: q11.jpg cho nhóm 11-15, q26.jpg cho nhóm 26-30)
SAVE_NAME = "q11.jpg"
# ============================================

def ghep_6_anh(folder_path, save_name):
    valid_exts = ('.png', '.jpg', '.jpeg')
    # Lấy danh sách ảnh và sắp xếp theo thứ tự (A->F hoặc 1->6)
    files = [f for f in os.listdir(folder_path) if f.lower().endswith(valid_exts)]
    files.sort()

    if len(files) != 6:
        print(f"❌ Lỗi: Thư mục có {len(files)} ảnh. Yêu cầu chính xác 6 ảnh!")
        return

    print("🔄 Đang xử lý ghép ảnh...")
    images = []
    
    # Mở ảnh và chuyển sang RGB
    for f in files:
        img_path = os.path.join(folder_path, f)
        img = Image.open(img_path).convert('RGB')
        images.append(img)

    # Lấy kích thước to nhất trong 6 ảnh để làm chuẩn (tránh bị méo)
    max_w = max(img.width for img in images)
    max_h = max(img.height for img in images)

    # Resize tất cả ảnh về cùng 1 kích thước (thêm viền trắng nếu ảnh gốc nhỏ hơn)
    uniform_images = []
    for img in images:
        new_img = Image.new('RGB', (max_w, max_h), (255, 255, 255)) # Nền trắng
        # Đặt ảnh vào giữa khung
        offset = ((max_w - img.width) // 2, (max_h - img.height) // 2)
        new_img.paste(img, offset)
        uniform_images.append(new_img)

    # Tạo tấm phông bạt khổng lồ (2 cột, 3 hàng)
    grid_width = max_w * 2
    grid_height = max_h * 3
    grid_image = Image.new('RGB', (grid_width, grid_height), (255, 255, 255))

    # Dán 6 ảnh vào đúng tọa độ lưới
    # [0: A]  [1: B]
    # [2: C]  [3: D]
    # [4: E]  [5: F]
    tọa_độ = [
        (0, 0),         (max_w, 0),
        (0, max_h),     (max_w, max_h),
        (0, max_h * 2), (max_w, max_h * 2)
    ]

    for i in range(6):
        grid_image.paste(uniform_images[i], tọa_độ[i])

    # Lưu kết quả ra file mới
    save_path = os.path.join(folder_path, save_name)
    grid_image.save(save_path, 'JPEG', quality=95)
    
    print("\n" + "="*40)
    print(f"🎉 THÀNH CÔNG! Đã ghép 6 ảnh thành: {save_name}")
    print("="*40)

if __name__ == "__main__":
    ghep_6_anh(FOLDER_PATH, SAVE_NAME)