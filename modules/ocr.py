import streamlit as st
import os
import tempfile
import subprocess

def ocr_page():
    st.title("🧠 Aplicar OCR")
    st.markdown("---")
    
    # Upload do arquivo
    uploaded_file = st.file_uploader(
        "📄 Selecione um arquivo PDF",
        type=['pdf'],
        help="Faça upload de um PDF digitalizado que precisa de reconhecimento de texto"
    )
    
    if uploaded_file is not None:
        # Mostrar informações do arquivo
        file_size = len(uploaded_file.getvalue())
        st.success(f"📄 Arquivo carregado: {uploaded_file.name}")
        st.info(f"📊 Tamanho: {file_size / (1024*1024):.2f} MB")
        
        # Opções de OCR
        st.markdown("### 🛠️ Configurações de OCR")
        
        col1, col2 = st.columns(2)
        
        with col1:
            ocr_language = st.selectbox(
                "🌐 Idioma do documento:",
                ["por", "eng", "spa", "fra", "deu", "ita"],
                format_func=lambda x: {
                    "por": "🇧🇷 Português",
                    "eng": "🇺🇸 Inglês", 
                    "spa": "🇪🇸 Espanhol",
                    "fra": "🇫🇷 Francês",
                    "deu": "🇩🇪 Alemão",
                    "ita": "🇮🇹 Italiano"
                }[x],
                help="Selecione o idioma principal do documento"
            )
            
            force_ocr = st.checkbox(
                "🔄 Forçar OCR completo",
                value=True,
                help="Aplica OCR mesmo em páginas que já têm texto"
            )
        
        with col2:
            optimize_output = st.checkbox(
                "⚡ Otimizar saída",
                value=True,
                help="Otimiza o PDF resultante para reduzir tamanho"
            )
            
            deskew = st.checkbox(
                "📐 Corrigir inclinação",
                value=True,
                help="Corrige automaticamente páginas inclinadas"
            )
        
        # Informações sobre qualidade
        st.markdown("### 📊 Configurações de Qualidade")
        
        col1, col2 = st.columns(2)
        with col1:
            jobs = st.slider(
                "🔧 Threads de processamento:",
                min_value=1,
                max_value=8,
                value=4,
                help="Número de threads para processamento paralelo"
            )
        
        with col2:
            jpeg_quality = st.slider(
                "🖼️ Qualidade JPEG:",
                min_value=50,
                max_value=100,
                value=85,
                help="Qualidade das imagens no PDF resultante"
            )
        
        # Botão para aplicar OCR
        if st.button("🧠 Aplicar OCR", type="primary"):
            apply_ocr(uploaded_file, ocr_language, force_ocr, optimize_output, deskew, jobs, jpeg_quality)
    
    else:
        pass
        
        # Informações sobre OCR
        with st.expander("ℹ️ Informações sobre OCR (Reconhecimento Ótico de Caracteres)"):
            st.markdown("""
            **Como funciona o OCR:**
            
            Esta ferramenta utiliza **OCRmyPDF** + **Tesseract** para:
            - Converter imagens de texto em texto editável
            - Tornar PDFs digitalizados pesquisáveis
            - Preservar formatação e layout original
            - Suportar múltiplos idiomas
            
            **O que é OCR?**
            
            OCR (Optical Character Recognition) é uma tecnologia que converte imagens de texto
            em texto editável e pesquisável. É especialmente útil para:
            
            - 📄 Documentos digitalizados (scanner)
            - 📸 Fotografias de documentos
            - 🖼️ PDFs que são apenas imagens
            - 📝 Tornar documentos pesquisáveis
            - 🔍 Permitir seleção e cópia de texto
            
            **Configurações disponíveis:**
            - **Idiomas**: Português, Inglês, Espanhol, Francês, Alemão, Italiano
            - **Forçar OCR**: Aplica OCR mesmo em páginas que já têm texto
            - **Otimizar saída**: Reduz tamanho do arquivo final
            - **Corrigir inclinação**: Corrige automaticamente páginas tortas
            - **Threads**: Processamento paralelo para velocidade
            - **Qualidade JPEG**: Controla qualidade das imagens no PDF final
            
            **Requisitos do sistema:**
            - **OCRmyPDF**: Deve estar instalado no sistema
            - **Tesseract OCR**: Engine de reconhecimento
            - **Suporte a idiomas**: Pacotes de idioma instalados
            
            **Formatos suportados:**
            - **Entrada**: PDF (qualquer tipo)
            - **Saída**: PDF com texto pesquisável
            - **Preservação**: Layout e formatação original
            """)
            
            st.markdown("**💡 Dica:** Use o OCR antes de converter PDFs digitalizados para Word ou Excel!")

def apply_ocr(uploaded_file, language, force_ocr, optimize, deskew, jobs, jpeg_quality):
    """Aplica OCR no PDF usando OCRmyPDF"""
    
    # Salvar arquivo temporário
    with tempfile.NamedTemporaryFile(delete=False, suffix='.pdf') as tmp_input:
        tmp_input.write(uploaded_file.getvalue())
        input_path = tmp_input.name
    
    # Arquivo de saída temporário
    with tempfile.NamedTemporaryFile(delete=False, suffix='_ocr.pdf') as tmp_output:
        output_path = tmp_output.name
    
    try:
        # Container para feedback
        status_container = st.container()
        
        with status_container:
            st.markdown("### 🔄 Aplicando OCR...")
            
            # Mostrar configurações
            st.info(f"""
            🛠️ **Configurações:**
            - Idioma: {language}
            - Forçar OCR: {'Sim' if force_ocr else 'Não'}
            - Otimizar: {'Sim' if optimize else 'Não'}
            - Corrigir inclinação: {'Sim' if deskew else 'Não'}
            - Threads: {jobs}
            - Qualidade JPEG: {jpeg_quality}%
            """)
            
            with st.spinner("🧠 Processando OCR... Isso pode levar alguns minutos..."):
                # Comando OCRmyPDF
                command = [
                    "ocrmypdf",
                    "--language", language,
                    "--jobs", str(jobs),
                    "--jpeg-quality", str(jpeg_quality),
                    "--output-type", "pdf"
                ]
                
                # Adicionar opções condicionais
                if force_ocr:
                    command.append("--force-ocr")
                
                if optimize:
                    command.append("--optimize")
                    command.append("1")
                
                if deskew:
                    command.append("--deskew")
                
                # Adicionar arquivos de entrada e saída
                command.extend([input_path, output_path])
                
                # Executar comando
                try:
                    if os.name == 'nt':
                        # Windows
                        si = subprocess.STARTUPINFO()
                        si.dwFlags |= subprocess.STARTF_USESHOWWINDOW
                        result = subprocess.run(command, check=True, startupinfo=si, 
                                              capture_output=True, text=True, timeout=1800)  # 30 min timeout
                    else:
                        # Linux/Mac
                        result = subprocess.run(command, check=True, capture_output=True, 
                                              text=True, timeout=1800)  # 30 min timeout
                    
                    # Verificar se arquivo foi criado
                    if not os.path.exists(output_path):
                        st.error("❌ Arquivo com OCR não foi criado")
                        return
                    
                    # Comparar tamanhos
                    original_size = len(uploaded_file.getvalue())
                    ocr_size = os.path.getsize(output_path)
                    
                    # Mostrar resultados
                    st.success("✅ OCR aplicado com sucesso!")
                    
                    col1, col2 = st.columns(2)
                    with col1:
                        st.metric("📊 Tamanho Original", f"{original_size / (1024*1024):.2f} MB")
                    with col2:
                        st.metric("📄 Tamanho com OCR", f"{ocr_size / (1024*1024):.2f} MB")
                    
                    # Ler arquivo com OCR
                    with open(output_path, 'rb') as f:
                        ocr_data = f.read()
                    
                    # Nome do arquivo com OCR
                    original_name = uploaded_file.name
                    ocr_name = original_name.replace('.pdf', '_ocr.pdf')
                    
                    # Botão de download
                    st.download_button(
                        label="📥 Baixar PDF com OCR",
                        data=ocr_data,
                        file_name=ocr_name,
                        mime="application/pdf",
                        type="primary"
                    )
                    
                
                except subprocess.TimeoutExpired:
                    st.error("⏱️ Timeout: O processamento OCR demorou muito tempo")
                    st.error("Tente com um arquivo menor ou ajuste as configurações")
                
                except subprocess.CalledProcessError as e:
                    st.error(f"❌ Erro ao executar OCRmyPDF: {e}")
                    st.error("Verifique se o OCRmyPDF está instalado e configurado")
                    
                    # Mostrar detalhes do erro
                    if e.stderr:
                        with st.expander("🔍 Detalhes do Erro"):
                            st.code(e.stderr)
                
                except FileNotFoundError:
                    st.error("❌ OCRmyPDF não encontrado")
                    st.error("Instale o OCRmyPDF para usar esta funcionalidade")
                    
                    with st.expander("📥 Como instalar o OCRmyPDF"):
                        st.markdown("""
                        **Windows:**
                        ```bash
                        pip install ocrmypdf
                        ```
                        
                        Você também precisa instalar o Tesseract:
                        1. Baixe em: https://github.com/UB-Mannheim/tesseract/wiki
                        2. Execute o instalador
                        3. Adicione ao PATH do sistema
                        
                        **Linux (Ubuntu/Debian):**
                        ```bash
                        sudo apt-get install ocrmypdf tesseract-ocr tesseract-ocr-por
                        ```
                        
                        **Linux (CentOS/RHEL):**
                        ```bash
                        sudo yum install ocrmypdf tesseract tesseract-langpack-por
                        ```
                        
                        **macOS:**
                        ```bash
                        brew install ocrmypdf tesseract tesseract-lang
                        ```
                        
                        **Python (via pip):**
                        ```bash
                        pip install ocrmypdf
                        ```
                        """)
                
    finally:
        # Limpar arquivos temporários
        try:
            os.unlink(input_path)
            os.unlink(output_path)
        except:
            pass

def check_ocrmypdf_available():
    """Verifica se o OCRmyPDF está disponível"""
    try:
        result = subprocess.run(["ocrmypdf", "--version"], 
                              capture_output=True, text=True)
        return True
    except (subprocess.CalledProcessError, FileNotFoundError):
        return False

def get_available_languages():
    """Obtém lista de idiomas disponíveis no Tesseract"""
    try:
        result = subprocess.run(["tesseract", "--list-langs"], 
                              capture_output=True, text=True)
        if result.returncode == 0:
            # Pular primeira linha que é "List of available languages"
            langs = result.stdout.strip().split('\n')[1:]
            return [lang.strip() for lang in langs if lang.strip()]
        return []
    except:
        return ["por", "eng"]  # Fallback