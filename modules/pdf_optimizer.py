import streamlit as st
import os
import tempfile
import subprocess

def pdf_optimizer_page():
    st.title("⚡ Otimizar PDF")
    st.markdown("---")
    
    # Upload do arquivo
    uploaded_file = st.file_uploader(
        "📄 Selecione um arquivo PDF",
        type=['pdf'],
        help="Faça upload de um PDF que deseja comprimir e otimizar"
    )
    
    if uploaded_file is not None:
        # Mostrar informações do arquivo
        original_size = len(uploaded_file.getvalue())
        st.success(f"📄 Arquivo carregado: {uploaded_file.name}")
        st.info(f"📊 Tamanho original: {original_size / (1024*1024):.2f} MB")
        
        # Opções de compressão
        st.markdown("### 🛠️ Opções de Compressão")
        
        col1, col2 = st.columns(2)
        with col1:
            compression_mode = st.radio(
                "Escolha o modo de compressão:",
                ["🔰 Leve (Ebook)", "🚀 Turbo (Screen)"],
                help="Leve: melhor qualidade, menor compressão | Turbo: maior compressão, qualidade reduzida"
            )
        
        with col2:
            st.markdown("**Configurações do modo selecionado:**")
            if "Leve" in compression_mode:
                st.info("""
                📚 **Modo Leve (Ebook):**
                - Mantém boa qualidade de texto
                - Compressão moderada
                - Ideal para documentos com texto
                """)
            else:
                st.info("""
                🚀 **Modo Turbo (Screen):**
                - Máxima compressão
                - Qualidade reduzida
                - Ideal para visualização digital
                """)
        
        # Botão para otimizar
        if st.button("⚡ Otimizar PDF", type="primary"):
            optimize_pdf(uploaded_file, compression_mode)
    else:
        pass
        
        # Informações sobre o Ghostscript
        with st.expander("ℹ️ Informações sobre Otimização"):
            st.markdown("""
            **Como funciona a otimização:**
            
            Esta ferramenta utiliza o Ghostscript para comprimir PDFs através de:
            - Recompressão de imagens
            - Otimização de fontes
            - Remoção de metadados desnecessários
            - Simplificação de elementos gráficos
            
            **Requisitos:**
            - Ghostscript deve estar instalado no sistema
            - Windows: `gswin64c.exe` deve estar no PATH
            - Linux: `gs` deve estar disponível
            
            **Modos de compressão:**
            - **Leve (/ebook)**: Mantém qualidade de texto e imagens
            - **Turbo (/screen)**: Máxima compressão para visualização
            """)

def optimize_pdf(uploaded_file, compression_mode):
    """Otimiza o PDF usando Ghostscript"""
    
    # Salvar arquivo temporário
    with tempfile.NamedTemporaryFile(delete=False, suffix='.pdf') as tmp_input:
        tmp_input.write(uploaded_file.getvalue())
        input_path = tmp_input.name
    
    # Arquivo de saída temporário
    with tempfile.NamedTemporaryFile(delete=False, suffix='_otimizado.pdf') as tmp_output:
        output_path = tmp_output.name
    
    try:
        # Container para feedback
        status_container = st.container()
        
        with status_container:
            st.markdown("### 🔄 Otimizando PDF...")
            
            # Determinar configuração
            setting = "/ebook" if "Leve" in compression_mode else "/screen"
            
            # Mostrar configuração
            st.info(f"🛠️ Usando configuração: {setting}")
            
            with st.spinner("⚡ Processando arquivo..."):
                # Comando Ghostscript
                gs_command = "gswin64c" if os.name == 'nt' else "gs"
                
                command = [
                    gs_command,
                    "-sDEVICE=pdfwrite",
                    "-dCompatibilityLevel=1.4",
                    f"-dPDFSETTINGS={setting}",
                    "-dNOPAUSE",
                    "-dQUIET",
                    "-dBATCH",
                    "-dPreserveEPSInfo=true",
                    "-dAutoRotatePages=/None",
                    f"-sOutputFile={output_path}",
                    input_path
                ]
                
                # Executar comando
                try:
                    if os.name == 'nt':
                        # Windows
                        si = subprocess.STARTUPINFO()
                        si.dwFlags |= subprocess.STARTF_USESHOWWINDOW
                        result = subprocess.run(command, check=True, startupinfo=si, 
                                              capture_output=True, text=True)
                    else:
                        # Linux/Mac
                        result = subprocess.run(command, check=True, capture_output=True, text=True)
                    
                    # Verificar se arquivo foi criado
                    if not os.path.exists(output_path):
                        st.error("❌ Arquivo otimizado não foi criado")
                        return
                    
                    # Comparar tamanhos
                    original_size = len(uploaded_file.getvalue())
                    optimized_size = os.path.getsize(output_path)
                    
                    compression_ratio = ((original_size - optimized_size) / original_size) * 100
                    
                    # Mostrar resultados
                    st.success("✅ PDF otimizado com sucesso!")
                    
                    col1, col2, col3 = st.columns(3)
                    with col1:
                        st.metric("📊 Tamanho Original", f"{original_size / (1024*1024):.2f} MB")
                    with col2:
                        st.metric("📉 Tamanho Otimizado", f"{optimized_size / (1024*1024):.2f} MB")
                    with col3:
                        st.metric("💾 Compressão", f"{compression_ratio:.1f}%")
                    
                    # Ler arquivo otimizado
                    with open(output_path, 'rb') as f:
                        optimized_data = f.read()
                    
                    # Nome do arquivo otimizado
                    original_name = uploaded_file.name
                    optimized_name = original_name.replace('.pdf', '_otimizado.pdf')
                    
                    # Botão de download
                    st.download_button(
                        label="📥 Baixar PDF Otimizado",
                        data=optimized_data,
                        file_name=optimized_name,
                        mime="application/pdf",
                        type="primary"
                    )
                    
                
                except subprocess.CalledProcessError as e:
                    st.error(f"❌ Erro ao executar Ghostscript: {e}")
                    st.error("Verifique se o Ghostscript está instalado e disponível no PATH")
                    
                    # Mostrar detalhes do erro
                    if e.stderr:
                        with st.expander("🔍 Detalhes do Erro"):
                            st.code(e.stderr)
                
                except FileNotFoundError:
                    st.error("❌ Ghostscript não encontrado")
                    st.error("Instale o Ghostscript para usar esta funcionalidade")
                    
                    with st.expander("📥 Como instalar o Ghostscript"):
                        st.markdown("""
                        **Windows:**
                        1. Baixe o Ghostscript em: https://www.ghostscript.com/download/gsdnld.html
                        2. Execute o instalador
                        3. Adicione o diretório bin ao PATH do sistema
                        
                        **Linux (Ubuntu/Debian):**
                        ```bash
                        sudo apt-get install ghostscript
                        ```
                        
                        **Linux (CentOS/RHEL):**
                        ```bash
                        sudo yum install ghostscript
                        ```
                        
                        **macOS:**
                        ```bash
                        brew install ghostscript
                        ```
                        """)
                
    finally:
        # Limpar arquivos temporários
        try:
            os.unlink(input_path)
            os.unlink(output_path)
        except:
            pass

def check_ghostscript_available():
    """Verifica se o Ghostscript está disponível"""
    try:
        gs_command = "gswin64c" if os.name == 'nt' else "gs"
        result = subprocess.run([gs_command, "--version"], 
                              capture_output=True, text=True)
        return True
    except (subprocess.CalledProcessError, FileNotFoundError):
        return False