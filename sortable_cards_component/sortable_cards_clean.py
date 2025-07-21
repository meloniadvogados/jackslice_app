import os
import streamlit.components.v1 as components

# Componente LIMPO - sem complicações
_component_func = components.declare_component(
    "sortable_cards_clean",
    path=os.path.join(os.path.dirname(__file__), "frontend", "clean")
)

def sortable_cards_clean(files, key=None, show_debug=True):
    """
    Componente de cards ordenáveis LIMPO e SIMPLES.
    
    Args:
        files: Lista de arquivos para exibir
        key: Chave única do componente  
        show_debug: Mostrar debug visual (padrão: True)
    
    Returns:
        Lista com ordem atual dos IDs sempre que houver mudança
        None quando não há mudanças
    """
    result = _component_func(
        files=files,
        show_debug=show_debug,
        key=key,
        default=None  # Nunca retorna nada por padrão
    )
    
    return result