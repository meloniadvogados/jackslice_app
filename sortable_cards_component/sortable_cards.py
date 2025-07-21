import os
import streamlit.components.v1 as components

_component_func = components.declare_component(
    "sortable_cards",
    path=os.path.join(os.path.dirname(__file__), "frontend", "public")
)

def sortable_cards(files, key=None, auto_update=True):
    default_ids = [f["id"] for f in files]
    return _component_func(files=files, key=key, auto_update=auto_update, default={"value": default_ids})
