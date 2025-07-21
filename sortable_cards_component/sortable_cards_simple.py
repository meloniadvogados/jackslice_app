import os
import streamlit.components.v1 as components

# Declarar componente apontando para a versão simples
_component_func = components.declare_component(
    "sortable_cards_simple",
    path=os.path.join(os.path.dirname(__file__), "frontend", "simple")
)

def sortable_cards_simple(command=None, key=None):
    """
    Componente super simples para testar loops.
    """
    return _component_func(
        command=command,
        key=key, 
        default=None  # NUNCA retorna nada por padrão
    )