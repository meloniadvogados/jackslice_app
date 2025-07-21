import streamlit as st
import pandas as pd
from io import BytesIO
import zipfile
import hashlib
from core.ui_components import (
    pdf_preview, validate_pdf_structure,
    status_badge, enhanced_metric
)

# Cache inteligente para resultados de processamento
@st.cache_data(ttl=3600, show_spinner=False)  # Cache por 1 hora
def process_pdf_cached(pdf_data, filename):
    """Processa PDF com cache baseado no hash do conteúdo"""
    try:
        import tempfile
        import os
        
        with tempfile.NamedTemporaryFile(delete=False, suffix='.pdf') as tmp_file:
            tmp_file.write(pdf_data)
            temp_pdf_path = tmp_file.name
        
        # Executar pipeline XPTO
        from core.XPTO import XPTO
        from core.processo_numero_extractor import ProcessoNumeroExtractor
        
        # Extrair número do processo
        numero_extractor = ProcessoNumeroExtractor(temp_pdf_path)
        numero_processo = numero_extractor.extrair_numero()
        
        # Executar pipeline XPTO
        pipeline = XPTO(temp_pdf_path)
        sections = pipeline.run()
        
        # Limpar arquivo temporário
        os.unlink(temp_pdf_path)
        
        return {
            'sections': sections,
            'numero_processo': numero_processo,
            'success': True,
            'error': None
        }
        
    except Exception as e:
        return {
            'sections': [],
            'numero_processo': '',
            'success': False,
            'error': str(e)
        }

@st.cache_data(ttl=1800, show_spinner=False)  # Cache por 30 min
def get_pdf_hash(pdf_data):
    """Gera hash do PDF para cache"""
    return hashlib.md5(pdf_data).hexdigest()

@st.cache_data(ttl=3600, show_spinner=False)  # Cache por 1 hora
def get_pdf_preview_cached(pdf_data, filename):
    """Preview do PDF com cache"""
    return pdf_preview(pdf_data, filename)

@st.cache_data(ttl=3600, show_spinner=False)  # Cache por 1 hora
def get_pdf_validation_cached(pdf_data):
    """Validação do PDF com cache"""
    return validate_pdf_structure(pdf_data)

def pdf_slicer_new_page():
    st.title("✂️ Fatiar PDF")
    st.markdown("---")
    
    # CSS para botão verde de download e loading states
    st.markdown("""
    <style>
    div[data-testid="column"]:nth-child(3) button[kind="formSubmit"] {
        background-color: #28a745 !important;
        color: white !important;
        border: none !important;
    }
    div[data-testid="column"]:nth-child(3) button[kind="formSubmit"]:hover {
        background-color: #218838 !important;
    }
    
    /* Loading states mais suaves */
    .stSpinner > div > div {
        border-top-color: #28a745 !important;
        animation: spin 1s linear infinite;
    }
    
    .stProgress > div > div {
        background-color: #28a745 !important;
        transition: width 0.3s ease;
    }
    
    @keyframes spin {
        0% { transform: rotate(0deg); }
        100% { transform: rotate(360deg); }
    }
    
    /* Smooth transitions */
    .stButton button {
        transition: all 0.3s ease;
    }
    
    .stAlert {
        animation: fadeIn 0.5s ease;
    }
    
    @keyframes fadeIn {
        from { opacity: 0; transform: translateY(-10px); }
        to { opacity: 1; transform: translateY(0); }
    }
    </style>
    """, unsafe_allow_html=True)
    
    
    # Upload de PDF
    uploaded_file = st.file_uploader(
        "📄 Selecione um arquivo PDF",
        type=['pdf'],
        help="Formatos aceitos: PDF (máx. 100MB)",
        key="pdf_uploader"
    )
    
    if uploaded_file is not None:
        # Armazenar dados do PDF com cache inteligente
        pdf_data = uploaded_file.getvalue()
        pdf_hash = get_pdf_hash(pdf_data)
        
        if ('uploaded_pdf_data' not in st.session_state or 
            st.session_state.get('current_filename') != uploaded_file.name or
            st.session_state.get('pdf_hash') != pdf_hash):
            
            st.session_state.uploaded_pdf_data = pdf_data
            st.session_state.current_filename = uploaded_file.name
            st.session_state.filename_base = uploaded_file.name.replace('.pdf', '')
            st.session_state.pdf_hash = pdf_hash
            
            # Reset dados das seções quando novo arquivo é carregado
            if 'pdf_sections' in st.session_state:
                del st.session_state.pdf_sections
            if 'pdf_sections_df' in st.session_state:
                del st.session_state.pdf_sections_df
        
        # Status de upload com sucesso
        st.success(f"📄 Arquivo carregado: {uploaded_file.name}")
        
        #st.markdown("---")
        
        # Informações do arquivo e validação em expander (com cache)
        with st.expander("📋 Informações do Arquivo e Validação", expanded=False):
            # Preview do arquivo (cached)
            preview_info = get_pdf_preview_cached(st.session_state.uploaded_pdf_data, uploaded_file.name)
            
            st.markdown("---")
            
            # Validação da estrutura (cached)
            validation_info = get_pdf_validation_cached(st.session_state.uploaded_pdf_data)
        
        #st.markdown("---")
        

        
        # Botão para processar com validação
        # Considerar validação para habilitar/desabilitar botão
        is_processing_recommended = True
        if validation_info:
            is_processing_recommended = validation_info.get('is_compatible', True)
        
        button_text = "🚀 Processar PDF"
        if validation_info and validation_info.get('compatibility_score', 100) == 100:
            button_text = "🚀 Processar PDF (Estrutura Ótima)"
        elif validation_info and validation_info.get('compatibility_score', 100) >= 50:
            button_text = "🚀 Processar PDF (Estrutura Boa)"
        elif validation_info:
            button_text = "⚠️ Processar PDF (Baixa Compatibilidade)"
        
        process_button = st.button(button_text, type="primary", use_container_width=True)
        st.markdown("---")

        # Mostrar número do processo se já foi processado
        if st.session_state.get('numero_processo'):
            st.metric("Número do Processo", st.session_state.numero_processo)

        if process_button:
            
            # Container para feedback com loading state melhorado
            status_container = st.container()
            
            with status_container:
                # Loading header com animação
                st.markdown("### 🔄 Processando PDF...")
                
                # Placeholder para status detalhado
                status_placeholder = st.empty()
                
                # Verificar se já existe resultado no cache
                if 'pdf_sections' in st.session_state and st.session_state.get('pdf_hash') == pdf_hash:
                    status_placeholder.info("💾 Carregando do cache...")
                    time.sleep(0.5)
                    status_placeholder.success("✅ PDF já processado! Dados carregados do cache.")
                else:
                    # Processar com cache
                    try:
                        # Progress bar melhorado com ETA
                        progress_bar = st.progress(0)
                        progress_text = st.empty()
                        
                        import time
                        start_time = time.time()
                        
                        def update_progress(current, total):
                            progress = current / total
                            progress_bar.progress(progress)
                            
                            # Calcular ETA
                            elapsed = time.time() - start_time
                            if current > 0:
                                eta = (elapsed / current) * (total - current)
                                eta_str = f" (ETA: {eta:.1f}s)" if eta > 0 else ""
                            else:
                                eta_str = ""
                            
                            progress_text.text(f"📖 Processando página {current} de {total}{eta_str}")
                            
                            # Status detalhado
                            status_placeholder.info(f"⏳ Progresso: {current}/{total} páginas processadas ({progress:.1%})")
                        
                        # Executar pipeline XPTO com cache
                        status_placeholder.info("🔍 Analisando estrutura do PDF...")
                        with st.spinner("🔍 Analisando estrutura do PDF..."):
                            # Usar função cached
                            result = process_pdf_cached(st.session_state.uploaded_pdf_data, uploaded_file.name)
                            
                            if result['success']:
                                st.session_state.pdf_sections = result['sections']
                                st.session_state.numero_processo = result['numero_processo'] or ""
                                
                                if result['numero_processo']:
                                    status_placeholder.success(f"📝 Número do processo encontrado: {result['numero_processo']}")
                                else:
                                    status_placeholder.warning("⚠️ Número do processo não encontrado")
                                
                                if result['sections']:
                                    status_placeholder.success(f"✅ PDF processado com sucesso! Encontradas {len(result['sections'])} seções.")
                                else:
                                    status_placeholder.warning("⚠️ Nenhuma seção encontrada no PDF. Verifique se o arquivo possui um sumário/índice.")
                            else:
                                raise Exception(result['error'])
                        
                        # Limpar elementos de progresso com delay suave
                        time.sleep(0.5)  # Pequeno delay para visualização
                        progress_bar.empty()
                        progress_text.empty()
                        
                    except Exception as e:
                        st.error(f"❌ Erro ao processar PDF: {str(e)}")
                        st.session_state.pdf_sections = []
                        st.session_state.numero_processo = ""
                
                # Limpar status após 2 segundos
                time.sleep(2)
                status_placeholder.empty()
            
            # Recriar DataFrame
            if 'pdf_sections_df' in st.session_state:
                del st.session_state.pdf_sections_df
            st.rerun()
    
    # Só mostrar seções se tiver PDF carregado E processado
    if uploaded_file is not None and 'pdf_sections' in st.session_state:
        st.markdown("### 📋 Seções do PDF")
        
        # Inicializar DataFrame das seções se não existir
        if 'pdf_sections_df' not in st.session_state:
            df_data = []
            for i, section in enumerate(st.session_state.pdf_sections):
                df_data.append({
                    "Selecionar": False,
                    "ID": section.get("id", ""),
                    "Data": section.get("data", ""),
                    "Documento": section.get("documento", ""),
                    "Tipo": section.get("tipo", ""),
                    "Pág. Inicial": section.get("pagina_inicial", ""),
                    "Pág. Final": section.get("pagina_final", ""),
                    "idx_interno": i
                })
            st.session_state.pdf_sections_df = pd.DataFrame(df_data)
        
        # Usar a MESMA lógica do teste de sessão que funcionou
        with st.form("pdf_sections_form"):
            edited_df = st.data_editor(
                st.session_state.pdf_sections_df,
                column_config={
                    "Selecionar": st.column_config.CheckboxColumn(
                        "Sel.",
                        help="Selecione as seções para download",
                        default=False,
                    ),
                    "ID": st.column_config.TextColumn("ID", width="small"),
                    "Data": st.column_config.TextColumn("Data", width="small"),
                    "Documento": st.column_config.TextColumn("Documento", width="large"),
                    "Tipo": st.column_config.TextColumn("Tipo", width="medium"),
                    "Pág. Inicial": st.column_config.NumberColumn("Pág. Inicial", width="small"),
                    "Pág. Final": st.column_config.NumberColumn("Pág. Final", width="small"),
                    "idx_interno": None
                },
                hide_index=True,
                use_container_width=True,
                height=600,
                key="pdf_sections_editor"
            )
        
            col1, col2, col3 = st.columns([2, 1, 2])
            with col1:
                subcol1, subcol2 = st.columns([1, 1], gap="small")
                with subcol1:
                    select_all = st.form_submit_button("✅ Selecionar Todas")
                with subcol2:
                    deselect_all = st.form_submit_button("❌ Desmarcar Todas")
            with col2:
                st.write("")  # Espaço vazio
            with col3:
                download_btn = st.form_submit_button("📦 Baixar Selecionadas", use_container_width=True)
    
        # Processar form (agora incluindo download)
            if select_all:
                st.session_state.pdf_sections_df = edited_df
                st.session_state.pdf_sections_df["Selecionar"] = True
                st.rerun()
            elif deselect_all:
                st.session_state.pdf_sections_df = edited_df
                st.session_state.pdf_sections_df["Selecionar"] = False
                st.rerun()
            elif download_btn:
                # Coletar seções selecionadas
                selected_sections = []
                try:
                    for _, row in edited_df.iterrows():
                        if "Selecionar" in row and row["Selecionar"]:
                            section_idx = row["idx_interno"]
                            selected_sections.append(st.session_state.pdf_sections[section_idx])
                except Exception as e:
                    st.error(f"Erro ao coletar seleções: {e}")
                    selected_sections = []
                
                if selected_sections:
                    
                    try:
                        # Usar StatelessFileManager para extração real
                        with st.spinner("📦 Gerando seções reais do PDF..."):
                            # Import direto para garantir
                            from core.session_manager import StatelessFileManager
                            
                            zip_data = StatelessFileManager.extract_sections_to_zip(
                                st.session_state.uploaded_pdf_data,
                                selected_sections,
                                st.session_state.get('temp_file_path')
                            )
                            
                            # Nome do arquivo ZIP baseado no número do processo ou filename
                            if st.session_state.get('numero_processo'):
                                zip_filename = f"{st.session_state.numero_processo}_fatiado.zip"
                            else:
                                zip_filename = f"{st.session_state.filename_base}_fatiado.zip"
                            
                            # Salvar no session state para download fora do form
                            st.session_state.download_ready = True
                            st.session_state.zip_data = zip_data
                            st.session_state.zip_filename = zip_filename
                            
                            st.success(f"✅ {len(selected_sections)} seção(ões) extraída(s) com sucesso!")
                            
                    except Exception as e:

                        st.error(f"❌ Erro ao extrair seções: {str(e)}")
                        st.error("🔄 Tentando método alternativo...")
                        
                        # Fallback para método simulado em caso de erro
                        try:
                            zip_buffer = BytesIO()
                            with zipfile.ZipFile(zip_buffer, 'w', zipfile.ZIP_DEFLATED) as zip_file:
                                for section in selected_sections:
                                    content = f"""SEÇÃO DO PDF (FALLBACK)
ID: {section.get('id', 'N/A')}
Data: {section.get('data', 'N/A')}
Documento: {section.get('documento', 'N/A')}
Tipo: {section.get('tipo', 'N/A')}
Páginas: {section.get('pagina_inicial', 'N/A')} - {section.get('pagina_final', 'N/A')}

[Erro na extração real - usando fallback]
"""
                                    filename = f"{section.get('id', 'item')}_{section.get('documento', 'documento').replace(' ', '_')}.txt"
                                    zip_file.writestr(filename, content)
                            
                            zip_buffer.seek(0)
                            
                            st.session_state.download_ready = True
                            st.session_state.zip_data = zip_buffer.getvalue()
                            st.session_state.zip_filename = f"{st.session_state.filename_base}_fallback.zip"
                            
                            st.warning(f"⚠️ {len(selected_sections)} seção(ões) gerada(s) com método fallback")
                            
                        except Exception as e2:
                            st.error(f"❌ Erro crítico: {str(e2)}")
                else:
                    st.warning("⚠️ Nenhuma seção selecionada")
    
        st.markdown("---")
        
        # Botão de download fora do form
        if st.session_state.get('download_ready', False):
            st.success("✅ Arquivo pronto para download!")
            st.download_button(
                label="📥 Baixar ZIP das Seções",
                data=st.session_state.zip_data,
                file_name=st.session_state.zip_filename,
                mime="application/zip",
                type="primary",
                use_container_width=True
            )
        
        # Mostrar contador usando edited_df (dados atuais)
        try:
            selected_count = edited_df["Selecionar"].sum()
            if selected_count > 0:
                st.info(f"📊 {selected_count} seção(ões) selecionada(s) (dados atuais)")
            else:
                pass  # Mensagem removida conforme solicitado
        except:
            pass  # Mensagem removida conforme solicitado
    else:
        pass  # Mensagem removida conforme solicitado
    
