import streamlit as st
from sortable_cards_component.sortable_cards_clean import sortable_cards_clean

def test_cards_clean_page():
    """
    Teste do componente LIMPO - sem loops, sem complicações
    """
    st.title("✨ Teste Componente LIMPO - Zero Loops")
    
    # Contador de reruns para detectar loops
    if "clean_rerun_count" not in st.session_state:
        st.session_state.clean_rerun_count = 0
    st.session_state.clean_rerun_count += 1
    
    # Alert de loop se necessário
    if st.session_state.clean_rerun_count > 5:
        st.error(f"🚨 POSSÍVEL LOOP! Rerun count: {st.session_state.clean_rerun_count}")
    else:
        st.info(f"🔄 Rerun count: {st.session_state.clean_rerun_count} (normal até 3-4)")
    
    # Dados de teste
    files = [
        {"id": "0", "name": "arquivoA.pdf", "pages": 5, "size": 2.1, "type": "application/pdf"},
        {"id": "1", "name": "fotoB.png", "pages": 3, "size": 0.8, "type": "image/png"},
        {"id": "2", "name": "arquivoC.pdf", "pages": 8, "size": 1.8, "type": "application/pdf"},
        {"id": "3", "name": "planilha.xlsx", "pages": 1, "size": 0.3, "type": "application/xlsx"},
    ]
    
    # Estado da ordem
    if "clean_order" not in st.session_state:
        st.session_state.clean_order = ["0", "1", "2", "3"]
    
    st.markdown("### 🎯 Componente Drag & Drop LIMPO")
    
    # Componente LIMPO - sem complicações
    result = sortable_cards_clean(files, key="test_clean", show_debug=True)
    
    # Processar resultado - SIMPLES
    if result:
        st.session_state.clean_order = [str(x) for x in result]
        st.success(f"✅ Nova ordem detectada: {result}")
        # NÃO faz rerun - deixa o Streamlit decidir
    
    st.markdown("---")
    
    # Informações de debug
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("### 📊 Estado Atual")
        st.write(f"**Ordem salva:** {st.session_state.clean_order}")
        st.write(f"**Resultado componente:** {result}")
        
    with col2:
        st.markdown("### 🎯 Lista Ordenada")
        for i, file_id in enumerate(st.session_state.clean_order, 1):
            file_data = next((f for f in files if f["id"] == file_id), None)
            if file_data:
                st.write(f"{i}. {file_data['name']}")
    
    # Botão para obter ordem manualmente
    if st.button("📋 Ver Ordem Atual"):
        st.write("Ordem no session_state:", st.session_state.clean_order)
    
    # Teste de estabilidade
    st.markdown("### 🧪 Teste de Estabilidade")
    if st.session_state.clean_rerun_count <= 3:
        st.success("✅ Componente estável - sem loops detectados")
    elif st.session_state.clean_rerun_count <= 5:
        st.warning("⚠️ Poucos reruns - ainda dentro do normal")
    else:
        st.error("🚨 Muitos reruns - possível problema!")

if __name__ == "__main__":
    test_cards_clean_page()