
import customtkinter as ctk
from tkinter import filedialog, messagebox
import subprocess
import os
import threading

class OCRPDFWindow(ctk.CTkToplevel):
    def __init__(self, parent):
        super().__init__(parent)
        self.title("🧠 Aplicar OCR em PDF")
        self.geometry("500x360")
        self.resizable(False, False)
        self.parent = parent

        self.protocol("WM_DELETE_WINDOW", self._on_close)

        self.selected_file = None

        self.create_widgets()
        self.center_window()

    def _on_close(self):
        self.parent.deiconify()
        self.destroy()

    def center_window(self):
        self.update_idletasks()
        width = 500
        height = 360
        x = (self.winfo_screenwidth() // 2) - (width // 2)
        y = (self.winfo_screenheight() // 2) - (height // 2)
        self.geometry(f"{width}x{height}+{x}+{y}")

    def create_widgets(self):
        container = ctk.CTkFrame(self)
        container.pack(padx=20, pady=20, fill="both", expand=True)

        self.label = ctk.CTkLabel(container, text="📄 Selecione um PDF com imagens para aplicar OCR:",
                                  font=ctk.CTkFont(size=14, weight="bold"))
        self.label.pack(pady=(5, 10))

        self.select_button = ctk.CTkButton(container, text="📂 Selecionar PDF", command=self.select_pdf)
        self.select_button.pack(pady=5)

        self.ocr_button = ctk.CTkButton(container, text="🧠 Aplicar OCR", command=self.start_ocr, state="disabled")
        self.ocr_button.pack(pady=10)

        self.progress_label = ctk.CTkLabel(container, text="⏳")
        self.progress_label.pack(pady=5)

        self.progress_bar = ctk.CTkProgressBar(container, mode='indeterminate')
        self.progress_bar.pack(pady=5)
        self.progress_bar.pack_forget()

    def select_pdf(self):
        file_path = filedialog.askopenfilename(filetypes=[("PDF files", "*.pdf")])
        if file_path:
            self.selected_file = file_path
            self.label.configure(text=f"📄 Arquivo selecionado: {os.path.basename(file_path)}")
            self.ocr_button.configure(state="normal")

    def start_ocr(self):
        self.progress_label.configure(text="🧠 Aplicando OCR, aguarde...")
        self.progress_bar.pack(pady=5)
        self.progress_bar.start()
        threading.Thread(target=self.run_ocr, daemon=True).start()

    def run_ocr(self):
        output_path = self.selected_file.replace(".pdf", "_ocr.pdf")

        try:
            command = [
                "ocrmypdf",
                "--force-ocr",
                "--output-type", "pdf",
                "--jobs", "4",
                self.selected_file,
                output_path
            ]

            si = subprocess.STARTUPINFO()
            si.dwFlags |= subprocess.STARTF_USESHOWWINDOW

            subprocess.run(command, check=True, startupinfo=si)

            self.progress_bar.stop()
            self.progress_bar.pack_forget()
            self.progress_label.configure(text="")

            messagebox.showinfo("Sucesso", f"✅ OCR aplicado com sucesso!\nArquivo salvo em:\n{output_path}")
            os.startfile(os.path.dirname(output_path))
            self.destroy()

        except Exception as e:
            self.progress_bar.stop()
            self.progress_bar.pack_forget()
            self.progress_label.configure(text="")
            messagebox.showerror("Erro", f"Ocorreu um erro ao aplicar OCR:\n{e}")
