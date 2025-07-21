import streamlit as st
import PyPDF2
from io import BytesIO
import time
from sortable_cards_component.sortable_cards_manual import sortable_cards_manual

def pdf_merger_page():
    """
    Página principal do merge de PDFs - Interface limpa e eficiente
    """
    st.title("🔗 Unir PDFs")
    st.markdown("---")
    
    # Informações sobre a ferramenta
    #st.info("📌 **Funcionalidade:** Combine múltiplos PDFs em um único arquivo na ordem desejada")
    
    # 1. 📤 Upload de múltiplos arquivos
    uploaded_files = st.file_uploader(
        "📄 Selecione os PDFs para unir:",
        type=['pdf'],
        accept_multiple_files=True,
        help="Selecione múltiplos arquivos PDF. Você pode reordenar depois."
    )
    
    if uploaded_files:
        # Verificar se os arquivos mudaram (nome, quantidade e conteúdo)
        current_files_hash = [(f.name, len(f.getvalue())) for f in uploaded_files]
        cached_files_hash = st.session_state.get('pdf_cached_files_hash', [])
        
        if current_files_hash != cached_files_hash:
            # Arquivos mudaram - reprocessar tudo
            st.session_state.pdf_files_data = process_uploaded_files(uploaded_files)
            st.session_state.pdf_order = list(range(len(uploaded_files)))
            st.session_state.pdf_cached_files_hash = current_files_hash
        
        # Verificação adicional se a quantidade não bate
        if len(st.session_state.get('pdf_files_data', [])) != len(uploaded_files):
            st.session_state.pdf_files_data = process_uploaded_files(uploaded_files)
            st.session_state.pdf_order = list(range(len(uploaded_files)))
        
        st.success(f"📊 {len(uploaded_files)} arquivo(s) carregado(s)")
        
        # Botão para forçar atualização se necessário
        if len(st.session_state.get('pdf_files_data', [])) != len(uploaded_files):
            if st.button("🔄 Atualizar lista de arquivos"):
                st.session_state.pdf_files_data = process_uploaded_files(uploaded_files)
                st.session_state.pdf_order = list(range(len(uploaded_files)))
                st.rerun()
        
        # 2. 👀 Visualização e 3. 🔄 Reordenação com sortable cards
        st.markdown("### 📋 Arquivos Carregados - Arraste para reordenar")
        
        # Preparar dados para o componente sortable
        sortable_files = []
        
        # Usar todos os arquivos disponíveis, não apenas os da ordem
        for i in range(len(st.session_state.pdf_files_data)):
            file_data = st.session_state.pdf_files_data[i]
            sortable_files.append({
                "id": i,
                "name": file_data['display_name'],
                "pages": file_data['pages'],
                "size": file_data['size_mb'],
                "type": "application/pdf"
            })
        
        # Renderizar componente sortable com key dinâmica para forçar atualização
        component_key = f"pdf_merger_cards_{len(sortable_files)}_{hash(str(sortable_files))}"
        result = sortable_cards_manual(sortable_files, command=None, key=component_key)
        
        st.markdown("---")
        
        # 4. ⚙️ Opções simples
        st.markdown("### ⚙️ Opções de Merge")
        
        # Nome fixo do arquivo final
        output_filename = "PDFs_Unidos.pdf"
        
        # Opções simples
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
        
        st.markdown("---")
        
        # 5. 🔗 Processar e 6. 📥 Download
        if st.button("🔗 Unir PDFs", type="primary", use_container_width=True):
            # Capturar ordem automaticamente (fazer o papel dos 2 cliques)
            with st.spinner("📥 Capturando ordem dos cards..."):
                # Primeiro "clique"
                result1 = sortable_cards_manual(sortable_files, command="get_order", key=f"{component_key}_capture1")
                
                # Segundo "clique" 
                result2 = sortable_cards_manual(sortable_files, command="get_order", key=f"{component_key}_capture2")
                
                # Usar o resultado do segundo clique (que é o correto)
                if result2 and isinstance(result2, list):
                    final_order = [int(x) for x in result2]
                    st.session_state.pdf_order = final_order
                    st.success("✅ Ordem capturada automaticamente!")
                elif result1 and isinstance(result1, list):
                    final_order = [int(x) for x in result1]
                    st.session_state.pdf_order = final_order
                    st.success("✅ Ordem capturada automaticamente!")
            
            # Fazer o merge com a ordem correta
            merge_pdfs(uploaded_files, st.session_state.pdf_order, output_filename, 
                      add_bookmarks, preserve_metadata)
        
        # Debug para verificar session_state
        st.write(f"DEBUG: merge_result no session_state: {'merge_result' in st.session_state}")
        
        # Mostrar resultado do merge se existir
        if 'merge_result' in st.session_state:
            result = st.session_state.merge_result
            st.write("DEBUG: Exibindo resultado")
            
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
            
            # Botão de download
            st.download_button(
                label="📥 Baixar PDF Unido",
                data=result['data'],
                file_name=result['filename'],
                mime="application/pdf",
                type="primary",
                use_container_width=True
            )
            
            # Botão para limpar resultado
            if st.button("🔄 Novo Merge", help="Limpar resultado e fazer novo merge"):
                del st.session_state.merge_result
                st.rerun()
    
    else:
        # Instruções quando não há arquivos
        st.markdown("""
        ### 📖 Como usar:
        
        1. **📤 Upload**: Selecione múltiplos arquivos PDF
        2. **👀 Visualização**: Veja os arquivos como cards organizados
        3. **🔄 Reordenação**: Arraste e solte os cards para organizar a ordem
        4. **⚙️ Configuração**: Escolha nome do arquivo e opções simples
        5. **🔗 Processamento**: Clique em "Unir PDFs" para processar
        6. **📥 Download**: Baixe o arquivo resultante
        
        ### ✨ Funcionalidades:
        - 📋 Upload múltiplo de arquivos
        - 🔄 Reordenação visual por drag & drop
        - 📑 Marcadores automáticos
        - 📋 Preservação de metadados
        - ⚡ Interface limpa e eficiente
        """)

def process_uploaded_files(uploaded_files):
    """
    Processa arquivos carregados e extrai informações (com cache)
    """
    files_data = []
    
    for i, file in enumerate(uploaded_files):
        try:
            # Obter informações do PDF
            pdf_info = get_pdf_info(file.getvalue())
            file_size_mb = len(file.getvalue()) / (1024 * 1024)
            
            # Nome para exibição (truncado se necessário)
            display_name = file.name[:20] + "..." if len(file.name) > 20 else file.name
            
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

def merge_pdfs(uploaded_files, file_order, output_filename, add_bookmarks, preserve_metadata):
    """
    Une múltiplos PDFs em um único arquivo - Implementação limpa
    """
    try:
        st.write("DEBUG: Iniciando merge_pdfs")
        # Container para feedback
        st.markdown("### 🔄 Processando...")
        
        # Verificar se há arquivos para processar
        if not uploaded_files or not file_order:
            st.error("❌ Nenhum arquivo para processar")
            return
        
        # Progress bar
        progress_bar = st.progress(0)
        status_text = st.empty()
        
        # Criar merger
        merger = PyPDF2.PdfMerger()
        
        total_files = len(file_order)
        total_pages = 0
        
        # Processar cada arquivo na ordem especificada
        for i, file_idx in enumerate(file_order):
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
                    # Adicionar com outline_item (nova sintaxe PyPDF2)
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
                first_file = uploaded_files[file_order[0]]
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
        
        # Salvar resultado no session_state para persistir após rerun
        st.session_state.merge_result = {
            'data': merged_data,
            'filename': output_filename,
            'total_files': total_files,
            'total_pages': total_pages,
            'final_size': final_size
        }
        
        st.write("DEBUG: Resultado salvo no session_state")
        st.write(f"DEBUG: Tamanho dos dados: {len(merged_data)} bytes")
        
        # Limpar elementos de progresso
        progress_bar.empty()
        status_text.empty()
        
    except Exception as e:
        st.error(f"❌ Erro ao unir PDFs: {str(e)}")
        st.error("Verifique se todos os arquivos são PDFs válidos")

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