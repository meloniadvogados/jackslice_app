from core.page_range_extractor import PageRangeExtractor

class XPTO:
    def __init__(self, pdf_path: str):
        self.pdf_path = pdf_path
        self.index_dict = None
        self.block_dict = None

    def run(self, progress_callback=None):
        print(f"[XPTO] Iniciando pipeline para: {self.pdf_path}")

        from core.pdf_index_extractor import PDFIndexExtractor
        index_extractor = PDFIndexExtractor(self.pdf_path)
        self.index_dict = index_extractor.extract_index()
        print(f"[XPTO] Index extraído: {len(self.index_dict)} entradas")

        from core.pdf_page_block_extractor import PDFPageBlockExtractor
        block_extractor = PDFPageBlockExtractor(self.pdf_path)
        block_extractor.extract_blocks(progress_callback=progress_callback)
        self.block_dict = block_extractor.blocks_per_page

        print("[XPTO] Executando PageRangeExtractor...")
        range_extractor = PageRangeExtractor(self.index_dict, self.block_dict)
        sections = range_extractor.atualizar_paginas()

        print("[XPTO] Pipeline finalizado com sucesso ✅")

        return sections
