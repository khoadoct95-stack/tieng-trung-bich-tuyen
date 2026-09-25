import os
import tkinter as tk
from tkinter import ttk, messagebox
from PIL import Image, ImageTk

# ================= CẤU HÌNH ĐƯỜNG DẪN =================
# 👉 NHỚ SỬA ĐƯỜNG DẪN THƯ MỤC CỦA BẠN:
FOLDER_PATH = r"C:\Users\Khoa\Desktop\ANH_EXTRACT"

# ================= CẤU TRÚC CÁC LOẠI ĐỀ THI =================
STRUCTURES = {
    "HSK 1 (3.0)": [
        # Nghe Phần 1 (1-5): Chọn ảnh A, B, C (Mỗi câu 3 ảnh)
        "1_a", "1_b", "1_c", "2_a", "2_b", "2_c", 
        "3_a", "3_b", "3_c", "4_a", "4_b", "4_c", "5_a", "5_b", "5_c",
        # Nghe Phần 3 (11-15): Nối ảnh A-F
        "11_a", "11_b", "11_c", "11_d", "11_e", "11_f",
        # Đọc Phần 1 (21-25): Nối ảnh A-F
        "21_a", "21_b", "21_c", "21_d", "21_e", "21_f"
    ],
    "HSK 2 (3.0)": [
        # Nghe Phần 1 (1-5): Chọn ảnh A, B, C
        "1_a", "1_b", "1_c", "2_a", "2_b", "2_c", 
        "3_a", "3_b", "3_c", "4_a", "4_b", "4_c", "5_a", "5_b", "5_c",
        # Nghe Phần 2 (6-10): Dùng chung rổ ảnh A-F
        "6_a", "6_b", "6_c", "6_d", "6_e", "6_f",
        # Nghe Phần 3 (11-15): Dùng chung rổ ảnh A-F
        "11_a", "11_b", "11_c", "11_d", "11_e", "11_f",
        # Đọc Phần 1 (26-30): Dùng chung rổ ảnh A-F (VỪA BỔ SUNG)
        "26_a", "26_b", "26_c", "26_d", "26_e", "26_f",
    ]
}

class ImageRenamerApp:
    def __init__(self, root):
        self.root = root
        self.root.title("⚙️ Cấu Hình Đổi Tên Ảnh")
        self.root.geometry("450x250")
        self.root.configure(bg="#F1F5F9")
        
        # --- MÀN HÌNH KHỞI ĐỘNG (CHỌN CẤU TRÚC) ---
        self.startup_frame = tk.Frame(self.root, bg="#F1F5F9")
        self.startup_frame.pack(expand=True, fill=tk.BOTH, padx=20, pady=20)
        
        tk.Label(self.startup_frame, text="CHỌN LOẠI CẤU TRÚC ĐỀ THI", font=("Arial", 14, "bold"), bg="#F1F5F9", fg="#334155").pack(pady=15)
        
        self.combo_type = ttk.Combobox(self.startup_frame, values=list(STRUCTURES.keys()), font=("Arial", 12), state="readonly", width=25)
        self.combo_type.current(1) # Mặc định chọn HSK 2
        self.combo_type.pack(pady=10)
        
        btn_start = tk.Button(
            self.startup_frame, text="🚀 Bắt đầu đổi tên", font=("Arial", 12, "bold"), 
            bg="#10B981", fg="white", cursor="hand2", padx=20, pady=5, borderwidth=0,
            command=self.start_renamer
        )
        btn_start.pack(pady=20)

    def start_renamer(self):
        # Lấy dữ liệu cấu trúc đã chọn
        selected_type = self.combo_type.get()
        self.expected_names = STRUCTURES[selected_type]
        self.exam_title = selected_type
        
        # Hủy màn hình khởi động
        self.startup_frame.destroy()
        
        # Mở giao diện chính
        self.init_main_ui()
        self.load_images()

    def init_main_ui(self):
        self.root.title(f"🚀 Bảng Điều Khiển Gắn Ảnh - {self.exam_title}")
        self.root.geometry("950x850") # Nới rộng ra một chút để chứa đủ các nút HSK2
        
        self.lbl_status = tk.Label(self.root, text="Đang tải dữ liệu...", font=("Arial", 12), bg="#F1F5F9", fg="#64748B")
        self.lbl_status.pack(pady=5)
        
        # Khung hiển thị ảnh
        self.lbl_img = tk.Label(self.root, bg="#E2E8F0", relief="solid", borderwidth=1)
        self.lbl_img.pack(pady=10)
        
        # --- KHUNG LƯỚI BUTTONS (GRID) ---
        self.frame_grid = tk.Frame(self.root, bg="#F1F5F9")
        self.frame_grid.pack(pady=10)
        
        self.buttons = {}
        cols = 6 # Chia 6 cột để hiển thị A-F trên cùng 1 hàng cho đẹp
        for i, name in enumerate(self.expected_names):
            btn = tk.Button(
                self.frame_grid, text=name, width=6, font=("Arial", 11, "bold"),
                cursor="hand2", command=lambda n=name: self.on_button_click(n)
            )
            btn.grid(row=i // cols, column=i % cols, padx=4, pady=4)
            self.buttons[name] = btn

        # Khung nhập tên thủ công (Phòng hờ)
        frame_input = tk.Frame(self.root, bg="#F1F5F9")
        frame_input.pack(pady=10)
        tk.Label(frame_input, text="Gõ tay nếu tên lạ:", font=("Arial", 11), bg="#F1F5F9").pack(side=tk.LEFT)
        self.entry_custom = tk.Entry(frame_input, font=("Arial", 14, "bold"), width=15, justify="center")
        self.entry_custom.pack(side=tk.LEFT, padx=10)
        
        help_text = (
            "🖱️ CLICK CHUỘT: Đặt tên cho ảnh bằng nút tương ứng.\n"
            "⌨️ [ENTER]: Đặt bằng ô Gõ tay   |   [Phím S]: Bỏ qua ẢNH này (Ảnh rác)\n"
            "🟧 Màu cam: Tên đang đề xuất   |   🟩 Màu xanh: Đã gán xong"
        )
        tk.Label(self.root, text=help_text, font=("Arial", 10), bg="#F1F5F9", fg="#0284c7", justify="center").pack(pady=5)
        
        # Lắng nghe sự kiện bàn phím
        self.root.bind('<Return>', self.on_enter)
        self.root.bind('<s>', self.on_skip_image)
        self.root.bind('<S>', self.on_skip_image)

    def load_images(self):
        # --- KIỂM TRA FILE ĐẦU VÀO ---
        if not os.path.exists(FOLDER_PATH):
            messagebox.showerror("Lỗi", "KHÔNG TÌM THẤY THƯ MỤC! Hãy kiểm tra lại FOLDER_PATH.")
            self.root.destroy()
            return

        valid_exts = ('.png', '.jpg', '.jpeg')
        # Lọc ra các file chưa có tiền tố 'q'
        self.files = [f for f in os.listdir(FOLDER_PATH) if f.lower().endswith(valid_exts) and not f.lower().startswith('q')]
        
        if not self.files:
            messagebox.showwarning("Trống", "KHÔNG TÌM THẤY ẢNH CHƯA ĐƯỢC XỬ LÝ!\nCó thể thư mục trống hoặc tất cả ảnh đã có chữ 'q' ở đầu.")
            self.root.destroy()
            return

        # Sắp xếp file theo thứ tự số tự nhiên
        self.files.sort(key=lambda f: int(''.join(filter(str.isdigit, f)) or 0))
        self.file_idx = 0
        self.name_idx = 0
        
        # Bắt đầu hiển thị
        self.load_current_state()

    def load_current_state(self):
        if self.file_idx >= len(self.files):
            messagebox.showinfo("Hoàn tất", "🎉 Đã duyệt hết tất cả các ảnh trong thư mục!\nGiờ bạn có thể nén file ZIP và Upload lên Web.")
            self.root.destroy()
            return
            
        self.current_file = self.files[self.file_idx]
        self.lbl_status.config(text=f"Tiến độ file ảnh: {self.file_idx + 1}/{len(self.files)}  (Đang hiển thị: {self.current_file})")
        
        # Tìm nút đang được đề xuất tiếp theo (màu cam)
        suggested_name = ""
        for i, name in enumerate(self.expected_names):
            if self.buttons[name]['state'] != 'disabled':
                if i == self.name_idx:
                    self.buttons[name].config(bg="#F59E0B", fg="white")
                    suggested_name = f"q{name}.jpg"
                else:
                    self.buttons[name].config(bg="SystemButtonFace", fg="black")

        self.entry_custom.delete(0, tk.END)
        self.entry_custom.insert(0, suggested_name)
        
        # Load và hiển thị ảnh
        img_path = os.path.join(FOLDER_PATH, self.current_file)
        try:
            img = Image.open(img_path)
            img.thumbnail((500, 350)) 
            self.tk_img = ImageTk.PhotoImage(img)
            self.lbl_img.config(image=self.tk_img)
        except Exception as e:
            self.lbl_status.config(text=f"Lỗi hiển thị ảnh: {e}")

    def on_button_click(self, name_clicked):
        final_name = f"q{name_clicked}.jpg"
        self.thuc_hien_doi_ten(final_name)

    def on_enter(self, event):
        custom_name = self.entry_custom.get().strip()
        if custom_name == "": return
        if not custom_name.endswith('.jpg'):
            custom_name += '.jpg'
        
        # Tự động chèn chữ 'q' nếu gõ thiếu
        if not custom_name.startswith('q'):
            custom_name = 'q' + custom_name
            
        self.thuc_hien_doi_ten(custom_name)

    def thuc_hien_doi_ten(self, final_name):
        if not hasattr(self, 'files') or not self.files: return
            
        old_path = os.path.join(FOLDER_PATH, self.current_file)
        new_path = os.path.join(FOLDER_PATH, final_name)
        
        try:
            with Image.open(old_path) as img:
                rgb_im = img.convert('RGB')
                rgb_im.save(new_path, 'JPEG', quality=95)
            if old_path != new_path:
                os.remove(old_path)
        except Exception as e:
            messagebox.showerror("Lỗi", f"Không thể lưu ảnh: {e}")
            return
            
        name_core = final_name.replace('.jpg', '').replace('q', '', 1)
        if name_core in self.buttons:
            self.buttons[name_core].config(bg="#10B981", fg="white", state="disabled")
            
            idx = self.expected_names.index(name_core)
            self.name_idx = max(self.name_idx, idx + 1)
            
        self.file_idx += 1
        self.load_current_state()

    def on_skip_image(self, event):
        if not hasattr(self, 'files') or not self.files: return
        self.file_idx += 1
        self.load_current_state()

if __name__ == "__main__":
    root = tk.Tk()
    app = ImageRenamerApp(root)
    root.mainloop()