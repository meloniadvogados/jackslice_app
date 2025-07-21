import streamlit as st
import PyPDF2
from io import BytesIO
import time
from sortable_cards_component.sortable_cards_clean import sortable_cards_clean

def pdf_merger_page():
    """
    PDF MERGER FINAL - Implementação completa
    """
    st.title("🔗 Unir PDFs")
    
    # Gerar uma key única para o uploader baseada em um contador
    if 'uploader_key' not in st.session_state:
        st.session_state.uploader_key = 0
    
    # Upload
    uploaded_files = st.file_uploader(
        "📄 Selecione arquivos PDF",
        type=['pdf'],
        accept_multiple_files=True,
        key=f"pdf_uploader_{st.session_state.uploader_key}"
    )
    
    if uploaded_files:
        st.success(f"{len(uploaded_files)} arquivo(s)")
        
        # Criar uma assinatura única baseada nos nomes e tamanhos dos arquivos
        files_signature = []
        for file in uploaded_files:
            files_signature.append(f"{file.name}_{file.size}")
        current_signature = "|".join(sorted(files_signature))
        
        # Processar arquivos se mudou a assinatura (arquivos diferentes)
        if ("pdf_files_data" not in st.session_state or 
            "files_signature" not in st.session_state or
            st.session_state.files_signature != current_signature):
            with st.spinner("📄 Analisando PDFs..."):
                st.session_state.pdf_files_data = process_uploaded_files(uploaded_files)
                st.session_state.files_signature = current_signature
                # Resetar ordem quando arquivos mudam
                if "ordem" in st.session_state:
                    del st.session_state.ordem
                if "ultimo_num_arquivos" in st.session_state:
                    del st.session_state.ultimo_num_arquivos
        
        # Dados para o componente (IGUAL Cards LIMPO)
        files = []
        for i, file_data in enumerate(st.session_state.pdf_files_data):
            files.append({
                "id": str(i),  # STRING
                "name": file_data['display_name'],
                "pages": file_data['pages'],
                "size": file_data['size_mb'],
                "type": "application/pdf"
            })
        
        # Estado da ordem (IGUAL Cards LIMPO) - só inicializar se não existir
        if "ordem" not in st.session_state:
            st.session_state.ordem = [str(i) for i in range(len(files))]
        
        # Só resetar se realmente mudou número de arquivos (evitar reset desnecessário)
        if "ultimo_num_arquivos" not in st.session_state:
            st.session_state.ultimo_num_arquivos = len(files)
        
        if st.session_state.ultimo_num_arquivos != len(files):
            st.session_state.ordem = [str(i) for i in range(len(files))]
            st.session_state.ultimo_num_arquivos = len(files)
        
        # Componente drag & drop - usar key dinâmica baseada na assinatura dos arquivos
        component_key = f"merger_final_{st.session_state.files_signature[:10]}"
        result = sortable_cards_clean(files, key=component_key, show_debug=False)
        
        # Processar resultado
        if result:
            nova_ordem = [str(x) for x in result]
            if nova_ordem != st.session_state.ordem:
                st.session_state.ordem = nova_ordem
        
        # Métricas
        if files:
            total_pages = sum(f['pages'] for f in files)
            total_size = sum(f['size'] for f in files)
            
            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric("📊 Arquivos", len(files))
            with col2:
                st.metric("📄 Páginas", total_pages)
            with col3:
                st.metric("📦 Tamanho", f"{total_size:.1f} MB")
        
        # Opções de merge
        st.markdown("---")
        st.markdown("### ⚙️ Opções")
        
        col1, col2 = st.columns(2)
        with col1:
            add_bookmarks = st.checkbox(
                "📑 Adicionar marcadores",
                value=True,
                help="Adiciona marcadores com nome de cada arquivo"
            )
        with col2:
            preserve_metadata = st.checkbox(
                "📋 Preservar metadados",
                value=True,
                help="Preserva metadados do primeiro PDF"
            )
        
        # Botão de merge
        st.markdown("---")
        if len(files) < 2:
            st.warning("⚠️ Adicione pelo menos 2 arquivos para unir")
        else:
            col1, col2 = st.columns(2)
            with col1:
                if st.button("🔗 Unir PDFs", type="primary", use_container_width=True):
                    merge_pdfs_final(uploaded_files, st.session_state.ordem, "PDFs_Unidos.pdf", add_bookmarks, preserve_metadata)
            with col2:
                if st.button("🔄 Começar Novamente", type="secondary", use_container_width=True):
                    # Limpar todos os estados relacionados ao merge
                    keys_to_clear = ['pdf_files_data', 'ordem', 'ultimo_num_arquivos', 'merge_result_final', 'files_signature']
                    for key in keys_to_clear:
                        if key in st.session_state:
                            del st.session_state[key]
                    # Incrementar a key do uploader para forçar reset
                    st.session_state.uploader_key += 1
                    st.rerun()
        
        # Resultado do merge
        if 'merge_result_final' in st.session_state:
            show_merge_result()
    


def process_uploaded_files(uploaded_files):
    """
    Processa arquivos carregados e extrai informações
    """
    files_data = []
    
    for i, file in enumerate(uploaded_files):
        try:
            # Obter informações do PDF
            pdf_info = get_pdf_info(file.getvalue())
            file_size_mb = len(file.getvalue()) / (1024 * 1024)
            
            # Nome para exibição (truncado se necessário)
            display_name = file.name[:25] + "..." if len(file.name) > 25 else file.name
            
            files_data.append({
                'original_name': file.name,
                'display_name': display_name,
                'pages': pdf_info['pages'],
                'size_mb': file_size_mb,
                'encrypted': pdf_info['encrypted']
            })
            
        except Exception as e:
            # Arquivo com problema
            files_data.append({
                'original_name': file.name,
                'display_name': f"❌ {file.name[:15]}...",
                'pages': 0,
                'size_mb': 0,
                'encrypted': False,
                'error': str(e)
            })
    
    return files_data


def get_pdf_info(file_data):
    """
    Obtém informações básicas do PDF
    """
    try:
        reader = PyPDF2.PdfReader(BytesIO(file_data))
        return {
            'pages': len(reader.pages),
            'encrypted': reader.is_encrypted,
            'metadata': reader.metadata if hasattr(reader, 'metadata') else None
        }
    except:
        return {'pages': 0, 'encrypted': False, 'metadata': None}


def merge_pdfs_final(uploaded_files, file_order, output_filename, add_bookmarks, preserve_metadata):
    """
    Une múltiplos PDFs em um único arquivo
    """
    try:
        # Progress feedback
        st.markdown("### 🔄 Processando...")
        progress_bar = st.progress(0)
        status_text = st.empty()
        
        # Verificar se há arquivos para processar
        if not uploaded_files or not file_order:
            st.error("❌ Nenhum arquivo para processar")
            return
        
        # Criar merger
        merger = PyPDF2.PdfMerger()
        
        total_files = len(file_order)
        total_pages = 0
        
        # Processar cada arquivo na ordem especificada
        for i, file_idx_str in enumerate(file_order):
            file_idx = int(file_idx_str)  # Converter string para int
            
            if file_idx >= len(uploaded_files):
                continue
                
            file = uploaded_files[file_idx]
            progress = (i + 1) / total_files
            progress_bar.progress(progress)
            status_text.text(f"📄 Processando: {file.name} ({i+1}/{total_files})")
            
            try:
                # Ler arquivo PDF
                pdf_reader = PyPDF2.PdfReader(BytesIO(file.getvalue()))
                num_pages = len(pdf_reader.pages)
                total_pages += num_pages
                
                # Adicionar ao merger
                if add_bookmarks:
                    # Adicionar com bookmark
                    outline_name = file.name.replace('.pdf', '')
                    try:
                        merger.append(pdf_reader, outline_item=outline_name)
                    except TypeError:
                        # Fallback para versões antigas do PyPDF2
                        merger.append(pdf_reader, bookmark=outline_name)
                else:
                    # Adicionar sem marcadores
                    merger.append(pdf_reader)
                
                # Pequeno delay para visualização
                time.sleep(0.1)
                
            except Exception as e:
                st.error(f"❌ Erro ao processar {file.name}: {str(e)}")
                continue
        
        # Finalizar merge
        status_text.text("📦 Finalizando merge...")
        progress_bar.progress(1.0)
        
        # Criar arquivo de saída
        output_buffer = BytesIO()
        
        # Preservar metadados do primeiro arquivo se solicitado
        if preserve_metadata and uploaded_files and file_order:
            try:
                first_file_idx = int(file_order[0])
                first_file = uploaded_files[first_file_idx]
                first_reader = PyPDF2.PdfReader(BytesIO(first_file.getvalue()))
                if hasattr(first_reader, 'metadata') and first_reader.metadata:
                    merger.add_metadata(first_reader.metadata)
            except:
                pass  # Ignorar erro de metadados
        
        # Escrever resultado
        merger.write(output_buffer)
        merger.close()
        
        # Obter dados do arquivo final
        output_buffer.seek(0)
        merged_data = output_buffer.getvalue()
        final_size = len(merged_data)
        
        # Salvar resultado no session_state
        st.session_state.merge_result_final = {
            'data': merged_data,
            'filename': output_filename,
            'total_files': total_files,
            'total_pages': total_pages,
            'final_size': final_size
        }
        
        # Limpar elementos de progresso
        progress_bar.empty()
        status_text.empty()
        
        st.rerun()  # Rerun para mostrar resultado
        
    except Exception as e:
        st.error(f"❌ Erro ao unir PDFs: {str(e)}")
        st.error("Verifique se todos os arquivos são PDFs válidos")


def show_merge_result():
    """
    Mostra o resultado do merge com botão de download
    """
    result = st.session_state.merge_result_final
    
    st.markdown("---")
    st.success("✅ PDFs unidos com sucesso!")
    
    # Estatísticas
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("📊 Arquivos Unidos", result['total_files'])
    with col2:
        st.metric("📄 Total de Páginas", result['total_pages'])
    with col3:
        st.metric("📦 Tamanho Final", f"{result['final_size'] / (1024*1024):.2f} MB")
    
    # Botões
    col1, col2 = st.columns(2)
    
    with col1:
        st.download_button(
            label="📥 Baixar PDF Unido",
            data=result['data'],
            file_name=result['filename'],
            mime="application/pdf",
            type="primary",
            use_container_width=True
        )
    
    with col2:
        if st.button("🔄 Novo Merge", help="Limpar resultado e fazer novo merge", use_container_width=True):
            del st.session_state.merge_result_final
            st.rerun()


if __name__ == "__main__":
    pdf_merger_page()