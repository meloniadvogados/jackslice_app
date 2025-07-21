# core/utils.py

import re
import unicodedata
import os

def sanitize_filename(filename: str, limit: int = 150) -> str:
    """
    Limpa e sanitiza nomes de arquivos para evitar erros no sistema operacional:
    - Remove acentos
    - Remove caracteres inválidos (\ / : * ? " < > |)
    - Substitui espaços por underscores
    - Remove múltiplos underscores consecutivos
    - Trunca o nome para não ultrapassar o limite de caracteres
    """
    # Remove acentos
    nfkd = unicodedata.normalize('NFKD', filename)
    filename = ''.join([c for c in nfkd if not unicodedata.combining(c)])

    # Substitui espaços por underscores
    filename = filename.replace(" ", "_")

    # Remove caracteres inválidos para nomes de arquivo no Windows
    filename = re.sub(r'[<>:"/\\|?*]', '', filename)

    # Remove underscores duplicados
    filename = re.sub(r'_{2,}', '_', filename)

    # Remove underscores do início/fim
    filename = filename.strip('_')

    #Remove quebra de linhas (\n)
    filename = re.sub(r'\s+', ' ', filename)

    # Garante extensão correta
    base, ext = os.path.splitext(filename)
    base = base[:limit]
    return f"{base}{ext}"
