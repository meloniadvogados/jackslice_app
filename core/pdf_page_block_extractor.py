import fitz  # PyMuPDF
import json
import os

class PDFPageBlockExtractor:
    def __init__(self, pdf_path):
        self.pdf_path = pdf_path
        self.blocks_per_page = []

    def extract_blocks(self, progress_callback=None):
        try:
            doc = fitz.open(self.pdf_path)
            total_pages = doc.page_count

            for page_num in range(total_pages):
                page = doc.load_page(page_num)
                blocks = page.get_text("blocks")

                if not blocks:
                    continue

                width = page.rect.width
                height = page.rect.height
                max_x = max(b[2] for b in blocks)
                max_y = max(b[3] for b in blocks)

                blocos_filtrados = []

                if width > height:
                    area_x0 = 500
                    area_x1 = max_x
                    area_y0 = 0
                    area_y1 = max_y
                else:
                    area_x0 = 0
                    area_x1 = max_x
                    area_y0 = max_y - 100
                    area_y1 = max_y

                for b in blocks:
                    x0, y0, x1, y1, texto = b[:5]

                    if (x1 >= area_x0 and x0 <= area_x1 and
                        y1 >= area_y0 and y0 <= area_y1):

                        blocos_filtrados.append({
                            "x0": x0,
                            "y0": y0,
                            "x1": x1,
                            "y1": y1,
                            "texto": texto.strip()
                        })

                self.blocks_per_page.append({
                    "pagina": page_num + 1,
                    "orientacao": "paisagem" if width > height else "retrato",
                    "max_x": max_x,
                    "max_y": max_y,
                    "blocos_filtrados": blocos_filtrados
                })

                if progress_callback:
                    progress_callback(page_num + 1, total_pages)

            print(f"[INFO] Total de páginas processadas: {total_pages}")

        except Exception as e:
            print(f"[ERROR] Falha ao processar PDF: {e}")

    def save_blocks_json(self):
        try:
            project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
            output_dir = os.path.join(project_root, "data")
            os.makedirs(output_dir, exist_ok=True)

            base_name = os.path.splitext(os.path.basename(self.pdf_path))[0]
            output_json = os.path.join(output_dir, f"{base_name}_blocks.json")

            with open(output_json, "w", encoding="utf-8") as f:
                json.dump(self.blocks_per_page, f, ensure_ascii=False, indent=4)

            print(f"[INFO] Blocos por página salvos em: {output_json}")
        except Exception as e:
            print(f"[ERROR] Falha ao salvar JSON: {e}")
