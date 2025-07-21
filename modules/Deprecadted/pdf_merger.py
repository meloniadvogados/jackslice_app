import streamlit as st
import PyPDF2
from io import BytesIO
import tempfile
import os
import time

def pdf_merger_page():
    st.title("🔗 Unir PDFs")
    st.markdown("---")
    
    # CSS simples que funciona
    st.markdown("""
    <style>
    .pdf-grid {
        display: flex;
        flex-wrap: wrap;
        gap: 10px;
        margin: 20px 0;
    }
    
    .pdf-card {
        border: 2px solid #ddd;
        border-radius: 10px;
        padding: 15px;
        background: white;
        text-align: center;
        cursor: move;
        transition: all 0.3s ease;
        position: relative;
        width: 150px;
        height: 160px;
        display: inline-block;
    }
    
    .pdf-card:hover {
        border-color: #4a90e2;
        box-shadow: 0 4px 8px rgba(0,0,0,0.1);
    }
    
    .pdf-card.dragging {
        opacity: 0.5;
    }
    
    .pdf-card.drag-over {
        border-color: #28a745;
        background-color: #f0f9ff;
    }
    
    .pdf-order {
        position: absolute;
        top: -8px;
        right: -8px;
        background: #4a90e2;
        color: white;
        border-radius: 50%;
        width: 20px;
        height: 20px;
        display: flex;
        align-items: center;
        justify-content: center;
        font-size: 12px;
        font-weight: bold;
    }
    
    .pdf-icon {
        font-size: 40px;
        margin: 10px 0;
        color: #4a90e2;
    }
    
    .pdf-name {
        font-weight: bold;
        font-size: 11px;
        margin: 5px 0;
        line-height: 1.2;
    }
    
    .pdf-info {
        font-size: 9px;
        color: #666;
        margin: 2px 0;
    }
    </style>
    """, unsafe_allow_html=True)
    
    # Informações sobre a ferramenta
    st.info("📌 **Funcionalidade:** Combine múltiplos PDFs em um único arquivo na ordem desejada")
    
    # Upload de múltiplos arquivos
    uploaded_files = st.file_uploader(
        "📄 Selecione os PDFs para unir:",
        type=['pdf'],
        accept_multiple_files=True,
        help="Selecione múltiplos arquivos PDF. Você pode reordenar depois."
    )
    
    if uploaded_files:
        # Inicializar ordem dos arquivos no session_state
        if 'file_order' not in st.session_state or len(st.session_state.file_order) != len(uploaded_files):
            st.session_state.file_order = list(range(len(uploaded_files)))
        
        st.success(f"📊 {len(uploaded_files)} arquivo(s) carregado(s)")
        
        # Mostrar arquivos com drag & drop
        st.markdown("### 📋 Arquivos Carregados - Arraste para reordenar")
        
        try:
            from streamlit_sortables import sort_items
            
            # Preparar dados para o componente sortable
            sortable_items = []
            for i, file_idx in enumerate(st.session_state.file_order):
                if file_idx >= len(uploaded_files):
                    continue
                    
                file = uploaded_files[file_idx]
                file_size = len(file.getvalue()) / (1024 * 1024)  # MB
                pdf_info = get_pdf_info(file.getvalue())
                display_name = file.name[:20] + "..." if len(file.name) > 20 else file.name
                
                # Criar item para o sortable
                item = {
                    'header': f'📄 {display_name}',
                    'items': [
                        f'📄 {pdf_info["pages"]} páginas',
                        f'💾 {file_size:.1f} MB'
                    ],
                    'file_idx': file_idx,  # Manter referência ao arquivo original
                    'original_name': file.name
                }
                sortable_items.append(item)
            
            # Componente sortable
            sorted_items = sort_items(sortable_items, multi_containers=False)
            
            # Atualizar a ordem no session_state baseado no resultado
            if sorted_items:
                new_order = [item['file_idx'] for item in sorted_items]
                if new_order != st.session_state.file_order:
                    st.session_state.file_order = new_order
                    st.rerun()
            
            # Mostrar ordem atual
            st.success(f"Ordem atual: {', '.join([f'{i+1}. {uploaded_files[idx].name}' for i, idx in enumerate(st.session_state.file_order)])}")
            
        except ImportError:
            st.error("❌ streamlit-sortables não está instalado. Execute: `pip install streamlit-sortables`")
            
            # Fallback: usar colunas simples
            st.markdown("**Visualização sem drag & drop:**")
            
            num_cols = min(len(uploaded_files), 4)
            cols = st.columns(num_cols)
            
            for i, file_idx in enumerate(st.session_state.file_order):
                if file_idx >= len(uploaded_files):
                    continue
                    
                file = uploaded_files[file_idx]
                file_size = len(file.getvalue()) / (1024 * 1024)  # MB
                pdf_info = get_pdf_info(file.getvalue())
                display_name = file.name[:15] + "..." if len(file.name) > 15 else file.name
                
                with cols[i % num_cols]:
                    st.markdown(f'''
                    <div style="border: 2px solid #ddd; border-radius: 10px; padding: 15px; 
                               background: white; text-align: center; height: 160px; position: relative;">
                        <div style="position: absolute; top: -8px; right: -8px; 
                                   background: #4a90e2; color: white; border-radius: 50%; 
                                   width: 24px; height: 24px; display: flex; align-items: center; 
                                   justify-content: center; font-size: 12px; font-weight: bold;">
                            {i+1}
                        </div>
                        <div style="font-size: 40px; margin: 10px 0; color: #4a90e2;">📄</div>
                        <div style="font-weight: bold; font-size: 12px; margin: 5px 0;">{display_name}</div>
                        <div style="font-size: 10px; color: #666; margin: 2px 0;">{pdf_info['pages']} páginas</div>
                        <div style="font-size: 10px; color: #666; margin: 2px 0;">{file_size:.1f} MB</div>
                    </div>
                    ''', unsafe_allow_html=True)
        
        st.markdown("---")
        
        # Controles de reordenação
        st.markdown("### 🔧 Reordenar Arquivos")
        
        # Seletor de arquivo para mover
        col1, col2 = st.columns([3, 1])
        
        with col1:
            selected_file = st.selectbox(
                "Selecione um arquivo para mover:",
                options=range(len(uploaded_files)),
                format_func=lambda x: f"{st.session_state.file_order.index(x)+1}. {uploaded_files[x].name}",
                help="Escolha o arquivo que deseja reordenar"
            )
        
        with col2:
            current_pos = st.session_state.file_order.index(selected_file)
            st.metric("Posição atual", current_pos + 1)
        
        # Controles de movimento
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            if st.button("⬆️ Mover para cima"):
                current_pos = st.session_state.file_order.index(selected_file)
                if current_pos > 0:
                    st.session_state.file_order[current_pos], st.session_state.file_order[current_pos-1] = \
                        st.session_state.file_order[current_pos-1], st.session_state.file_order[current_pos]
                    st.rerun()
        
        with col2:
            if st.button("⬇️ Mover para baixo"):
                current_pos = st.session_state.file_order.index(selected_file)
                if current_pos < len(st.session_state.file_order) - 1:
                    st.session_state.file_order[current_pos], st.session_state.file_order[current_pos+1] = \
                        st.session_state.file_order[current_pos+1], st.session_state.file_order[current_pos]
                    st.rerun()
        
        with col3:
            if st.button("⬆️ Mover para início"):
                current_pos = st.session_state.file_order.index(selected_file)
                if current_pos > 0:
                    file_to_move = st.session_state.file_order.pop(current_pos)
                    st.session_state.file_order.insert(0, file_to_move)
                    st.rerun()
        
        with col4:
            if st.button("⬇️ Mover para fim"):
                current_pos = st.session_state.file_order.index(selected_file)
                if current_pos < len(st.session_state.file_order) - 1:
                    file_to_move = st.session_state.file_order.pop(current_pos)
                    st.session_state.file_order.append(file_to_move)
                    st.rerun()
        
        # Controles gerais
        st.markdown("### 🔄 Controles Gerais")
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            if st.button("🔄 Inverter Ordem"):
                st.session_state.file_order = list(reversed(st.session_state.file_order))
                st.rerun()
        
        with col2:
            if st.button("🔀 Ordem Aleatória"):
                import random
                random.shuffle(st.session_state.file_order)
                st.rerun()
        
        with col3:
            if st.button("↩️ Resetar Ordem"):
                st.session_state.file_order = list(range(len(uploaded_files)))
                st.rerun()
        
        st.markdown("---")
        
        # Opções de merge
        st.markdown("### ⚙️ Opções de Merge")
        
        col1, col2 = st.columns(2)
        
        with col1:
            add_bookmarks = st.checkbox(
                "📑 Adicionar marcadores",
                value=True,
                help="Adiciona marcadores (bookmarks) com o nome de cada arquivo"
            )
            
            preserve_metadata = st.checkbox(
                "📋 Preservar metadados",
                value=True,
                help="Preserva metadados do primeiro PDF no arquivo final"
            )
        
        with col2:
            add_separators = st.checkbox(
                "📄 Adicionar páginas separadoras",
                value=False,
                help="Adiciona uma página em branco entre cada PDF"
            )
            
            optimize_output = st.checkbox(
                "⚡ Otimizar saída",
                value=True,
                help="Tenta otimizar o PDF resultante"
            )
        
        # Nome do arquivo final
        st.markdown("### 📝 Nome do Arquivo Final")
        output_filename = st.text_input(
            "Nome do arquivo:",
            value="PDFs_Unidos.pdf",
            help="Nome do arquivo PDF resultante"
        )
        
        # Verificar se o nome termina com .pdf
        if not output_filename.endswith('.pdf'):
            output_filename += '.pdf'
        
        # Botão para unir PDFs
        if st.button("🔗 Unir PDFs", type="primary", use_container_width=True):
            merge_pdfs(uploaded_files, st.session_state.file_order, output_filename, 
                      add_bookmarks, preserve_metadata, add_separators, optimize_output)
    
    else:
        # Instruções quando não há arquivos
        st.markdown("""
        ### 📖 Como usar:
        
        1. **Upload**: Selecione múltiplos arquivos PDF
        2. **Reordenar**: Arraste e solte os ícones para organizar a ordem
        3. **Configurar**: Escolha as opções de merge desejadas
        4. **Unir**: Clique em "Unir PDFs" para processar
        5. **Download**: Baixe o arquivo resultante
        
        ### ✨ Funcionalidades:
        - 📋 Upload múltiplo de arquivos
        - 🔄 Reordenação por drag & drop
        - 📑 Marcadores automáticos
        - 📄 Páginas separadoras opcionais
        - 📋 Preservação de metadados
        - ⚡ Otimização automática
        """)

def merge_pdfs(uploaded_files, file_order, output_filename, add_bookmarks, preserve_metadata, add_separators, optimize_output):
    """
    Une múltiplos PDFs em um único arquivo
    """
    try:
        # Container para feedback
        status_container = st.container()
        
        with status_container:
            st.markdown("### 🔄 Unindo PDFs...")
            
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
                        bookmark_name = file.name.replace('.pdf', '')
                        merger.append(pdf_reader, bookmark=bookmark_name)
                    else:
                        # Adicionar sem bookmark
                        merger.append(pdf_reader)
                    
                    # Adicionar página separadora se solicitado
                    if add_separators and i < len(file_order) - 1:
                        # Criar página em branco simples
                        try:
                            blank_page = create_blank_page()
                            if blank_page:
                                merger.append(blank_page)
                        except:
                            pass  # Ignorar erro na criação da página separadora
                    
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
            if preserve_metadata and uploaded_files:
                try:
                    first_file = uploaded_files[file_order[0]]
                    first_reader = PyPDF2.PdfReader(BytesIO(first_file.getvalue()))
                    if first_reader.metadata:
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
            
            # Limpar elementos de progresso
            progress_bar.empty()
            status_text.empty()
            
            # Mostrar resultados
            st.success("✅ PDFs unidos com sucesso!")
            
            # Estatísticas
            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric("📊 Arquivos Unidos", total_files)
            with col2:
                st.metric("📄 Total de Páginas", total_pages)
            with col3:
                st.metric("📦 Tamanho Final", f"{final_size / (1024*1024):.2f} MB")
            
            # Botão de download
            st.download_button(
                label="📥 Baixar PDF Unido",
                data=merged_data,
                file_name=output_filename,
                mime="application/pdf",
                type="primary",
                use_container_width=True
            )
            
    except Exception as e:
        st.error(f"❌ Erro ao unir PDFs: {str(e)}")
        st.error("Verifique se todos os arquivos são PDFs válidos")

def create_blank_page():
    """
    Cria uma página em branco para usar como separador
    """
    try:
        # Criar PDF temporário com página em branco
        from reportlab.pdfgen import canvas
        from reportlab.lib.pagesizes import letter
        
        buffer = BytesIO()
        c = canvas.Canvas(buffer, pagesize=letter)
        
        # Adicionar texto indicativo (opcional)
        c.setFont("Helvetica", 12)
        c.drawCentredText(letter[0]/2, letter[1]/2, "--- Página Separadora ---")
        
        c.save()
        buffer.seek(0)
        
        return PyPDF2.PdfReader(buffer)
        
    except ImportError:
        # Fallback: criar página simples sem reportlab
        return None
    except Exception:
        return None

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