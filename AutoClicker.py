import tkinter as tk
import customtkinter as ctk
import threading
import time
import random
from pynput import mouse, keyboard
from pynput.mouse import Button, Controller as MouseController
from pynput.keyboard import Key, KeyCode, Controller as KeyboardController

# Rowez Pro Theme
ctk.set_appearance_mode("Dark")
ctk.set_default_color_theme("blue")

class AutoClickerApp(ctk.CTk):
    def __init__(self):
        super().__init__()

        # Pencere Yapılandırması
        self.title("Rowez Elite Auto Clicker PRO")
        self.geometry("500x780")
        self.attributes("-alpha", 0.96)
        
        # Engine Değişkenleri
        self.clicking = False
        self.mouse_ctrl = MouseController()
        self.kb_ctrl = KeyboardController()
        
        # Hotkey Değişkenleri
        self.current_hotkey = keyboard.Key.f8
        self.hotkey_display_text = "F8"
        self.is_listening_for_key = False
        self.fixed_pos = None
        
        # UI Kurulumu
        self.setup_ui()
        
        # Global Listeners
        self.kb_listener = keyboard.Listener(on_press=self.on_key_press)
        self.kb_listener.start()
        
        self.ms_listener = mouse.Listener(on_click=self.on_mouse_click_global)
        self.ms_listener.start()

    def setup_ui(self):
        # Üst Başlık ve Versiyon
        self.title_label = ctk.CTkLabel(self, text="ELITE AUTO CLICKER", font=ctk.CTkFont(size=26, weight="bold", family="Consolas"))
        self.title_label.pack(pady=(25, 5))
        self.ver_label = ctk.CTkLabel(self, text="v3.0 Key-Binding Edition", text_color="#3b8ed0", font=ctk.CTkFont(size=12))
        self.ver_label.pack(pady=(0, 20))

        # Ana Scrollable Frame
        self.scroll_frame = ctk.CTkScrollableFrame(self, fg_color="transparent")
        self.scroll_frame.pack(padx=20, pady=10, fill="both", expand=True)

        # 1. HIZ VE ZAMANLAMA
        self.section_header(self.scroll_frame, "ZAMANLAMA VE HIZ")
        self.speed_frame = ctk.CTkFrame(self.scroll_frame)
        self.speed_frame.pack(pady=5, padx=10, fill="x")
        self.create_input_row(self.speed_frame, "Gecikme (ms):", "100", "entry_speed")
        self.create_input_row(self.speed_frame, "Tıklama Sınırı (0=Sınırsız):", "0", "entry_limit")

        self.random_var = ctk.BooleanVar(value=True)
        self.check_random = ctk.CTkCheckBox(self.scroll_frame, text="Rastgele Sapma (Anti-Detect %15)", variable=self.random_var)
        self.check_random.pack(pady=10, padx=20, anchor="w")

        # 2. FARE VE MODLAR
        self.section_header(self.scroll_frame, "EYLEM AYARLARI")
        self.mouse_btn_opt = ctk.CTkOptionMenu(self.scroll_frame, values=["Sol Tık (Left)", "Sağ Tık (Right)", "Orta Tık (Middle)"])
        self.mouse_btn_opt.pack(pady=5, padx=10, fill="x")
        self.click_type_opt = ctk.CTkOptionMenu(self.scroll_frame, values=["Single Click", "Double Click", "Triple Click"], fg_color="#2b2b2b")
        self.click_type_opt.pack(pady=5, padx=10, fill="x")

        # 3. KISAYOL ATAMA (Key Binder)
        self.section_header(self.scroll_frame, "KISAYOL (HOTKEY) AYARI")
        self.hotkey_frame = ctk.CTkFrame(self.scroll_frame)
        self.hotkey_frame.pack(pady=5, padx=10, fill="x")
        
        self.label_cur_hkey = ctk.CTkLabel(self.hotkey_frame, text=f"Mevcut: {self.hotkey_display_text}", font=ctk.CTkFont(weight="bold"))
        self.label_cur_hkey.pack(side="left", padx=15, pady=15)
        
        self.btn_bind = ctk.CTkButton(self.hotkey_frame, text="TUŞ ATA", width=100, command=self.start_binding_mode, fg_color="#34495e")
        self.btn_bind.pack(side="right", padx=10)

        # 4. GELİŞMİŞ OPSİYONLAR
        self.section_header(self.scroll_frame, "GELİŞMİŞ OPSİYONLAR")
        self.lock_pos_var = ctk.BooleanVar(value=False)
        self.check_lock = ctk.CTkCheckBox(self.scroll_frame, text="Konumu Kilitle (Cursor Lock)", variable=self.lock_pos_var)
        self.check_lock.pack(pady=5, padx=20, anchor="w")

        # 5. DURUM VE KONTROL
        self.status_frame = ctk.CTkFrame(self, height=80, corner_radius=0, fg_color="#1a1a1a")
        self.status_frame.pack(side="bottom", fill="x")
        self.status_label = ctk.CTkLabel(self.status_frame, text="SİSTEM BEKLEMEDE", text_color="gray", font=ctk.CTkFont(size=14, weight="bold"))
        self.status_label.pack(pady=10)
        self.main_btn = ctk.CTkButton(self.status_frame, text="START ENGINE", command=self.toggle_engine, 
                                     fg_color="#1f6aa5", hover_color="#144870", height=40)
        self.main_btn.pack(pady=(0, 15), padx=50, fill="x")

    def section_header(self, parent, text):
        lbl = ctk.CTkLabel(parent, text=text, font=ctk.CTkFont(size=11, weight="bold"), text_color="#555555")
        lbl.pack(pady=(15, 5), padx=15, anchor="w")

    def create_input_row(self, parent, label, default, attr_name):
        row = ctk.CTkFrame(parent, fg_color="transparent")
        row.pack(fill="x", pady=2)
        ctk.CTkLabel(row, text=label).pack(side="left", padx=10)
        entry = ctk.CTkEntry(row, width=70)
        entry.insert(0, default)
        entry.pack(side="right", padx=10)
        setattr(self, attr_name, entry)

    # --- KEY BINDING LOGIC ---
    def start_binding_mode(self):
        self.is_listening_for_key = True
        self.btn_bind.configure(text="TUŞA BASIN...", fg_color="#e67e22")
        self.label_cur_hkey.configure(text="Bekleniyor...")

    def on_key_press(self, key):
        if self.is_listening_for_key:
            self.current_hotkey = key
            self.hotkey_display_text = str(key).replace("Key.", "").upper()
            self.finalize_binding()
        elif key == self.current_hotkey:
            self.toggle_engine()

    def on_mouse_click_global(self, x, y, button, pressed):
        if pressed and self.is_listening_for_key:
            # Sol tıkı (button.left) hotkey olarak atamayı engelliyoruz (arayüzü kullanabilmek için)
            if button != mouse.Button.left:
                self.current_hotkey = button
                self.hotkey_display_text = str(button).replace("Button.", "MOUSE ").upper()
                self.finalize_binding()

        elif pressed and button == self.current_hotkey:
            self.toggle_engine()

    def finalize_binding(self):
        self.is_listening_for_key = False
        self.btn_bind.configure(text="TUŞ ATA", fg_color="#34495e")
        self.label_cur_hkey.configure(text=f"Mevcut: {self.hotkey_display_text}")

    # --- CORE ENGINE ---
    def toggle_engine(self):
        if self.is_listening_for_key: return # Atama modundayken çalışma
        
        self.clicking = not self.clicking
        if self.clicking:
            if self.lock_pos_var.get():
                self.fixed_pos = self.mouse_ctrl.position
            self.status_label.configure(text="ENGINE RUNNING...", text_color="#2ecc71")
            self.main_btn.configure(text="STOP", fg_color="#c0392b", hover_color="#a93226")
            threading.Thread(target=self.core_loop, daemon=True).start()
        else:
            self.status_label.configure(text="SİSTEM DURDURULDU", text_color="red")
            self.main_btn.configure(text="START ENGINE", fg_color="#1f6aa5")

    def core_loop(self):
        click_count = 0
        try:
            limit = int(self.entry_limit.get())
            base_delay = int(self.entry_speed.get()) / 1000.0
        except:
            limit, base_delay = 0, 0.1

        while self.clicking:
            if self.lock_pos_var.get() and self.fixed_pos:
                self.mouse_ctrl.position = self.fixed_pos

            btn_str = self.mouse_btn_opt.get()
            m_btn = Button.left if "Sol" in btn_str else Button.right if "Sağ" in btn_str else Button.middle
            
            type_str = self.click_type_opt.get()
            reps = 1 if "Single" in type_str else 2 if "Double" in type_str else 3

            for _ in range(reps):
                self.mouse_ctrl.click(m_btn)
            
            click_count += 1
            if limit > 0 and click_count >= limit:
                self.clicking = False
                self.after(0, self.toggle_engine)
                break

            delay = base_delay
            if self.random_var.get():
                delay += random.uniform(-0.015, 0.015) * base_delay
            
            time.sleep(max(0.0001, delay))

if __name__ == "__main__":
    app = AutoClickerApp()
    app.mainloop()