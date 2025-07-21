import streamlit as st
import sys
import os

# Garante que o Python enxergue as pastas core/ e modules/
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Configuração da página
st.set_page_config(
    page_title="Jack PDF Slicer",
    page_icon="🔪",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Inicializar diretórios necessários apenas para logs
os.makedirs("logs", exist_ok=True)

# CSS customizado
try:
    with open("static/styles.css", "r") as f:
        st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)
except FileNotFoundError:
    # Fallback CSS mínimo se arquivo não for encontrado
    st.markdown("""
    <style>
        .main-header {
            text-align: center;
            color: #FF6B6B;
            font-size: 2.5rem;
            margin-bottom: 2rem;
            font-weight: bold;
        }
    </style>
    """, unsafe_allow_html=True)

def main():
    # Sidebar para navegação
    with st.sidebar:
        # Logo e título responsivos ao tema
        try:
            import base64
            
            with open("graphics/Logo-branco.png", "rb") as img_file:
                logo_base64 = base64.b64encode(img_file.read()).decode()
            
            st.markdown(f"""
            <style>
            /* Forçar cor fixa da sidebar com largura 300px */
            .css-1d391kg,
            [data-testid="stSidebar"],
            .stSidebar > div {{
                background-color: #1c1c34 !important;
                width: 300px !important;
                min-width: 300px !important;
                max-width: 300px !important;
            }}
            
            /* Forçar fonte branca em toda a sidebar */
            .css-1d391kg,
            .css-1d391kg *,
            [data-testid="stSidebar"],
            [data-testid="stSidebar"] *,
            .stSidebar,
            .stSidebar * {{
                color: #FFFFFF !important;
            }}
            
            /* Garantir que selectbox, botões e outros elementos sejam brancos */
            .css-1d391kg .stSelectbox label,
            .css-1d391kg .stSelectbox div,
            .css-1d391kg .stSelectbox option,
            [data-testid="stSidebar"] .stSelectbox label,
            [data-testid="stSidebar"] .stSelectbox div,
            [data-testid="stSidebar"] .stSelectbox option {{
                color: #FFFFFF !important;
            }}
            
            .logo-title-container {{
                display: flex;
                flex-direction: column;
                align-items: center;
                margin-bottom: 10px;
                padding: 0;
                margin-top: -10px;
            }}
            
            .logo {{
                width: 180px;
                height: auto;
                margin-bottom: 5px;
                /* Logo branco fixo */
                filter: brightness(0) invert(1);
            }}
            
            .title {{
                font-size: 1.4rem;
                font-weight: bold;
                text-align: center;
                margin: 0;
                /* Título branco fixo */
                color: #FFFFFF;
            }}
            </style>
            
            <div class="logo-title-container">
                <img src="data:image/png;base64,{logo_base64}" 
                     class="logo" 
                     alt="Jack PDF Slicer Logo">
                <h2 class="title">Jack PDF Slicer</h2>
            </div>
            """, unsafe_allow_html=True)
            
        except FileNotFoundError:
            # Fallback final se logo não for encontrado
            st.markdown("# 🔪 Jack PDF Slicer")
        
        st.markdown("---")
        
        # Menu de navegação com botões fixos
        #st.markdown("### 🗂️ Menu")
        
        if st.button("🏠 Home", use_container_width=True):
            st.session_state.current_page = "🏠 Home"
        
        if st.button("🔪 Fatiar PDF", use_container_width=True):
            st.session_state.current_page = "🔪 Fatiar PDF"
        
        if st.button("⚡ Otimizar PDF", use_container_width=True):
            st.session_state.current_page = "⚡ Otimizar PDF"
        
        if st.button("🧠 Aplicar OCR", use_container_width=True):
            st.session_state.current_page = "🧠 Aplicar OCR"
        
        if st.button("🔗 Unir PDFs", use_container_width=True):
            st.session_state.current_page = "🔗 Unir PDFs"
        
        if st.button("✂️ Dividir PDF", use_container_width=True):
            st.session_state.current_page = "✂️ Dividir PDF"
        
        if st.button("🪄 Converter PDF", use_container_width=True):
            st.session_state.current_page = "🪄 Converter PDF"
        
        if st.button("⚙️ Configurações", use_container_width=True):
            st.session_state.current_page = "⚙️ Configurações"
        
        # Definir página padrão se não existir
        if "current_page" not in st.session_state:
            st.session_state.current_page = "🏠 Home"
        
        page = st.session_state.current_page
        
        st.markdown("---")
        #st.markdown("### ℹ️ Sistema:")
        
        # Informações do sistema compactadas
        import platform
        import subprocess
        
        # Dependências e Tools em 2 colunas
        col1, col2 = st.columns(2)
        
        with col1:
            # Dependências principais
            st.markdown("**Dependências**")
            dependencies = [
                "PyPDF2", "pdfplumber", "fitz", "pikepdf",
                "pdf2docx", "openpyxl", "python-docx", "Pillow"
            ]
            for dep in dependencies:
                try:
                    # Mapear nomes de import diferentes
                    import_name = dep
                    if dep == "python-docx":
                        import_name = "docx"
                    elif dep == "Pillow":
                        import_name = "PIL"
                    elif dep == "fitz":
                        import_name = "fitz"
                    
                    __import__(import_name)
                    st.markdown(f"✅ {dep}")
                except ImportError:
                    st.markdown(f"❌ {dep}")
        
        with col2:
            # Ferramentas externas
            st.markdown("**Tools**")
            external_tools = {
                "Ghostscript": "gswin64c" if os.name == 'nt' else "gs",
                "OCRmyPDF": "ocrmypdf", 
                "Tesseract": "tesseract",
                "LibreOffice": "libreoffice" if os.name != 'nt' else "soffice",
                "Pandoc": "pandoc"
            }
            
            for name, command in external_tools.items():
                try:
                    subprocess.run([command, "--version"], 
                                  capture_output=True, text=True, timeout=2)
                    st.markdown(f"✅ {name}")
                except:
                    st.markdown(f"❌ {name}")
        
        

    # Conteúdo principal baseado na seleção
    if page == "🏠 Home":
        show_home()
    elif page == "🔪 Fatiar PDF":
        show_pdf_slicer_new()
    elif page == "⚡ Otimizar PDF":
        show_pdf_optimizer()
    elif page == "🧠 Aplicar OCR":
        show_ocr()
    elif page == "🔗 Unir PDFs":
        show_pdf_merger_clean()
    elif page == "✂️ Dividir PDF":
        show_pdf_splitter()
    elif page == "🪄 Converter PDF":
        show_pdf_converter()
    elif page == "⚙️ Configurações":
        show_settings()

def show_home():
    st.markdown('<h1 class="main-header">🔪 Jack PDF Slicer</h1>', unsafe_allow_html=True)
    st.markdown('<p style="text-align: center; font-size: 1.2rem; color: #666;">Ferramenta profissional para processamento de PDFs legais</p>', unsafe_allow_html=True)
    
    # Importar componentes de UI
    from core.ui_components import enhanced_metric, tooltip, status_badge
    
    # Estatísticas da sessão com tooltips
    if st.session_state.get('numero_processo') or st.session_state.get('pdf_sections'):
        st.markdown("### 📊 Status da Sessão")
        col1, col2, col3 = st.columns(3)
        
        with col1:
            if st.session_state.get('numero_processo'):
                enhanced_metric(
                    "Processo Ativo",
                    st.session_state.numero_processo[:12] + "...",
                    tooltip_text="Número do processo extraído automaticamente do PDF carregado"
                )
        
        with col2:
            if st.session_state.get('pdf_sections'):
                enhanced_metric(
                    "Seções Encontradas",
                    str(len(st.session_state.pdf_sections)),
                    tooltip_text="Número de documentos individuais identificados no PDF"
                )
        
        with col3:
            if st.session_state.get('current_filename'):
                enhanced_metric(
                    "Arquivo Atual",
                    st.session_state.current_filename[:15] + "...",
                    tooltip_text="Nome do arquivo PDF atualmente carregado"
                )
        
        st.markdown("---")
    
    # Grid de funcionalidades
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown("""
        <div class="feature-card">
            <h3>🔪 Fatiamento de PDF</h3>
            <p>Extrai automaticamente documentos individuais de PDFs grandes baseado em índices/sumários.</p>
        </div>
        """, unsafe_allow_html=True)
        
        st.markdown("""
        <div class="feature-card">
            <h3>🔗 Unir PDFs</h3>
            <p>Combine múltiplos PDFs em um único arquivo na ordem desejada.</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown("""
        <div class="feature-card">
            <h3>⚡ Otimização de PDF</h3>
            <p>Reduz o tamanho de arquivos PDF mantendo a qualidade, com opções de compressão leve e turbo.</p>
        </div>
        """, unsafe_allow_html=True)
        
        st.markdown("""
        <div class="feature-card">
            <h3>✂️ Dividir PDF</h3>
            <p>Divida PDFs por páginas, tamanho ou extraia páginas específicas.</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col3:
        st.markdown("""
        <div class="feature-card">
            <h3>🧠 OCR Inteligente</h3>
            <p>Aplica reconhecimento óptico de caracteres em PDFs digitalizados para torná-los pesquisáveis.</p>
        </div>
        """, unsafe_allow_html=True)
        
        st.markdown("""
        <div class="feature-card">
            <h3>🪄 Converter PDF</h3>
            <p>Converta PDFs para Word, Excel, imagens, texto e outros formatos.</p>
        </div>
        """, unsafe_allow_html=True)
    
    st.markdown("---")
    
    # Instruções de uso
    col1, col2 = st.columns([3, 1])
    
    with col1:
        st.markdown("## 🚀 Como usar:")
        st.markdown("""
        1. **Selecione uma funcionalidade** no menu lateral
        2. **Faça upload** do seu arquivo PDF
        3. **Configure** as opções desejadas
        4. **Execute** o processamento
        5. **Baixe** os resultados
        """)
    
    with col2:
        st.markdown("### 📚 Documentação")
        if st.button("📖 Ver Documentação Completa", type="secondary", use_container_width=True):
            st.session_state.show_documentation = True
            st.rerun()
    
    # Mostrar documentação se solicitado
    if st.session_state.get('show_documentation', False):
        show_documentation()
        if st.button("❌ Fechar Documentação", type="secondary"):
            st.session_state.show_documentation = False
            st.rerun()
    
    # Informações adicionais
    with st.expander("ℹ️ Informações do Sistema"):
        st.markdown("""
        **Formatos suportados:** PDF
        
        **Funcionalidades principais:**
        - Extração automática de sumários
        - Validação de datas (dd/mm/yyyy, yyyy-mm-dd)
        - Sanitização de nomes de arquivo
        - Processamento 100% em memória
        - OCR com múltiplos idiomas
        
        **Arquitetura:**
        - Processamento stateless (sem arquivos temporários)
        - Download direto pelo navegador
        - Otimizado para servidor
        - `logs/`: Logs do sistema
        """)

def show_pdf_slicer_new():
    from modules.pdf_slicer_new import pdf_slicer_new_page
    pdf_slicer_new_page()

def show_pdf_optimizer():
    from modules.pdf_optimizer import pdf_optimizer_page
    pdf_optimizer_page()

def show_ocr():
    from modules.ocr import ocr_page
    ocr_page()

def show_cards_clean():
    from test_cards_clean import test_cards_clean_page
    test_cards_clean_page()

def show_pdf_merger_clean():
    from modules.pdf_merger_final import pdf_merger_page
    pdf_merger_page()

def show_pdf_splitter():
    from modules.pdf_splitter import pdf_splitter_page
    pdf_splitter_page()

def show_pdf_converter():
    from modules.pdf_converter import pdf_converter_page
    pdf_converter_page()

def show_settings():
    from modules.settings import settings_page
    settings_page()

def show_documentation():
    """Mostra a documentação completa do sistema"""
    st.markdown("---")
    st.markdown("# 📚 Documentação Completa - Jack PDF Slicer")
    
    # Ler e exibir a documentação
    try:
        with open("DOCUMENTACAO.md", "r", encoding="utf-8") as f:
            documentation = f.read()
        
        # Remover o título duplicado
        documentation = documentation.replace("# 📚 Documentação Completa - Jack PDF Slicer\n\n", "")
        
        st.markdown(documentation)
        
    except FileNotFoundError:
        st.error("❌ Arquivo de documentação não encontrado!")
        st.info("📝 A documentação deveria estar no arquivo `DOCUMENTACAO.md`")
    
    st.markdown("---")

if __name__ == "__main__":
    main()