
import os
import fitz  # PyMuPDF

class PDFExtractRunner:
    def __init__(self, pdf_path: str):
        self.pdf_path = pdf_path

    def extrair_intervalo(self, pagina_inicial: int, pagina_final: int):
        """Extrai intervalo de páginas e retorna bytes em memória"""
        if not os.path.exists(self.pdf_path):
            raise FileNotFoundError(f"Arquivo não encontrado: {self.pdf_path}")

        if pagina_inicial > pagina_final:
            raise ValueError("A página inicial não pode ser maior que a página final.")

        doc = fitz.open(self.pdf_path)
        total = doc.page_count

        if pagina_inicial < 1 or pagina_final > total:
            raise ValueError(f"Intervalo inválido. O PDF tem {total} páginas.")

        novo_pdf = fitz.open()
        for i in range(pagina_inicial - 1, pagina_final):
            novo_pdf.insert_pdf(doc, from_page=i, to_page=i)

        # Retornar bytes em memória em vez de salvar arquivo
        pdf_bytes = novo_pdf.tobytes()
        novo_pdf.close()
        doc.close()

        return pdf_bytes
