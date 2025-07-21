import streamlit as st
import PyPDF2
import fitz  # PyMuPDF
from io import BytesIO
import zipfile
import math
from core.utils import sanitize_filename

def clear_splitter_data():
    """
    Limpa todos os dados do splitter e força reset completo
    """
    # Limpar dados específicos do splitter
    keys_to_clear = [
        'splitter_pdf_data', 'splitter_filename', 'splitter_total_pages',
        'splitter_file_size_mb', 'splitter_results'
    ]
    
    for key in keys_to_clear:
        if key in st.session_state:
            del st.session_state[key]
    
    # Incrementar key do uploader para forçar reset
    st.session_state.splitter_uploader_key += 1

def pdf_splitter_page():
    """
    Página para dividir PDFs de várias formas
    """
    st.title("✂️ Dividir PDF")
    
    # Gerar uma key única para o uploader baseada em um contador
    if 'splitter_uploader_key' not in st.session_state:
        st.session_state.splitter_uploader_key = 0
    
    # Upload do PDF
    uploaded_file = st.file_uploader(
        "📄 Selecione um arquivo PDF",
        type=['pdf'],
        help="Formatos aceitos: PDF",
        key=f"splitter_uploader_{st.session_state.splitter_uploader_key}"
    )
    
    if uploaded_file is not None:
        # Armazenar dados do PDF
        pdf_data = uploaded_file.getvalue()
        
        # Obter informações do PDF
        try:
            pdf_reader = PyPDF2.PdfReader(BytesIO(pdf_data))
            total_pages = len(pdf_reader.pages)
            file_size_mb = len(pdf_data) / (1024 * 1024)
            
            # Exibir informações do arquivo
            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric("📄 Total de Páginas", total_pages)
            with col2:
                st.metric("📦 Tamanho", f"{file_size_mb:.2f} MB")
            with col3:
                st.metric("📊 Média por Página", f"{file_size_mb/total_pages:.2f} MB")
            
            st.markdown("---")
            
            # Tabs para diferentes modos de divisão
            tab1, tab2, tab3 = st.tabs(["📄 Por Páginas", "✂️ Extrair/Remover", "📦 Por Tamanho"])
            
            with tab1:
                split_by_pages(pdf_data, total_pages, uploaded_file.name)
            
            with tab2:
                extract_remove_pages(pdf_data, total_pages, uploaded_file.name)
            
            with tab3:
                split_by_size(pdf_data, total_pages, file_size_mb, uploaded_file.name)
                
        except Exception as e:
            st.error(f"❌ Erro ao processar PDF: {str(e)}")
    
    else:
        # Informações sobre divisão quando não há arquivo carregado
        with st.expander("ℹ️ Informações sobre Divisão de PDF"):
            st.markdown("""
            **Como funciona a divisão:**
            
            Esta ferramenta divide PDFs utilizando **PyMuPDF** para:
            - Divisão precisa por número de páginas
            - Extração de páginas específicas
            - Divisão por tamanho de arquivo
            - Remoção de páginas indesejadas
            
            **Modos de divisão:**
            
            📄 **Por Páginas:**
            - **A cada X páginas**: Divide em partes fixas (ex: 10 páginas cada)
            - **Em partes iguais**: Divide em N partes de tamanho similar
            - **Intervalos customizados**: Define páginas específicas para cada arquivo
            
            ✂️ **Extrair/Remover:**
            - **Extrair específicas**: Cria PDF apenas com páginas selecionadas
            - **Remover específicas**: Cria PDF removendo páginas indesejadas
            - **Formato flexível**: Use vírgulas (1,3,5) e hífens (5-10)
            
            📦 **Por Tamanho:**
            - **Limite de tamanho**: Divide quando atingir tamanho máximo
            - **Ideal para email**: Respeita limites de anexo
            - **Estimativa inteligente**: Calcula número provável de arquivos
            
            **Recursos especiais:**
            - Interface "for dummies" com exemplos claros
            - Download em ZIP para múltiplos arquivos
            - Nomes de arquivo descritivos
            - Validação de intervalos e páginas
            """)
            
            st.markdown("**💡 Dica:** Use 'Por Tamanho' para dividir PDFs grandes para envio por email!")
    

def split_by_pages(pdf_data, total_pages, filename):
    """
    Dividir PDF por número de páginas
    """
    st.markdown("### 📄 Dividir por Páginas")
    st.markdown("💡 **Como funciona**: Divide seu PDF em vários arquivos menores")
    
    # Opções de divisão com explicações
    split_mode = st.radio(
        "**Escolha como dividir:**",
        ["🔢 A cada X páginas", "⚡ Em partes iguais", "🎯 Intervalos customizados"],
        help="Selecione o modo que melhor se adequa ao seu objetivo"
    )
    
    if split_mode == "🔢 A cada X páginas":
        st.markdown("**📝 Exemplo**: Se você tem 30 páginas e escolher 10, vai gerar 3 arquivos")
        
        pages_per_file = st.number_input(
            "**Quantas páginas por arquivo?**",
            min_value=1,
            max_value=total_pages,
            value=min(10, total_pages),
            help="Cada arquivo novo terá no máximo esta quantidade de páginas"
        )
        
        # Calcular número de arquivos resultantes
        num_files = math.ceil(total_pages / pages_per_file)
        st.success(f"✅ **Resultado**: Serão gerados {num_files} arquivos")
        
        # Mostrar detalhes
        with st.expander("📋 Ver detalhes dos arquivos"):
            for i in range(num_files):
                start_page = i * pages_per_file + 1
                end_page = min((i + 1) * pages_per_file, total_pages)
                st.write(f"📄 Arquivo {i+1}: páginas {start_page} a {end_page}")
        
        st.markdown("---")
        
        col1, col2 = st.columns(2)
        with col1:
            if st.button("✂️ Dividir PDF", type="primary", use_container_width=True, key="split_by_x_pages"):
                split_pdf_by_pages(pdf_data, pages_per_file, filename)
        with col2:
            if st.button("🔄 Começar Novamente", type="secondary", use_container_width=True, key="restart_x_pages"):
                clear_splitter_data()
                st.rerun()
    
    elif split_mode == "⚡ Em partes iguais":
        st.markdown("**📝 Exemplo**: Se você tem 30 páginas e escolher 3 partes, cada arquivo terá 10 páginas")
        
        num_parts = st.number_input(
            "**Em quantas partes dividir?**",
            min_value=2,
            max_value=total_pages,
            value=min(3, total_pages),
            help="O PDF será dividido em partes de tamanho similar"
        )
        
        # Calcular páginas por parte
        pages_per_part = math.ceil(total_pages / num_parts)
        st.success(f"✅ **Resultado**: {num_parts} arquivos com ~{pages_per_part} páginas cada")
        
        # Mostrar detalhes
        with st.expander("📋 Ver detalhes dos arquivos"):
            for i in range(num_parts):
                start_page = i * pages_per_part + 1
                end_page = min((i + 1) * pages_per_part, total_pages)
                st.write(f"📄 Arquivo {i+1}: páginas {start_page} a {end_page}")
        
        st.markdown("---")
        
        col1, col2 = st.columns(2)
        with col1:
            if st.button("✂️ Dividir PDF", type="primary", use_container_width=True, key="split_by_n_parts"):
                split_pdf_by_pages(pdf_data, pages_per_part, filename)
        with col2:
            if st.button("🔄 Começar Novamente", type="secondary", use_container_width=True, key="restart_n_parts"):
                clear_splitter_data()
                st.rerun()
    
    else:  # Intervalos customizados
        st.markdown("**📝 Exemplo**: Para criar 3 arquivos com páginas 1-5, 6-10 e 11-15")
        st.markdown("**🎯 Use quando**: Quiser páginas específicas em cada arquivo")
        
        intervals_text = st.text_area(
            "**Digite os intervalos (um por linha):**",
            value="1-10\n11-20\n21-30",
            help="Formato: início-fim (exemplo: 1-5). Uma linha para cada arquivo",
            height=100
        )
        
        # Validar e mostrar preview
        if intervals_text:
            try:
                intervals = parse_intervals(intervals_text, total_pages)
                st.success(f"✅ **Resultado**: {len(intervals)} arquivos serão criados")
                
                with st.expander("📋 Ver detalhes dos arquivos"):
                    for i, (start, end) in enumerate(intervals):
                        st.write(f"📄 Arquivo {i+1}: páginas {start} a {end}")
                        
            except Exception as e:
                st.error(f"❌ **Erro**: {str(e)}")
                st.markdown("**💡 Dica**: Use o formato 1-10 (início-fim) em cada linha")
        
        st.markdown("---")
        
        col1, col2 = st.columns(2)
        with col1:
            if st.button("✂️ Dividir PDF", type="primary", use_container_width=True, key="split_by_intervals"):
                try:
                    intervals = parse_intervals(intervals_text, total_pages)
                    split_pdf_by_intervals(pdf_data, intervals, filename)
                except Exception as e:
                    st.error(f"❌ Erro ao processar intervalos: {str(e)}")
        with col2:
            if st.button("🔄 Começar Novamente", type="secondary", use_container_width=True, key="restart_intervals"):
                clear_splitter_data()
                st.rerun()


def extract_remove_pages(pdf_data, total_pages, filename):
    """
    Extrair ou remover páginas específicas
    """
    st.markdown("### ✂️ Extrair ou Remover Páginas")
    st.markdown("💡 **Como funciona**: Seleciona páginas específicas para manter ou remover")
    
    mode = st.radio(
        "**O que você quer fazer?**",
        ["📥 Extrair páginas específicas", "🗑️ Remover páginas específicas"],
        help="Extrair = manter apenas as páginas selecionadas | Remover = tirar as páginas selecionadas"
    )
    
    # Exemplos baseados no modo
    if mode == "📥 Extrair páginas específicas":
        st.markdown("**📝 Exemplo**: Digite `1,3,5-10` para criar um PDF só com essas páginas")
        st.markdown("**🎯 Use quando**: Quiser apenas algumas páginas do PDF")
    else:
        st.markdown("**📝 Exemplo**: Digite `2,4,6-8` para criar um PDF sem essas páginas")
        st.markdown("**🎯 Use quando**: Quiser tirar páginas indesejadas do PDF")
    
    # Input de páginas
    pages_input = st.text_input(
        "**Digite as páginas:**",
        placeholder="Ex: 1,3,5-10,15",
        help="Use vírgulas para páginas individuais (1,3,5) e hífen para intervalos (5-10)"
    )
    
    if pages_input:
        try:
            pages = parse_page_numbers(pages_input, total_pages)
            
            if mode == "📥 Extrair páginas específicas":
                st.success(f"✅ **Resultado**: PDF final terá {len(pages)} páginas")
                st.info(f"📄 **Páginas selecionadas**: {format_page_list(pages)}")
                
                st.markdown("---")
                col1, col2 = st.columns(2)
                with col1:
                    if st.button("📥 Extrair Páginas", type="primary", use_container_width=True, key="extract_pages"):
                        extract_specific_pages(pdf_data, pages, filename)
                with col2:
                    if st.button("🔄 Começar Novamente", type="secondary", use_container_width=True, key="restart_extract"):
                        clear_splitter_data()
                        st.rerun()
            else:
                pages_to_keep = [p for p in range(1, total_pages + 1) if p not in pages]
                st.success(f"✅ **Resultado**: PDF final terá {len(pages_to_keep)} páginas")
                st.info(f"🗑️ **Páginas removidas**: {format_page_list(pages)}")
                
                st.markdown("---")
                col1, col2 = st.columns(2)
                with col1:
                    if st.button("🗑️ Remover Páginas", type="primary", use_container_width=True, key="remove_pages"):
                        extract_specific_pages(pdf_data, pages_to_keep, filename, mode="remove")
                with col2:
                    if st.button("🔄 Começar Novamente", type="secondary", use_container_width=True, key="restart_remove"):
                        clear_splitter_data()
                        st.rerun()
                    
        except Exception as e:
            st.error(f"❌ Erro: {str(e)}")


def split_by_size(pdf_data, total_pages, file_size_mb, filename):
    """
    Dividir PDF por tamanho máximo
    """
    st.markdown("### 📦 Dividir por Tamanho")
    st.markdown("💡 **Como funciona**: Divide o PDF quando atingir o tamanho máximo escolhido")
    st.markdown("**🎯 Use quando**: Precisar enviar por email ou sistemas com limite de tamanho")
    
    # Mostrar tamanho atual com melhor formatação
    if file_size_mb < 0.1:
        size_display = f"{file_size_mb:.3f} MB"
    else:
        size_display = f"{file_size_mb:.1f} MB"
    
    st.info(f"📊 **Tamanho atual**: {size_display} ({total_pages} páginas)")
    
    # Tamanho máximo por arquivo
    max_size_mb = st.number_input(
        "**Tamanho máximo por arquivo (MB):**",
        min_value=0.01,  # Permitir arquivos muito pequenos
        max_value=max(file_size_mb, 0.01),  # Garantir que max não seja menor que min
        value=min(10.0, max(file_size_mb, 0.01)),
        step=0.01,
        format="%.2f",
        help="Cada arquivo novo terá no máximo este tamanho"
    )
    
    # Estimar número de arquivos
    estimated_files = math.ceil(file_size_mb / max_size_mb)
    avg_pages_per_file = total_pages // estimated_files if estimated_files > 0 else total_pages
    
    # Verificar se vale a pena dividir
    if max_size_mb >= file_size_mb:
        st.warning(f"⚠️ **Atenção**: O tamanho máximo ({max_size_mb:.2f} MB) é maior que o arquivo atual ({file_size_mb:.3f} MB)")
        st.info("💡 Neste caso, será gerado apenas 1 arquivo igual ao original")
        estimated_files = 1
        avg_pages_per_file = total_pages
    
    st.success(f"✅ **Resultado**: ~{estimated_files} arquivos com ~{avg_pages_per_file} páginas cada")
    
    # Aviso sobre variação
    with st.expander("💡 Informação importante"):
        st.warning("⚠️ O tamanho final pode variar dependendo do conteúdo de cada página")
        st.markdown("- Páginas com muitas imagens = arquivos maiores")
        st.markdown("- Páginas só com texto = arquivos menores")
        st.markdown("- O sistema tenta manter o limite, mas pode haver pequenas variações")
    
    st.markdown("---")
    
    col1, col2 = st.columns(2)
    with col1:
        if st.button("✂️ Dividir PDF", type="primary", use_container_width=True, key="split_by_size"):
            split_pdf_by_size(pdf_data, max_size_mb, filename)
    with col2:
        if st.button("🔄 Começar Novamente", type="secondary", use_container_width=True, key="restart_by_size"):
            clear_splitter_data()
            st.rerun()


# Funções auxiliares de processamento

def split_pdf_by_pages(pdf_data, pages_per_file, filename):
    """
    Divide PDF em arquivos com número fixo de páginas
    """
    try:
        with st.spinner("✂️ Dividindo PDF..."):
            doc = fitz.open(stream=pdf_data, filetype="pdf")
            total_pages = doc.page_count
            num_files = math.ceil(total_pages / pages_per_file)
            
            # Criar ZIP para múltiplos arquivos
            zip_buffer = BytesIO()
            with zipfile.ZipFile(zip_buffer, 'w', zipfile.ZIP_DEFLATED) as zip_file:
                
                for i in range(num_files):
                    start_page = i * pages_per_file
                    end_page = min((i + 1) * pages_per_file, total_pages)
                    
                    # Criar novo PDF
                    new_doc = fitz.open()
                    for page_num in range(start_page, end_page):
                        new_doc.insert_pdf(doc, from_page=page_num, to_page=page_num)
                    
                    # Salvar no ZIP
                    pdf_bytes = new_doc.tobytes()
                    base_name = filename.replace('.pdf', '')
                    part_name = f"{base_name}_parte_{i+1}_pags_{start_page+1}-{end_page}.pdf"
                    zip_file.writestr(part_name, pdf_bytes)
                    new_doc.close()
            
            doc.close()
            zip_buffer.seek(0)
            
            # Download
            st.success(f"✅ PDF dividido em {num_files} partes!")
            st.download_button(
                label="📥 Baixar Arquivos Divididos (ZIP)",
                data=zip_buffer.getvalue(),
                file_name=f"{filename.replace('.pdf', '')}_dividido.zip",
                mime="application/zip",
                type="primary"
            )
            
    except Exception as e:
        st.error(f"❌ Erro ao dividir PDF: {str(e)}")


def split_pdf_by_intervals(pdf_data, intervals, filename):
    """
    Divide PDF por intervalos customizados
    """
    try:
        with st.spinner("✂️ Dividindo PDF por intervalos..."):
            doc = fitz.open(stream=pdf_data, filetype="pdf")
            
            # Criar ZIP
            zip_buffer = BytesIO()
            with zipfile.ZipFile(zip_buffer, 'w', zipfile.ZIP_DEFLATED) as zip_file:
                
                for i, (start, end) in enumerate(intervals):
                    # Criar novo PDF
                    new_doc = fitz.open()
                    for page_num in range(start - 1, end):
                        new_doc.insert_pdf(doc, from_page=page_num, to_page=page_num)
                    
                    # Salvar no ZIP
                    pdf_bytes = new_doc.tobytes()
                    base_name = filename.replace('.pdf', '')
                    part_name = f"{base_name}_pags_{start}-{end}.pdf"
                    zip_file.writestr(part_name, pdf_bytes)
                    new_doc.close()
            
            doc.close()
            zip_buffer.seek(0)
            
            # Download
            st.success(f"✅ PDF dividido em {len(intervals)} partes!")
            st.download_button(
                label="📥 Baixar Arquivos Divididos (ZIP)",
                data=zip_buffer.getvalue(),
                file_name=f"{filename.replace('.pdf', '')}_intervalos.zip",
                mime="application/zip",
                type="primary"
            )
            
    except Exception as e:
        st.error(f"❌ Erro ao dividir PDF: {str(e)}")


def extract_specific_pages(pdf_data, page_numbers, filename, mode="extract"):
    """
    Extrai páginas específicas do PDF
    """
    try:
        with st.spinner("📄 Processando páginas..."):
            doc = fitz.open(stream=pdf_data, filetype="pdf")
            
            # Criar novo PDF
            new_doc = fitz.open()
            for page_num in page_numbers:
                new_doc.insert_pdf(doc, from_page=page_num - 1, to_page=page_num - 1)
            
            # Gerar bytes
            pdf_bytes = new_doc.tobytes()
            new_doc.close()
            doc.close()
            
            # Nome do arquivo
            base_name = filename.replace('.pdf', '')
            if mode == "extract":
                output_name = f"{base_name}_extraido.pdf"
                success_msg = f"✅ {len(page_numbers)} páginas extraídas!"
            else:
                output_name = f"{base_name}_removido.pdf"
                success_msg = f"✅ Páginas removidas! PDF resultante tem {len(page_numbers)} páginas."
            
            # Download
            st.success(success_msg)
            st.download_button(
                label="📥 Baixar PDF Processado",
                data=pdf_bytes,
                file_name=output_name,
                mime="application/pdf",
                type="primary"
            )
            
    except Exception as e:
        st.error(f"❌ Erro ao processar páginas: {str(e)}")


def split_pdf_by_size(pdf_data, max_size_mb, filename):
    """
    Divide PDF por tamanho máximo
    """
    try:
        with st.spinner("📦 Dividindo PDF por tamanho..."):
            doc = fitz.open(stream=pdf_data, filetype="pdf")
            total_pages = doc.page_count
            max_size_bytes = max_size_mb * 1024 * 1024
            
            # Criar ZIP
            zip_buffer = BytesIO()
            with zipfile.ZipFile(zip_buffer, 'w', zipfile.ZIP_DEFLATED) as zip_file:
                
                part_num = 1
                current_doc = fitz.open()
                current_size = 0
                start_page = 1
                
                for page_num in range(total_pages):
                    # Adicionar página ao documento atual
                    current_doc.insert_pdf(doc, from_page=page_num, to_page=page_num)
                    
                    # Estimar tamanho (aproximado)
                    temp_bytes = current_doc.tobytes()
                    current_size = len(temp_bytes)
                    
                    # Se excedeu o tamanho ou é a última página
                    if current_size >= max_size_bytes or page_num == total_pages - 1:
                        # Salvar parte atual
                        base_name = filename.replace('.pdf', '')
                        part_name = f"{base_name}_parte_{part_num}.pdf"
                        zip_file.writestr(part_name, temp_bytes)
                        
                        # Preparar próxima parte
                        current_doc.close()
                        current_doc = fitz.open()
                        part_num += 1
                        start_page = page_num + 2
                
                if current_doc.page_count > 0:
                    current_doc.close()
            
            doc.close()
            zip_buffer.seek(0)
            
            # Download
            st.success(f"✅ PDF dividido em {part_num - 1} partes!")
            st.download_button(
                label="📥 Baixar Arquivos Divididos (ZIP)",
                data=zip_buffer.getvalue(),
                file_name=f"{filename.replace('.pdf', '')}_por_tamanho.zip",
                mime="application/zip",
                type="primary"
            )
            
    except Exception as e:
        st.error(f"❌ Erro ao dividir PDF: {str(e)}")


# Funções de parsing

def parse_intervals(text, total_pages):
    """
    Parse de intervalos de texto para lista de tuplas
    """
    intervals = []
    lines = text.strip().split('\n')
    
    for line in lines:
        line = line.strip()
        if not line:
            continue
            
        if '-' in line:
            start, end = line.split('-')
            start = int(start.strip())
            end = int(end.strip())
            
            if start < 1 or end > total_pages or start > end:
                raise ValueError(f"Intervalo inválido: {line}")
                
            intervals.append((start, end))
        else:
            raise ValueError(f"Formato inválido: {line}. Use início-fim (ex: 1-10)")
    
    return intervals


def parse_page_numbers(text, total_pages):
    """
    Parse de números de página (1,3,5-10,15)
    """
    pages = set()
    parts = text.replace(' ', '').split(',')
    
    for part in parts:
        if '-' in part:
            start, end = part.split('-')
            start = int(start)
            end = int(end)
            
            if start < 1 or end > total_pages or start > end:
                raise ValueError(f"Intervalo inválido: {part}")
                
            pages.update(range(start, end + 1))
        else:
            page = int(part)
            if page < 1 or page > total_pages:
                raise ValueError(f"Página inválida: {page}")
            pages.add(page)
    
    return sorted(list(pages))


def format_page_list(pages):
    """
    Formata lista de páginas para exibição
    """
    if len(pages) <= 10:
        return ', '.join(map(str, pages))
    else:
        return f"{', '.join(map(str, pages[:5]))}... {', '.join(map(str, pages[-5:]))}"