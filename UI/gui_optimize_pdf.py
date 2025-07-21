
import customtkinter as ctk
from tkinter import filedialog, messagebox
import subprocess
import os
import threading

class OptimizePDFWindow(ctk.CTkToplevel):
    def __init__(self, parent):
        super().__init__(parent)
        self.title("🧹 Otimizar PDF")
        self.geometry("500x420")
        self.resizable(False, False)
        self.parent = parent

        self.protocol("WM_DELETE_WINDOW", self._on_close)

        self.selected_file = None
        self.output_dir = None
        self.compression_mode = ctk.StringVar(value="leve")

        self.create_widgets()
        self.center_window()

    def _on_close(self):
        self.parent.deiconify()
        self.destroy()

    def center_window(self):
        self.update_idletasks()
        width = 500
        height = 420
        x = (self.winfo_screenwidth() // 2) - (width // 2)
        y = (self.winfo_screenheight() // 2) - (height // 2)
        self.geometry(f"{width}x{height}+{x}+{y}")

    def create_widgets(self):
        container = ctk.CTkFrame(self)
        container.pack(padx=20, pady=20, fill="both", expand=True)

        self.label = ctk.CTkLabel(container, text="📄 Selecione um arquivo PDF para otimizar:", font=ctk.CTkFont(size=14, weight="bold"))
        self.label.pack(pady=(5, 10))

        ctk.CTkButton(container, text="📂 Selecionar PDF", command=self.select_pdf).pack(pady=5)

        self.output_label = ctk.CTkLabel(container, text="📁 Diretório de saída: (não selecionado)")
        self.output_label.pack(pady=5)

        ctk.CTkButton(container, text="📁 Selecionar diretório de saída", command=self.select_output_dir).pack(pady=5)

        radio_frame = ctk.CTkFrame(container, fg_color="transparent")
        radio_frame.pack(pady=10)
        ctk.CTkLabel(radio_frame, text="🛠️ Escolha o modo de compressão:").pack(anchor="w", pady=(0, 5))
        ctk.CTkRadioButton(radio_frame, text="🔰 Modo Leve", variable=self.compression_mode, value="leve").pack(anchor="w", pady=2)
        ctk.CTkRadioButton(radio_frame, text="🚀 Modo Turbo", variable=self.compression_mode, value="turbo").pack(anchor="w", pady=2)

        self.optimize_button = ctk.CTkButton(container, text="🧹 Otimizar", command=self.start_optimization, state="disabled")
        self.optimize_button.pack(pady=15)

        self.progress_label = ctk.CTkLabel(container, text="⏳")
        self.progress_label.pack()

        self.progress_bar = ctk.CTkProgressBar(container, mode='indeterminate')
        self.progress_bar.set(0)
        self.progress_bar.pack(pady=10)
        self.progress_bar.pack_forget()

    def select_pdf(self):
        file_path = filedialog.askopenfilename(filetypes=[("PDF files", "*.pdf")])
        if file_path:
            self.selected_file = file_path
            self.label.configure(text=f"📄 Arquivo selecionado: {os.path.basename(file_path)}")
            self.check_ready()

    def select_output_dir(self):
        dir_path = filedialog.askdirectory()
        if dir_path:
            self.output_dir = dir_path
            self.output_label.configure(text=f"📁 Diretório de saída: {dir_path}")
            self.check_ready()

    def check_ready(self):
        if self.selected_file and self.output_dir:
            self.optimize_button.configure(state="normal")

    def start_optimization(self):
        self.progress_label.configure(text="⏳ Otimizando PDF...")
        self.progress_bar.pack(pady=10)
        self.progress_bar.start()
        threading.Thread(target=self.optimize_pdf, daemon=True).start()

    def optimize_pdf(self):
        filename = os.path.basename(self.selected_file).replace(".pdf", "_otimizado.pdf")
        output_path = os.path.join(self.output_dir, filename)
        mode = self.compression_mode.get()

        try:
            setting = "/ebook" if mode == "leve" else "/screen"

            command = [
                "gswin64c",
                "-sDEVICE=pdfwrite",
                "-dCompatibilityLevel=1.4",
                f"-dPDFSETTINGS={setting}",
                "-dNOPAUSE",
                "-dQUIET",
                "-dBATCH",
                "-dPreserveEPSInfo=true",
                "-dAutoRotatePages=/None",
                f"-sOutputFile={output_path}",
                self.selected_file
            ]

            si = subprocess.STARTUPINFO()
            si.dwFlags |= subprocess.STARTF_USESHOWWINDOW

            subprocess.run(command, check=True, startupinfo=si)

            self.progress_bar.stop()
            self.progress_bar.pack_forget()
            self.progress_label.configure(text="")

            messagebox.showinfo("Sucesso",f"✅ PDF otimizado com sucesso! Arquivo salvo em: {output_path}")
            resposta = messagebox.askyesno("Fatiar?", "Deseja fatiar agora o arquivo otimizado?")
            if resposta:
                self.withdraw()
                def abrir_fatiador():
                    from UI.gui_pdf_sliced import MainWindow
                    self.parent.janela_fatiamento = MainWindow(self.parent, preloaded_pdf=output_path)
                self.parent.after(200, abrir_fatiador)
                self.destroy()
            else:
                os.startfile(self.output_dir)
                self.destroy()

        except Exception as e:
            self.progress_bar.stop()
            self.progress_bar.pack_forget()
            self.progress_label.configure(text="")
            messagebox.showerror("Erro", f"Erro ao otimizar o PDF:\n{e}")
