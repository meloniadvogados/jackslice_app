"""
Componentes de UI melhorados para feedback visual e UX
"""

import streamlit as st
import time
from typing import Optional, Callable, Any


def show_processing_state(message: str = "Processando..."):
    """
    Exibe um estado de processamento elegante com animação
    
    Args:
        message: Mensagem a ser exibida durante o processamento
    """
    return st.markdown(f"""
    <div class="processing-state">
        <div class="custom-loader"></div>
        <div style="margin-top: 10px;">{message}</div>
    </div>
    """, unsafe_allow_html=True)


def show_success_state(message: str = "✅ Processamento concluído com sucesso!"):
    """
    Exibe um estado de sucesso com animação
    
    Args:
        message: Mensagem de sucesso
    """
    return st.markdown(f"""
    <div class="success-state">
        {message}
    </div>
    """, unsafe_allow_html=True)


def show_error_state(message: str = "❌ Erro durante o processamento"):
    """
    Exibe um estado de erro com animação
    
    Args:
        message: Mensagem de erro
    """
    return st.markdown(f"""
    <div class="error-state">
        {message}
    </div>
    """, unsafe_allow_html=True)


def elegant_progress_bar(progress: float, text: str = ""):
    """
    Progress bar elegante personalizada
    
    Args:
        progress: Valor de 0 a 1
        text: Texto a ser exibido junto ao progress bar
    """
    percentage = int(progress * 100)
    
    return st.markdown(f"""
    <div style="margin: 10px 0;">
        {f'<div style="margin-bottom: 5px; font-weight: bold;">{text}</div>' if text else ''}
        <div class="elegant-progress" style="--progress-width: {percentage}%;"></div>
        <div style="text-align: center; font-size: 12px; color: #666; margin-top: 5px;">
            {percentage}%
        </div>
    </div>
    """, unsafe_allow_html=True)


def status_badge(status: str, text: str):
    """
    Badge de status elegante
    
    Args:
        status: 'processing', 'completed', 'error', 'waiting'
        text: Texto do badge
    """
    return st.markdown(f"""
    <span class="status-badge {status}">{text}</span>
    """, unsafe_allow_html=True)


def tooltip(text: str, tooltip_text: str):
    """
    Texto com tooltip elegante
    
    Args:
        text: Texto a ser exibido
        tooltip_text: Conteúdo do tooltip
    """
    return st.markdown(f"""
    <span class="custom-tooltip" data-tooltip="{tooltip_text}">{text}</span>
    """, unsafe_allow_html=True)


def enhanced_file_uploader(
    label: str,
    type: Optional[list] = None,
    accept_multiple_files: bool = False,
    key: Optional[str] = None,
    help_text: str = "",
    tooltip_text: str = ""
):
    """
    File uploader melhorado com tooltip e feedback visual
    
    Args:
        label: Label do uploader
        type: Tipos de arquivo aceitos
        accept_multiple_files: Se aceita múltiplos arquivos
        key: Chave única
        help_text: Texto de ajuda
        tooltip_text: Texto do tooltip
    """
    if tooltip_text:
        st.markdown(f"""
        <div class="custom-tooltip" data-tooltip="{tooltip_text}">
            <strong>{label}</strong>
        </div>
        """, unsafe_allow_html=True)
    else:
        st.markdown(f"**{label}**")
    
    if help_text:
        st.markdown(f"<small style='color: #666;'>{help_text}</small>", unsafe_allow_html=True)
    
    return st.file_uploader(
        label="",
        type=type,
        accept_multiple_files=accept_multiple_files,
        key=key,
        label_visibility="collapsed"
    )


def enhanced_button(
    label: str,
    key: Optional[str] = None,
    tooltip_text: str = "",
    disabled: bool = False,
    use_container_width: bool = False
):
    """
    Botão melhorado com tooltip
    
    Args:
        label: Texto do botão
        key: Chave única
        tooltip_text: Texto do tooltip
        disabled: Se o botão está desabilitado
        use_container_width: Se deve usar toda a largura
    """
    if tooltip_text:
        col1, col2 = st.columns([0.01, 0.99])
        with col1:
            st.markdown(f"""
            <div class="custom-tooltip" data-tooltip="{tooltip_text}" style="margin-top: 8px;">
                ℹ️
            </div>
            """, unsafe_allow_html=True)
        with col2:
            return st.button(
                label,
                key=key,
                disabled=disabled,
                use_container_width=use_container_width
            )
    else:
        return st.button(
            label,
            key=key,
            disabled=disabled,
            use_container_width=use_container_width
        )


def processing_context(message: str = "Processando..."):
    """
    Context manager para exibir estado de processamento
    
    Usage:
        with processing_context("Extraindo dados..."):
            # código que demora
            time.sleep(2)
    """
    class ProcessingContext:
        def __init__(self, message):
            self.message = message
            self.placeholder = None
        
        def __enter__(self):
            self.placeholder = st.empty()
            with self.placeholder:
                show_processing_state(self.message)
            return self
        
        def __exit__(self, exc_type, exc_val, exc_tb):
            if self.placeholder:
                self.placeholder.empty()
            
            if exc_type is None:
                show_success_state("✅ Processamento concluído!")
                time.sleep(1)
            else:
                show_error_state(f"❌ Erro: {str(exc_val)}")
                time.sleep(2)
    
    return ProcessingContext(message)


def step_indicator(current_step: int, total_steps: int, step_names: list):
    """
    Indicador de passos elegante
    
    Args:
        current_step: Passo atual (1-indexed)
        total_steps: Total de passos
        step_names: Lista com nomes dos passos
    """
    st.markdown("### 📋 Progresso")
    
    for i, step_name in enumerate(step_names[:total_steps], 1):
        if i < current_step:
            # Passo concluído
            st.markdown(f"""
            <div style="display: flex; align-items: center; margin: 5px 0;">
                <div style="width: 24px; height: 24px; border-radius: 50%; background: linear-gradient(135deg, #27ae60 0%, #2ecc71 100%); 
                           color: white; display: flex; align-items: center; justify-content: center; font-weight: bold; margin-right: 10px;">
                    ✓
                </div>
                <span style="color: #27ae60; font-weight: bold;">{step_name}</span>
            </div>
            """, unsafe_allow_html=True)
        elif i == current_step:
            # Passo atual
            st.markdown(f"""
            <div style="display: flex; align-items: center; margin: 5px 0;">
                <div class="pulse" style="width: 24px; height: 24px; border-radius: 50%; background: linear-gradient(135deg, #2C3E50 0%, #4CA1AF 100%); 
                           color: white; display: flex; align-items: center; justify-content: center; font-weight: bold; margin-right: 10px;">
                    {i}
                </div>
                <span style="color: #2C3E50; font-weight: bold;">{step_name}</span>
            </div>
            """, unsafe_allow_html=True)
        else:
            # Passo pendente
            st.markdown(f"""
            <div style="display: flex; align-items: center; margin: 5px 0;">
                <div style="width: 24px; height: 24px; border-radius: 50%; background: #e0e0e0; 
                           color: #999; display: flex; align-items: center; justify-content: center; font-weight: bold; margin-right: 10px;">
                    {i}
                </div>
                <span style="color: #999;">{step_name}</span>
            </div>
            """, unsafe_allow_html=True)


def enhanced_metric(label: str, value: str, delta: Optional[str] = None, tooltip_text: str = ""):
    """
    Métrica melhorada com tooltip
    
    Args:
        label: Label da métrica
        value: Valor da métrica
        delta: Variação (opcional)
        tooltip_text: Texto do tooltip
    """
    if tooltip_text:
        col1, col2 = st.columns([0.05, 0.95])
        with col1:
            st.markdown(f"""
            <div class="custom-tooltip" data-tooltip="{tooltip_text}" style="margin-top: 15px;">
                ℹ️
            </div>
            """, unsafe_allow_html=True)
        with col2:
            st.metric(label, value, delta)
    else:
        st.metric(label, value, delta)


def notification_toast(message: str, type: str = "info", duration: int = 3):
    """
    Notificação toast elegante
    
    Args:
        message: Mensagem da notificação
        type: 'info', 'success', 'error', 'warning'
        duration: Duração em segundos
    """
    colors = {
        "info": "linear-gradient(135deg, #2C3E50 0%, #4CA1AF 100%)",
        "success": "linear-gradient(135deg, #27ae60 0%, #2ecc71 100%)",
        "error": "linear-gradient(135deg, #e74c3c 0%, #c0392b 100%)",
        "warning": "linear-gradient(135deg, #f39c12 0%, #e67e22 100%)"
    }
    
    placeholder = st.empty()
    
    with placeholder:
        st.markdown(f"""
        <div style="position: fixed; top: 20px; right: 20px; z-index: 9999; 
                    background: {colors.get(type, colors['info'])}; color: white; 
                    padding: 15px 20px; border-radius: 10px; box-shadow: 0 4px 12px rgba(0,0,0,0.3);
                    animation: slideInFromTop 0.5s ease-out;">
            {message}
        </div>
        """, unsafe_allow_html=True)
    
    time.sleep(duration)
    placeholder.empty()


def advanced_file_uploader(
    label: str = "📁 Arraste seu PDF aqui ou clique para selecionar",
    help_text: str = "Formatos aceitos: PDF (máx. 100MB)",
    key: Optional[str] = None
):
    """
    Upload avançado com drag & drop e preview
    
    Args:
        label: Label do uploader
        help_text: Texto de ajuda
        key: Chave única
    """
    
    # CSS para estilizar o uploader
    st.markdown("""
    <style>
    .advanced-uploader {
        border: 2px dashed #4CA1AF;
        border-radius: 15px;
        padding: 40px 20px;
        text-align: center;
        background: linear-gradient(135deg, rgba(44, 62, 80, 0.02) 0%, rgba(76, 161, 175, 0.02) 100%);
        transition: all 0.3s ease;
        cursor: pointer;
        position: relative;
        overflow: hidden;
        margin: 20px 0;
    }
    
    .advanced-uploader:hover {
        border-color: #2C3E50;
        background: linear-gradient(135deg, rgba(44, 62, 80, 0.05) 0%, rgba(76, 161, 175, 0.05) 100%);
        transform: translateY(-2px);
        box-shadow: 0 8px 25px rgba(76, 161, 175, 0.15);
    }
    
    .upload-icon {
        font-size: 48px;
        color: #4CA1AF;
        margin-bottom: 15px;
        display: block;
    }
    
    .upload-text {
        font-size: 18px;
        font-weight: bold;
        color: #2C3E50;
        margin-bottom: 10px;
    }
    
    .upload-help {
        font-size: 14px;
        color: #666;
        margin-bottom: 20px;
    }
    
    .upload-features {
        display: flex;
        justify-content: center;
        gap: 20px;
        flex-wrap: wrap;
        margin-top: 20px;
    }
    
    .upload-feature {
        display: flex;
        align-items: center;
        gap: 5px;
        font-size: 12px;
        color: #4CA1AF;
        background: rgba(76, 161, 175, 0.1);
        padding: 5px 10px;
        border-radius: 15px;
    }
    </style>
    """, unsafe_allow_html=True)
    
    # Container do uploader visual
    st.markdown(f"""
    <div class="advanced-uploader">
        <div class="upload-icon">📁</div>
        <div class="upload-text">{label}</div>
        <div class="upload-help">{help_text}</div>
        <div class="upload-features">
            <div class="upload-feature">
                <span>📊</span> Preview automático
            </div>
            <div class="upload-feature">
                <span>🔍</span> Validação de sumário
            </div>
            <div class="upload-feature">
                <span>⚡</span> Funcional
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    # File uploader real do Streamlit
    uploaded_file = st.file_uploader(
        "Selecione um arquivo PDF",
        type=['pdf'],
        key=key,
        help=help_text
    )
    
    return uploaded_file


def pdf_preview(file_data: bytes, filename: str):
    """
    Preview do PDF com informações básicas
    
    Args:
        file_data: Dados do arquivo PDF
        filename: Nome do arquivo
    """
    try:
        import PyPDF2
        from io import BytesIO
        
        # Criar leitor PDF
        pdf_reader = PyPDF2.PdfReader(BytesIO(file_data))
        num_pages = len(pdf_reader.pages)
        
        # Extrair primeira página para preview
        first_page = pdf_reader.pages[0]
        full_text = first_page.extract_text()
        text_preview = full_text[:800] + "..." if len(full_text) > 800 else full_text
        
        # Container do preview mais bonito
        st.markdown("### 📄 Informações do Arquivo")
        
        # Métricas em linha
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.metric(
                "📄 Páginas", 
                num_pages,
                help="Número total de páginas do documento"
            )
        
        with col2:
            file_size_mb = len(file_data) / (1024*1024)
            st.metric(
                "📊 Tamanho", 
                f"{file_size_mb:.1f} MB",
                help="Tamanho do arquivo em megabytes"
            )
        
        with col3:
            st.metric(
                "📝 Texto", 
                "Sim" if text_preview.strip() else "Não",
                help="Indica se foi possível extrair texto da primeira página"
            )
        
        # Preview removido conforme solicitado
        
        return {
            "num_pages": num_pages,
            "has_text": bool(text_preview.strip()),
            "file_size": len(file_data)
        }
        
    except Exception as e:
        st.error(f"❌ Erro ao analisar PDF: {str(e)}")
        return {
            "num_pages": 0,
            "has_text": False,
            "file_size": len(file_data)
        }


def validate_pdf_structure(file_data: bytes):
    """
    Valida a estrutura do PDF e verifica se tem sumário
    
    Args:
        file_data: Dados do arquivo PDF
    """
    try:
        import PyPDF2
        import pdfplumber
        from io import BytesIO
        
        # Análise com PyPDF2
        pdf_reader = PyPDF2.PdfReader(BytesIO(file_data))
        
        # Verificar bookmarks/outline
        has_bookmarks = pdf_reader.outline is not None and len(pdf_reader.outline) > 0
        
        # Análise com pdfplumber para detectar sumário
        has_summary_text = False
        summary_keywords = ['sumário', 'índice', 'contents', 'index', 'conteúdo']
        
        with pdfplumber.open(BytesIO(file_data)) as pdf:
            # Verificar primeiras 5 páginas
            for i, page in enumerate(pdf.pages[:5]):
                text = page.extract_text()
                if text:
                    text_lower = text.lower()
                    if any(keyword in text_lower for keyword in summary_keywords):
                        has_summary_text = True
                        break
        
        # Container de validação
        st.markdown("### 🔍 Validação da Estrutura")
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            if has_bookmarks:
                st.success("📑 PDF possui bookmarks/outline")
            else:
                st.warning("⚠️ PDF não possui bookmarks")
        
        with col2:
            if has_summary_text:
                st.success("📋 Sumário detectado no texto")
            else:
                st.warning("⚠️ Sumário não detectado")
        
        with col3:
            compatibility_score = 0
            if has_bookmarks:
                compatibility_score += 50
            if has_summary_text:
                compatibility_score += 50
            
            if compatibility_score >= 75:
                st.success(f"🎯 Compatibilidade: {compatibility_score}%")
            elif compatibility_score >= 50:
                st.info(f"⚡ Compatibilidade: {compatibility_score}%")
            else:
                st.error(f"⚠️ Compatibilidade: {compatibility_score}%")
        
        # Recomendações
        if compatibility_score < 75:
            st.markdown("### 💡 Recomendações")
            
            if not has_bookmarks and not has_summary_text:
                st.warning("""
                **⚠️ PDF com baixa compatibilidade**
                - Este PDF não possui bookmarks nem sumário detectável
                - O processamento pode não encontrar seções
                - Recomenda-se usar um PDF com estrutura de índice
                """)
            elif not has_bookmarks:
                st.info("""
                **ℹ️ PDF sem bookmarks**
                - O PDF possui sumário textual mas sem bookmarks
                - O processamento tentará extrair do texto
                - Resultados podem variar dependendo do formato
                """)
            elif not has_summary_text:
                st.info("""
                **ℹ️ PDF com bookmarks mas sem sumário textual**
                - O PDF possui estrutura mas sumário não detectado
                - O processamento usará os bookmarks disponíveis
                """)
        else:
            st.success("""
            **✅ PDF com excelente compatibilidade!**
            - Estrutura adequada para processamento
            - Alta probabilidade de sucesso na extração
            """)
        
        return {
            "has_bookmarks": has_bookmarks,
            "has_summary_text": has_summary_text,
            "compatibility_score": compatibility_score,
            "is_compatible": compatibility_score >= 50
        }
        
    except Exception as e:
        st.error(f"❌ Erro na validação: {str(e)}")
        return None