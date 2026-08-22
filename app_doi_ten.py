import os
import tkinter as tk
from tkinter import messagebox
from PIL import Image, ImageTk

# ================= CẤU HÌNH ĐƯỜNG DẪN =================
# 👉 NHỚ SỬA ĐƯỜNG DẪN THƯ MỤC CỦA BẠN:
FOLDER_PATH = r"C:\Users\Khoa\Desktop\ANH_EXTRACT"

HSK1_OLD = [
    "1", "2", "3", "4", "5",
    "6_A", "6_B", "6_C", "7_A", "7_B", "7_C", "8_A", "8_B", "8_C", "9_A", "9_B", "9_C", "10_A", "10_B", "10_C",
    "11_A", "11_B", "11_C", "11_D", "11_E", "11_F",
    "21", "22", "23", "24", "25",
    "26_A", "26_B", "26_C", "26_D", "26_E", "26_F"
]

HSK1_3_0 = [
    "1", "2", "3", "4", "5",
    "6_A", "6_B", "6_C", "7_A", "7_B", "7_C", "8_A", "8_B", "8_C", "9_A", "9_B", "9_C", "10_A", "10_B", "10_C",
    "11_A", "11_B", "11_C", "11_D", "11_E", "11_F",
    "21_A", "21_B", "21_C", "21_D", "21_E", "21_F",
    "26_A", "26_B", "26_C", "26_D", "26_E", "26_F",
    "31_A", "31_B", "31_C", "31_D", "31_E", "31_F"
]
# ======================================================

class ImageRenamerApp:
    def __init__(self, root, folder_path, expected_names, title):
        self.root = root
        self.folder_path = folder_path
        self.expected_names = expected_names
        
        # --- THIẾT KẾ GIAO DIỆN CHÍNH ---
        self.root.title(f"🚀 Bảng Điều Khiển Gắn Ảnh - {title}")
        self.root.geometry("900x750")
        self.root.configure(bg="#F1F5F9")
        
        self.lbl_status = tk.Label(root, text="", font=("Arial", 12), bg="#F1F5F9", fg="#64748B")
        self.lbl_status.pack(pady=5)
        
        # Khung hiển thị ảnh
        self.lbl_img = tk.Label(root, bg="#E2E8F0", relief="solid", borderwidth=1)
        self.lbl_img.pack(pady=10)
        
        # --- KHUNG LƯỚI BUTTONS (GRID) ---
        self.frame_grid = tk.Frame(root, bg="#F1F5F9")
        self.frame_grid.pack(pady=10)
        
        self.buttons = {}
        cols = 8 # Số cột của lưới
        for i, name in enumerate(self.expected_names):
            # Tạo các nút tương ứng với danh sách tên
            btn = tk.Button(
                self.frame_grid, 
                text=name, 
                width=6, 
                font=("Arial", 11, "bold"),
                cursor="hand2",
                command=lambda n=name: self.on_button_click(n) # Lệnh khi bấm nút
            )
            btn.grid(row=i // cols, column=i % cols, padx=4, pady=4)
            self.buttons[name] = btn

        # Khung nhập tên thủ công (Phòng hờ)
        frame_input = tk.Frame(root, bg="#F1F5F9")
        frame_input.pack(pady=10)
        tk.Label(frame_input, text="Gõ tay nếu tên lạ:", font=("Arial", 11), bg="#F1F5F9").pack(side=tk.LEFT)
        self.entry_custom = tk.Entry(frame_input, font=("Arial", 14, "bold"), width=12, justify="center")
        self.entry_custom.pack(side=tk.LEFT, padx=10)
        
        help_text = (
            "🖱️ CLICK CHUỘT VÀO LƯỚI: Đặt tên cho ảnh bằng nút tương ứng.\n"
            "⌨️ [ENTER]: Đặt bằng ô Gõ tay   |   [Phím S]: Bỏ qua ẢNH này (Ảnh rác)\n"
            "🟧 Màu cam: Tên đang đề xuất   |   🟩 Màu xanh: Đã gán xong"
        )
        tk.Label(root, text=help_text, font=("Arial", 10), bg="#F1F5F9", fg="#0284c7", justify="center").pack(pady=5)
        
        # Lắng nghe sự kiện bàn phím
        self.root.bind('<Return>', self.on_enter)
        self.root.bind('<s>', self.on_skip_image)

        # --- KIỂM TRA FILE ĐẦU VÀO ---
        if not os.path.exists(folder_path):
            messagebox.showerror("Lỗi", "KHÔNG TÌM THẤY THƯ MỤC! Hãy kiểm tra lại FOLDER_PATH.")
            self.root.destroy()
            return

        valid_exts = ('.png', '.jpg', '.jpeg')
        self.files = [f for f in os.listdir(folder_path) if f.lower().endswith(valid_exts) and not f.lower().startswith('q')]
        
        if not self.files:
            messagebox.showwarning("Trống", "KHÔNG TÌM THẤY ẢNH!\nCó thể thư mục trống hoặc các ảnh đã có chữ 'q' ở đầu.")
            self.root.destroy()
            return

        # Sắp xếp file theo thứ tự số tự nhiên trong tên file
        self.files.sort(key=lambda f: int(''.join(filter(str.isdigit, f)) or 0))
        self.file_idx = 0
        self.name_idx = 0
        
        # Bắt đầu hiển thị
        self.load_current_state()

    def load_current_state(self):
        if self.file_idx >= len(self.files):
            messagebox.showinfo("Hoàn tất", "🎉 Đã duyệt hết tất cả các ảnh trong thư mục!")
            self.root.destroy()
            return
            
        self.current_file = self.files[self.file_idx]
        self.lbl_status.config(text=f"Tiến độ file ảnh: {self.file_idx + 1}/{len(self.files)}")
        
        # Tìm nút đang được đề xuất tiếp theo (màu cam)
        suggested_name = ""
        for i, name in enumerate(self.expected_names):
            if self.buttons[name]['state'] != 'disabled': # Nút chưa bị bấm
                if i == self.name_idx:
                    self.buttons[name].config(bg="#F59E0B", fg="white") # Nổi bật màu Cam
                    suggested_name = f"q{name}.jpg"
                else:
                    self.buttons[name].config(bg="SystemButtonFace", fg="black") # Trở về mặc định

        self.entry_custom.delete(0, tk.END)
        self.entry_custom.insert(0, suggested_name)
        
        # Load và hiển thị ảnh
        img_path = os.path.join(self.folder_path, self.current_file)
        try:
            img = Image.open(img_path)
            img.thumbnail((450, 300)) # Bo kích thước ảnh cho vừa khung
            self.tk_img = ImageTk.PhotoImage(img)
            self.lbl_img.config(image=self.tk_img)
        except Exception as e:
            self.lbl_status.config(text=f"Lỗi hiển thị ảnh: {e}")

    # Khi người dùng bấm trực tiếp vào lưới Button
    def on_button_click(self, name_clicked):
        final_name = f"q{name_clicked}.jpg"
        self.thuc_hien_doi_ten(final_name)

    # Khi người dùng tự gõ vào ô Text và bấm Enter
    def on_enter(self, event):
        custom_name = self.entry_custom.get().strip()
        if custom_name == "": return
        if not custom_name.endswith('.jpg'):
            custom_name += '.jpg'
        self.thuc_hien_doi_ten(custom_name)

    # Hàm lõi xử lý việc đổi tên
    def thuc_hien_doi_ten(self, final_name):
        if not hasattr(self, 'files') or not self.files: return
            
        old_path = os.path.join(self.folder_path, self.current_file)
        new_path = os.path.join(self.folder_path, final_name)
        
        try:
            # Ép kiểu JPG và lưu
            with Image.open(old_path) as img:
                rgb_im = img.convert('RGB')
                rgb_im.save(new_path, 'JPEG', quality=95)
            if old_path != new_path:
                os.remove(old_path)
        except Exception as e:
            messagebox.showerror("Lỗi", f"Không thể lưu ảnh: {e}")
            return
            
        # Tìm xem cái tên vừa đặt khớp với nút nào trong Lưới để đổi sang màu Xanh (Hoàn tất)
        name_core = final_name.replace('.jpg', '').replace('q', '', 1)
        if name_core in self.buttons:
            self.buttons[name_core].config(bg="#10B981", fg="white", state="disabled")
            
            # Cập nhật con trỏ name_idx sang vị trí kế tiếp
            idx = self.expected_names.index(name_core)
            self.name_idx = max(self.name_idx, idx + 1)
            
        # Chuyển sang ảnh tiếp theo
        self.file_idx += 1
        self.load_current_state()

    def on_skip_image(self, event):
        if not hasattr(self, 'files') or not self.files: return
        self.file_idx += 1
        self.load_current_state()

# ================= MENU TỪ TERMINAL =================
def chon_cau_truc():
    print("\n" + "="*50)
    print("🌟 MENU APP GẮN TÊN ẢNH NHANH 🌟")
    print("  [1]. Đề HSK 1 Bản cũ")
    print("  [2]. Đề HSK 1 Bản 3.0")
    print("="*50)
    
    while True:
        choice = input("👉 Nhập số 1 hoặc 2: ").strip()
        if choice == '1':
            return HSK1_OLD, "HSK 1 BẢN CŨ"
        elif choice == '2':
            return HSK1_3_0, "HSK 1 BẢN 3.0"
        else:
            print("❌ Vui lòng chỉ nhập 1 hoặc 2.")

if __name__ == "__main__":
    # Bước 1: Chọn đề trên cửa sổ đen
    danh_sach, ten_de = chon_cau_truc()
    
    # Bước 2: Bật giao diện trực quan lên
    root = tk.Tk()
    app = ImageRenamerApp(root, FOLDER_PATH, danh_sach, ten_de)
    root.mainloop()