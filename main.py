
import sys
import os

# Garante que o Python enxergue as pastas core/ e UI/
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

import customtkinter as ctk
from tkinter import messagebox
from PIL import Image

from core.settings_manager import SettingsManager
from core.XPTO import XPTO

class PDFSlicerApp(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("Jack - Fatiador de PDF 🔪")
        self.geometry("500x600")
        self.resizable(False, False)
        self.center_window()

        # Garante que a pasta de saída exista
        os.makedirs("output_pdf", exist_ok=True)

        self.settings_manager = SettingsManager()
        self.create_widgets()

    def center_window(self):
        self.update_idletasks()
        width = 500
        height = 600
        x = (self.winfo_screenwidth() // 2) - (width // 2)
        y = (self.winfo_screenheight() // 2) - (height // 2)
        self.geometry(f"{width}x{height}+{x}+{y}")

    def create_widgets(self):
        container = ctk.CTkFrame(self)
        container.pack(padx=20, pady=20, fill="both", expand=True)

        # Frame superior com logo e título
        top = ctk.CTkFrame(container, fg_color="transparent")
        top.pack(fill="both", expand=True)

        try:
            self.logo = ctk.CTkImage(Image.open("assets/logo.png"), size=(250, 100))
            ctk.CTkLabel(top, image=self.logo, text="").pack(pady=(40, 10))
        except Exception as e:
            print(f"Logo não carregada: {e}")

        ctk.CTkLabel(top, text="Jack - Fatiador de PDF 🔪", font=ctk.CTkFont(size=20, weight="bold")).pack(pady=(40, 10))

        # Frame central com botões
        middle = ctk.CTkFrame(container, fg_color="transparent")
        middle.pack(fill="both", expand=True)

        botoes = [
            ("⚙️ Configurações", self.open_settings),
            ("✂️ Fatiar PDF", self.slice_pdf),
            ("🧹 Otimizar PDF", self.open_optimize_window),
            ("🧠 Aplicar OCR", self.open_ocr_window),
            ("🚪 Sair", self.quit),
        ]
        for texto, comando in botoes:
            ctk.CTkButton(middle, text=texto, command=comando, height=40).pack(pady=6, fill="x", padx=40)

    def open_settings(self):
        from UI.gui_settings import SettingsWindow
        SettingsWindow(self)

    def slice_pdf(self):
        from UI.gui_pdf_sliced import MainWindow
        self.iconify()
        MainWindow(self)

    def open_optimize_window(self):
        try:
            from UI.gui_optimize_pdf import OptimizePDFWindow
            self.iconify()
            OptimizePDFWindow(self)
        except Exception as e:
            messagebox.showerror("Erro", f"Erro ao abrir janela de otimização:\n{e}")

    def open_ocr_window(self):
        try:
            from UI.gui_ocr_pdf import OCRPDFWindow
            self.iconify()
            OCRPDFWindow(self)
        except Exception as e:
            messagebox.showerror("Erro", f"Erro ao abrir janela de OCR:\n{e}")

def run_terminal_pipeline(pdf_path):
    print(f"[CLI] Rodando pipeline para: {pdf_path}")
    pipeline = XPTO(pdf_path)
    pipeline.run()

if __name__ == "__main__":
    if len(sys.argv) == 2:
        run_terminal_pipeline(sys.argv[1])
    else:
        app = PDFSlicerApp()
        app.mainloop()
