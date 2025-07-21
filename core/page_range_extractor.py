import json
import os

class PageRangeExtractor:
    def __init__(self, index_data: list[dict], block_data: list[dict]):
        self.index_data = index_data
        self.block_data = block_data

    def atualizar_paginas(self):
        for item in self.index_data:
            doc_id = item.get("id")
            paginas_com_id = []

            for pagina_info in self.block_data:
                pagina_num = pagina_info.get("pagina")
                blocos = pagina_info.get("blocos_filtrados", [])

                for bloco in blocos:
                    texto = bloco.get("texto", "")
                    if doc_id in texto:
                        paginas_com_id.append(pagina_num)
                        break  # evita contar múltiplas vezes a mesma página

            if paginas_com_id:
                item["pagina_inicial"] = min(paginas_com_id)
                item["pagina_final"] = max(paginas_com_id)

        return self.index_data

    def salvar_json(self, output_path: str = "data/index_com_paginas.json"):
        dados = self.atualizar_paginas()
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        with open(output_path, "w", encoding="utf-8") as f:
            json.dump(dados, f, ensure_ascii=False, indent=4)
        print(f"[PageRangeExtractor] Arquivo salvo em: {output_path}")
