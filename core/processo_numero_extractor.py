import os
import re
import fitz  # PyMuPDF

class ProcessoNumeroExtractor:
    def __init__(self, pdf_path: str):
        self.pdf_path = pdf_path

    def extrair_numero(self) -> str:
        # Tenta primeiro pelo conteúdo do PDF (1ª página)
        try:
            doc = fitz.open(self.pdf_path)
            texto = doc[0].get_text()
            doc.close()

            match = re.search(r"\d{7}-\d{2}\.\d{4}\.\d\.\d{2}\.\d{4}", texto)
            if match:
                return match.group()
        except Exception as e:
            print(f"[ERRO] Falha ao ler PDF: {e}")

        # Fallback: tenta extrair do nome do arquivo
        nome_arquivo = os.path.basename(self.pdf_path)
        match = re.search(r"\d{7}-\d{2}\.\d{4}\.\d\.\d{2}\.\d{4}", nome_arquivo)
        return match.group() if match else "processo"
