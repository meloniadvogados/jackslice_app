# core/pdf_index_extractor.py

import pdfplumber
import logging
import json
import sys
import os
from datetime import datetime

logging.getLogger("pdfminer").setLevel(logging.ERROR)

class PDFIndexExtractor:
    """
    Extrai o Sumário (ID, Data, Documento, Tipo) usando pdfplumber.
    Só aceita linhas cuja coluna de data contenha uma data válida em vários formatos.
    """

    def __init__(self, pdf_path):
        self.pdf_path = pdf_path
        self.index = []

    def find_summary_start_page(self):
        try:
            with pdfplumber.open(self.pdf_path) as pdf:
                for i in reversed(range(len(pdf.pages))):
                    text = pdf.pages[i].extract_text()
                    if text and "SUMÁRIO" in text.upper():
                        print(f"[INFO] Sumário encontrado na página {i+1}")
                        return i
        except Exception as e:
            print(f"[ERROR] Erro ao localizar o Sumário: {e}")
        return -1

    def is_valid_date(self, text):
        formats = ["%d/%m/%Y", "%d/%m/%Y %H:%M", "%Y-%m-%d", "%Y-%m-%d %H:%M:%S"]
        for fmt in formats:
            try:
                datetime.strptime(text.strip(), fmt)
                return True
            except:
                continue
        return False

    def extract_index(self):
        start_page = self.find_summary_start_page()
        if start_page == -1:
            print("[INFO] Nenhum Sumário encontrado.")
            return []

        try:
            with pdfplumber.open(self.pdf_path) as pdf:
                for i in range(start_page, len(pdf.pages)):
                    page = pdf.pages[i]
                    table = page.extract_table()
                    if not table:
                        continue
                    for row in table:
                        if not row or len(row) < 4:
                            continue

                        id_val   = (row[0] or "").strip()
                        data_val = (row[1] or "").strip()
                        doc_val  = (row[2] or "").strip()
                        type_val = (row[3] or "").strip()

                        # Só aceita a linha se a data for válida
                        if not self.is_valid_date(data_val):
                            continue

                        if id_val:
                            self.index.append({
                                "id": id_val,
                                "data": data_val,
                                "documento": doc_val,
                                "tipo": type_val,
                                "pagina_inicial": "",
                                "pagina_final": ""
                            })
                print(f"[INFO] Total de itens no Sumário extraídos: {len(self.index)}")
        except Exception as e:
            print(f"[ERROR] Erro ao extrair índice: {e}")

        return self.index

    def salvar_index_json(self):
        try:
            project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
            output_dir = os.path.join(project_root, "data")
            os.makedirs(output_dir, exist_ok=True)

            base_name = os.path.splitext(os.path.basename(self.pdf_path))[0]
            output_json = os.path.join(output_dir, f"{base_name}_index.json")

            with open(output_json, "w", encoding="utf-8") as f:
                json.dump(self.index, f, ensure_ascii=False, indent=4)

            print(f"[INFO] Index salvo com sucesso em: {output_json}")
        except Exception as e:
            print(f"[ERROR] Falha ao salvar JSON: {e}")

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Uso: python pdf_index_extractor.py <caminho_para_o_pdf>")
        sys.exit(1)

    pdf_path = sys.argv[1]
    extractor = PDFIndexExtractor(pdf_path)
    index = extractor.extract_index()
    extractor.salvar_index_json()
