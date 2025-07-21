import customtkinter as ctk
from tkinter import filedialog
from core.XPTO import XPTO
from core.pdf_extract_runner import PDFExtractRunner
from core.processo_numero_extractor import ProcessoNumeroExtractor
import threading
import os
from core.utils import sanitize_filename

class MainWindow(ctk.CTkToplevel):
    def __init__(self, parent, preloaded_pdf=None):
        self.parent = parent
        super().__init__(parent)
        self.title("✂️ PDF Slicer - Fatiamento de PDF")
        self.geometry("1300x720")
        self.resizable(False, False)
        self.center_window()
        self.protocol("WM_DELETE_WINDOW", self._on_close)

        self.check_vars = []
        self.sections = []
        self.pdf_path = ""
        self.filename_base = ""
        self.numero_processo = ""

        self._build()
        self.grab_set()
        self.focus_force()
        self.transient(parent)


        if preloaded_pdf:
            threading.Thread(target=self._process, args=(preloaded_pdf,), daemon=True).start()

    def center_window(self):
        self.update_idletasks()
        width = 1300
        height = 720
        x = (self.winfo_screenwidth() // 2) - (width // 2)
        y = (self.winfo_screenheight() // 2) - (height // 2)
        self.geometry(f"{width}x{height}+{x}+{y}")

    def _build(self):
        container = ctk.CTkFrame(self)
        container.pack(padx=20, pady=10, fill="both")

        self.label = ctk.CTkLabel(container, text="📄 Selecione um arquivo PDF:", font=ctk.CTkFont(size=16, weight="bold"))
        self.label.pack(pady=(10, 5))

        btn_frame = ctk.CTkFrame(container, fg_color="transparent")
        btn_frame.pack()

        ctk.CTkButton(btn_frame, text="📂 Selecionar", command=self._on_select, width=150).pack(side="left", padx=10)
        self.execute_button = ctk.CTkButton(btn_frame, text="🚀 Executar", command=self._on_execute, width=150)
        self.execute_button.pack(side="left", padx=10)

        self.numero_label = ctk.CTkLabel(container, text="", font=ctk.CTkFont(size=14))
        self.numero_label.pack(pady=(5, 0))

        self.progress_label = ctk.CTkLabel(container, text="")
        self.progress_label.pack()

        self.progress_bar = ctk.CTkProgressBar(container, mode='determinate')
        self.progress_bar.set(0)
        self.progress_bar.pack(pady=10)
        self.progress_bar.pack_forget()

        header = ctk.CTkFrame(self)
        header.pack(fill="x", padx=10, pady=(10, 0))
        titles = ["", "ID", "Data", "Documento", "Tipo", "Página Inicial", "Página Final"]
        widths = [30, 100, 150, 400, 150, 100, 100]
        for i, (t, w) in enumerate(zip(titles, widths)):
            ctk.CTkLabel(header, text=t, width=w, anchor="w").grid(row=0, column=i, padx=5)

        self.scroll = ctk.CTkScrollableFrame(self, width=1250, height=500)
        self.scroll.pack(pady=10, padx=10, fill="both", expand=True)

    def _on_select(self):
        path = filedialog.askopenfilename(filetypes=[("PDF files", "*.pdf")])
        if not path:
            return
        self.label.configure(text=f"📄 Arquivo selecionado: {os.path.basename(path)}")
        threading.Thread(target=self._process, args=(path,), daemon=True).start()

    def _process(self, pdf_path):
        self._show_progress()
        self.pdf_path = pdf_path
        self.filename_base = os.path.splitext(os.path.basename(pdf_path))[0]

        self.numero_processo = ProcessoNumeroExtractor(pdf_path).extrair_numero()
        self.numero_label.configure(text=f"Nº Processo: {self.numero_processo}")

        def update_progress(current, total):
            progress = current / total
            self.progress_bar.set(progress)
            self.progress_label.configure(text=f"Lendo página {current} / {total}")

        pipeline = XPTO(pdf_path)
        sections = pipeline.run(progress_callback=update_progress)

        self._hide_progress()
        self.sections = sections
        self._display(sections)

    def _show_progress(self):
        self.progress_bar.set(0)
        self.progress_label.configure(text="⏳ Lendo PDF...")
        self.progress_bar.pack(pady=10)
        self.progress_bar.start()

    def _hide_progress(self):
        self.progress_bar.stop()
        self.progress_bar.pack_forget()
        self.progress_label.configure(text="")

    def _display(self, sections):
        for w in self.scroll.winfo_children():
            w.destroy()
        self.check_vars.clear()

        if not sections:
            ctk.CTkLabel(self.scroll, text="Nenhum documento encontrado.").pack()
            return

        for sec in sections:
            row = ctk.CTkFrame(self.scroll)
            row.pack(fill="x", padx=5, pady=2)

            var = ctk.BooleanVar()
            ctk.CTkCheckBox(row, text="", variable=var, width=20).grid(row=0, column=0, padx=5)
            self.check_vars.append((var, sec))

            cols = ["id", "data", "documento", "tipo", "pagina_inicial", "pagina_final"]
            widths = [100, 150, 400, 150, 100, 100]
            for i, (k, w) in enumerate(zip(cols, widths), start=1):
                ctk.CTkLabel(row, text=sec.get(k, ""), width=w, anchor="w").grid(row=0, column=i, padx=5)

    def _on_execute(self):
        selected = [sec for var, sec in self.check_vars if var.get()]
        if not selected:
            print("[GUI] Nenhum item selecionado.")
            return

        runner = PDFExtractRunner(self.pdf_path)

        for item in selected:
            id_ = item.get("id")
            start = int(item.get("pagina_inicial", 1))
            end = int(item.get("pagina_final", start))
            nome_doc = sanitize_filename(item.get("documento", "saida"))
            nome_arquivo = f"{nome_doc}.pdf"
            output_path = self.numero_processo
            runner.extrair_intervalo(start, end, nome_arquivo, output_path)

        print(f"[GUI] Extração concluída para {len(selected)} documentos.")
        self._show_success_popup(len(selected))

    def _show_success_popup(self, total):
        popup = ctk.CTkToplevel(self)
        popup.title("Sucesso")
        popup.geometry("350x120")
        popup.resizable(False, False)
        popup.grab_set()

        popup.update_idletasks()
        width = 350
        height = 120
        x = (popup.winfo_screenwidth() // 2) - (width // 2)
        y = (popup.winfo_screenheight() // 2) - (height // 2)
        popup.geometry(f"{width}x{height}+{x}+{y}")

        texto = f"✅ {total} documento{'s' if total != 1 else ''} extraído{'s' if total != 1 else ''} com sucesso!"

        ctk.CTkLabel(popup, text=texto, font=ctk.CTkFont(size=14)).pack(pady=20)
        ctk.CTkButton(popup, text="OK", command=lambda: [popup.destroy(), self._show_open_folder_popup()]).pack(pady=(0, 10))

    def _show_open_folder_popup(self):
        popup = ctk.CTkToplevel(self)
        popup.title("Abrir pasta")
        popup.geometry("400x150")
        popup.resizable(False, False)
        popup.grab_set()

        popup.update_idletasks()
        width = 400
        height = 150
        x = (popup.winfo_screenwidth() // 2) - (width // 2)
        y = (popup.winfo_screenheight() // 2) - (height // 2)
        popup.geometry(f"{width}x{height}+{x}+{y}")

        ctk.CTkLabel(popup, text="📁 Deseja abrir a pasta de saída?", font=ctk.CTkFont(size=14)).pack(pady=(20, 10))

        btn_frame = ctk.CTkFrame(popup, fg_color="transparent")
        btn_frame.pack(pady=10)

        ctk.CTkButton(btn_frame, text="📂 Abrir Pasta", command=lambda: [popup.destroy(), self._abrir_pasta_output()]).pack(side="left", padx=10)
        ctk.CTkButton(btn_frame, text="❌ Cancelar", command=popup.destroy).pack(side="left", padx=10)

    def _abrir_pasta_output(self):
        pasta = os.path.abspath("output_pdf")
        if os.path.exists(pasta):
            os.startfile(pasta)
        else:
            print("[ERRO] Pasta de saída não encontrada.")

    def _on_close(self):
        self.parent.deiconify()
        self.master.deiconify()
        self.destroy()