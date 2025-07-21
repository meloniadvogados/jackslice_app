import streamlit as st
import PyPDF2
from io import BytesIO
import time
from sortable_cards_component.sortable_cards_clean import sortable_cards_clean

def pdf_merger_page():
    """
    🔗 UNIR PDFs - Versão LIMPA com componente CLEAN
    ===============================================
    
    ✨ FUNCIONALIDADES:
    - Upload múltiplo com detecção inteligente de mudanças
    - Drag & Drop sem loops com componente CLEAN
    - Métricas em tempo real (arquivos, páginas, tamanho)
    - Cache inteligente para performance
    - Progress bar com feedback detalhado
    - Bookmarks e metadados automáticos
    - Download direto e resultado persistente
    - Interface simplificada e limpa
    """
    st.title("🔗 Unir PDFs")
    st.markdown("---")
    
    # Inicializar session_state
    if 'pdf_files_data' not in st.session_state:
        st.session_state.pdf_files_data = []
    if 'pdf_order' not in st.session_state:
        st.session_state.pdf_order = []  # Será preenchida como strings quando houver arquivos
    if 'pdf_cached_files_hash' not in st.session_state:
        st.session_state.pdf_cached_files_hash = []
    
    # ==========================================
    # SEÇÃO 1: MÉTRICAS E UPLOAD DE ARQUIVOS  
    # ==========================================
    
    # Upload principal
    uploaded_files = st.file_uploader(
        "📄 Selecione PDFs para unir:",
        type=['pdf'],
        accept_multiple_files=True,
        help="💡 Dica: Selecione múltiplos arquivos de uma vez",
        key="main_uploader"
    )
    
    # ==========================================
    # PROCESSAMENTO INTELIGENTE DE ARQUIVOS
    # ==========================================
    
    # Processamento de arquivos carregados
    if uploaded_files:
        current_files_hash = [(f.name, len(f.getvalue())) for f in uploaded_files]
        cached_files_hash = st.session_state.pdf_cached_files_hash
        
        if current_files_hash != cached_files_hash:
            # Arquivos mudaram - reprocessar tudo
            with st.spinner("🔄 Processando arquivos carregados..."):
                st.session_state.pdf_files_data = process_uploaded_files(uploaded_files)
                # ORDEM COMO STRING igual no Cards LIMPO
                st.session_state.pdf_order = [str(i) for i in range(len(uploaded_files))]
                st.session_state.pdf_cached_files_hash = current_files_hash
                # Limpar merge anterior se existir
                if 'merge_result' in st.session_state:
                    del st.session_state.merge_result
    

    # ==========================================
    # SEÇÃO 2: VISUALIZAÇÃO E ORGANIZAÇÃO
    # ==========================================
    
    if st.session_state.pdf_files_data:
        # Métricas
        total_files = len(st.session_state.pdf_files_data)
        total_pages = sum(f.get('pages', 0) for f in st.session_state.pdf_files_data)
        total_size = sum(f.get('size_mb', 0) for f in st.session_state.pdf_files_data)
        
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric("📊 Arquivos", total_files)
        with col2:
            st.metric("📄 Páginas", total_pages)
        with col3:
            st.metric("📦 Tamanho", f"{total_size:.1f} MB")
        with col4:
            if st.button("🗑️ Limpar", help="Remove todos os arquivos"):
                clear_all_files()
                st.rerun()
        
        st.markdown("### 📋 Arquivos Carregados - Arraste para reordenar")
        
        # Preparar dados para o componente CLEAN (IDs como STRING - igual no Cards LIMPO)
        sortable_files = []
        for i, file_data in enumerate(st.session_state.pdf_files_data):
            sortable_files.append({
                "id": str(i),  # STRING igual no Cards LIMPO
                "name": file_data['display_name'],
                "pages": file_data['pages'],
                "size": file_data['size_mb'],
                "type": "application/pdf"
            })
        
        # ==========================================
        # COMPONENTE DRAG & DROP CLEAN - SEM LOOPS!
        # ==========================================
        component_key = f"pdf_merger_clean_v2_{len(sortable_files)}"
        result = sortable_cards_clean(sortable_files, key=component_key, show_debug=True)
        
        # Processar resultado - EXATAMENTE igual no Cards LIMPO
        if result:
            # MANTER como STRING igual no Cards LIMPO
            st.session_state.pdf_order = [str(x) for x in result]
            st.success(f"✅ Nova ordem detectada: {result}")
            # NÃO faz rerun - deixa o Streamlit decidir (igual Cards LIMPO)
            # Limpar merge anterior ao reordenar
            if 'merge_result' in st.session_state:
                del st.session_state.merge_result
        
        
        # ==========================================
        # SEÇÃO 3: OPÇÕES DE MERGE
        # ==========================================
        st.markdown("---")
        st.markdown("### ⚙️ Opções de Merge")
        
        # Nome fixo do arquivo
        output_filename = "PDFs_Unidos.pdf"
        
        col1, col2 = st.columns(2)
        
        with col1:
            add_bookmarks = st.checkbox(
                "📑 Adicionar marcadores",
                value=True,
                help="Adiciona marcadores (bookmarks) com o nome de cada arquivo"
            )
        
        with col2:
            preserve_metadata = st.checkbox(
                "📋 Preservar metadados",
                value=True,
                help="Preserva metadados do primeiro PDF no arquivo final"
            )
        
        # ==========================================
        # SEÇÃO 4: EXECUTAR MERGE
        # ==========================================
        st.markdown("---")
        
        if len(st.session_state.pdf_order) < 2:
            st.warning("⚠️ Adicione pelo menos 2 arquivos para fazer o merge")
        else:
            if st.button("🔗 Unir PDFs", type="primary", use_container_width=True):
                # Converter ordem de strings para ints para o merge
                order_as_ints = [int(x) for x in st.session_state.pdf_order]
                # Executar merge com ordem atual
                merge_pdfs_clean(st.session_state.pdf_files_data, order_as_ints, 
                               output_filename, add_bookmarks, preserve_metadata)
    
    # ==========================================
    # SEÇÃO 5: RESULTADO DO MERGE
    # ==========================================
    
    # DEBUG: Verificar se resultado existe
    st.write(f"🔍 DEBUG: merge_result existe? {'merge_result' in st.session_state}")
    if 'merge_result' in st.session_state:
        st.write(f"📋 DEBUG: Tamanho dos dados: {len(st.session_state.merge_result.get('data', []))} bytes")
    
    # Mostrar resultado se existir
    if 'merge_result' in st.session_state:
        result_data = st.session_state.merge_result
        
        st.markdown("---")
        st.success("🎉 PDFs unidos com sucesso!")
        
        # Estatísticas detalhadas
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("📊 Arquivos Unidos", result_data['total_files'])
        with col2:
            st.metric("📄 Total de Páginas", result_data['total_pages'])
        with col3:
            st.metric("📦 Tamanho Final", f"{result_data['final_size'] / (1024*1024):.2f} MB")
        
        # Botões de ação
        col1, col2 = st.columns(2)
        
        with col1:
            st.download_button(
                label="📥 Baixar PDF Unido",
                data=result_data['data'],
                file_name=result_data['filename'],
                mime="application/pdf",
                type="primary",
                use_container_width=True
            )
        
        with col2:
            if st.button("🔄 Novo Merge", help="Limpar resultado e fazer novo merge", use_container_width=True):
                del st.session_state.merge_result
                st.rerun()
    
    # ==========================================
    # SEÇÃO 6: INSTRUÇÕES (quando vazio)
    # ==========================================
    else:
        # Instruções quando não há arquivos
        st.markdown("""
        ### 📖 Como usar esta versão LIMPA:
        
        #### 📤 **Upload Simples:**
        - **Upload múltiplo**: Selecione vários PDFs de uma vez
        - **Detecção automática**: Sistema detecta mudanças e atualiza automaticamente
        - **Métricas em tempo real**: Veja arquivos, páginas e tamanho total
        
        #### 🔄 **Drag & Drop LIMPO:**
        - **Arraste cards**: Reordene arquivos sem loops ou travamentos
        - **Atualização instantânea**: Ordem muda em tempo real
        - **Interface estável**: Zero reruns desnecessários
        
        #### ⚙️ **Merge Simples:**
        - **Nome fixo**: "PDFs_Unidos.pdf" automático
        - **Bookmarks automáticos**: Marcadores com nome de cada arquivo
        - **Preservar metadados**: Mantém informações do primeiro PDF
        
        #### 🎯 **Interface Otimizada:**
        - **Cache inteligente**: Performance otimizada
        - **Progress detalhado**: Acompanhe cada etapa do processo
        - **Resultado persistente**: Download disponível após merge
        - **Design limpo**: Interface simplificada e funcional
        
        ### ✨ **Melhorias desta versão LIMPA:**
        - 🚀 **Zero loops** - drag & drop completamente estável
        - 📊 **Métricas integradas** - informações sempre visíveis
        - 🧹 **Interface ultra simplificada** - sem campos desnecessários
        - ⚡ **Performance otimizada** - nome fixo e processamento eficiente
        """)


# ==========================================
# FUNÇÕES AUXILIARES
# ==========================================

def process_uploaded_files(uploaded_files):
    """Processa múltiplos arquivos carregados"""
    files_data = []
    
    for i, file in enumerate(uploaded_files):
        file_data = process_single_file(file)
        if file_data:
            files_data.append(file_data)
    
    return files_data

def process_single_file(file):
    """Processa um único arquivo"""
    try:
        # Obter informações do PDF
        pdf_info = get_pdf_info(file.getvalue())
        file_size_mb = len(file.getvalue()) / (1024 * 1024)
        
        # Nome para exibição (truncado se necessário)
        display_name = file.name[:25] + "..." if len(file.name) > 25 else file.name
        
        return {
            'original_name': file.name,
            'display_name': display_name,
            'pages': pdf_info['pages'],
            'size_mb': file_size_mb,
            'encrypted': pdf_info['encrypted'],
            'file_data': file.getvalue()  # Guardar os dados do arquivo
        }
        
    except Exception as e:
        # Arquivo com problema
        return {
            'original_name': file.name,
            'display_name': f"❌ {file.name[:20]}...",
            'pages': 0,
            'size_mb': 0,
            'encrypted': False,
            'error': str(e),
            'file_data': None
        }


def clear_all_files():
    """Limpa todos os arquivos"""
    st.session_state.pdf_files_data = []
    st.session_state.pdf_order = []  # Mantém como lista vazia (vai ser repreenchida como strings)
    st.session_state.pdf_cached_files_hash = []
    if 'merge_result' in st.session_state:
        del st.session_state.merge_result


def merge_pdfs_clean(files_data, file_order, output_filename, add_bookmarks, preserve_metadata):
    """
    Une múltiplos PDFs usando dados do session_state - Versão CLEAN
    """
    try:
        # Container para feedback
        st.markdown("### 🔄 Processando merge...")
        
        # Verificar se há arquivos para processar
        if not files_data or not file_order:
            st.error("❌ Nenhum arquivo para processar")
            return
        
        # Progress bar
        progress_bar = st.progress(0)
        status_text = st.empty()
        
        # Criar merger
        merger = PyPDF2.PdfMerger()
        
        total_files = len(file_order)
        total_pages = 0
        processed_files = 0
        
        
        # Processar cada arquivo na ordem especificada
        for i, file_idx in enumerate(file_order):
            if file_idx >= len(files_data):
                continue
                
            file_data = files_data[file_idx]
            
            # Verificar se o arquivo tem dados válidos
            if file_data.get('file_data') is None:
                st.warning(f"⚠️ Pulando {file_data['original_name']} - dados não disponíveis")
                continue
            
            progress = (i + 1) / total_files
            progress_bar.progress(progress)
            status_text.text(f"📄 Processando: {file_data['original_name']} ({i+1}/{total_files})")
            
            try:
                # Ler arquivo PDF dos dados salvos
                pdf_reader = PyPDF2.PdfReader(BytesIO(file_data['file_data']))
                num_pages = len(pdf_reader.pages)
                total_pages += num_pages
                processed_files += 1
                
                # Adicionar ao merger
                if add_bookmarks:
                    # Adicionar com outline_item (nova sintaxe PyPDF2)
                    outline_name = file_data['original_name'].replace('.pdf', '')
                    try:
                        merger.append(pdf_reader, outline_item=outline_name)
                    except TypeError:
                        # Fallback para versões antigas do PyPDF2
                        merger.append(pdf_reader, bookmark=outline_name)
                else:
                    # Adicionar sem marcadores
                    merger.append(pdf_reader)
                
                # Pequeno delay para visualização
                time.sleep(0.05)
                
            except Exception as e:
                st.error(f"❌ Erro ao processar {file_data['original_name']}: {str(e)}")
                continue
        
        if processed_files == 0:
            st.error("❌ Nenhum arquivo foi processado com sucesso")
            return
        
        # Finalizar merge
        status_text.text("📦 Finalizando merge...")
        progress_bar.progress(1.0)
        
        # Criar arquivo de saída
        output_buffer = BytesIO()
        
        # Preservar metadados do primeiro arquivo se solicitado
        if preserve_metadata and file_order and files_data:
            try:
                first_file_data = files_data[file_order[0]]
                if first_file_data.get('file_data'):
                    first_reader = PyPDF2.PdfReader(BytesIO(first_file_data['file_data']))
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
        st.session_state.merge_result = {
            'data': merged_data,
            'filename': output_filename,
            'total_files': processed_files,
            'total_pages': total_pages,
            'final_size': final_size
        }
        
        # DEBUG: Confirmar que resultado foi salvo
        st.success(f"✅ DEBUG: Merge concluído! {processed_files} arquivos processados, resultado salvo.")
        
        # Limpar elementos de progresso
        progress_bar.empty()
        status_text.empty()
        
        st.rerun()  # Atualizar para mostrar resultado
        
    except Exception as e:
        st.error(f"❌ Erro ao unir PDFs: {str(e)}")
        st.error("Verifique se todos os arquivos são PDFs válidos")

def get_pdf_info(file_data):
    """Obtém informações básicas do PDF"""
    try:
        reader = PyPDF2.PdfReader(BytesIO(file_data))
        return {
            'pages': len(reader.pages),
            'encrypted': reader.is_encrypted,
            'metadata': reader.metadata if hasattr(reader, 'metadata') else None
        }
    except:
        return {'pages': 0, 'encrypted': False, 'metadata': None}