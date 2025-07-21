import customtkinter as ctk

class SettingsWindow(ctk.CTkToplevel):
    def __init__(self, parent):
        super().__init__(parent)
        self.title("⚙️ Configurações")
        self.geometry("300x180")
        self.resizable(False, False)
        self.parent = parent

        self.protocol("WM_DELETE_WINDOW", self._on_close)

        self.parent.iconify()

        self.create_widgets()
        self.center_window()

        self.grab_set()
        self.focus_force()
        self.transient(parent)

    def center_window(self):
        self.update_idletasks()
        width = 300
        height = 180
        x = (self.winfo_screenwidth() // 2) - (width // 2)
        y = (self.winfo_screenheight() // 2) - (height // 2)
        self.geometry(f"{width}x{height}+{x}+{y}")

    def create_widgets(self):
        ctk.CTkLabel(self, text="⚙️ Configurações", font=ctk.CTkFont(size=14)).pack(pady=(20, 5))
        
        ctk.CTkLabel(self, text="Configurações disponíveis no menu principal", 
                    font=ctk.CTkFont(size=12)).pack(pady=10)

        ctk.CTkButton(self, text="✅ OK", command=self.apply_settings).pack(pady=20)

    def apply_settings(self):
        self.destroy()
        self.parent.deiconify()

    def _on_close(self):
        self.destroy()
        self.parent.deiconify()