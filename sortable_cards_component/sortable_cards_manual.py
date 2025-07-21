import os
import streamlit.components.v1 as components

# Declarar componente apontando para o diretório manual
_component_func = components.declare_component(
    "sortable_cards_manual",
    path=os.path.join(os.path.dirname(__file__), "frontend", "manual")
)

def sortable_cards_manual(files, command=None, key=None):
    """
    Componente de cards ordenáveis com controle manual.
    
    Args:
        files: Lista de arquivos para exibir
        command: Comando a executar ('get_order', 'reset_changes', ou None)
        key: Chave única do componente
    
    Returns:
        Dict com a ordem atual se command='get_order', None caso contrário
    """
    # O default deve ser None para não causar reruns
    result = _component_func(
        files=files, 
        command=command,
        key=key, 
        default=None
    )
    
    return result