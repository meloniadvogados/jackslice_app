import streamlit as st
import tempfile
import os
import zipfile
from io import BytesIO
from pathlib import Path
import json
from typing import List, Dict, Any, Callable, Optional

class StreamlitProgressCallback:
    """Classe para gerenciar progresso no Streamlit"""
    
    def __init__(self, total_steps: int, description: str = "Processando..."):
        self.total_steps = total_steps
        self.current_step = 0
        self.description = description
        self.progress_bar = st.progress(0)
        self.status_text = st.empty()
        
    def update(self, step: int, message: str = ""):
        """Atualiza o progresso"""
        self.current_step = step
        progress = min(step / self.total_steps, 1.0)
        self.progress_bar.progress(progress)
        
        if message:
            self.status_text.text(f"{self.description} - {message}")
        else:
            self.status_text.text(f"{self.description} - {step}/{self.total_steps}")
    
    def complete(self, message: str = "Concluído!"):
        """Finaliza o progresso"""
        self.progress_bar.progress(1.0)
        self.status_text.text(message)
    
    def clear(self):
        """Remove elementos de progresso"""
        self.progress_bar.empty()
        self.status_text.empty()

class StreamlitFileManager:
    """Gerenciador de arquivos para Streamlit"""
    
    @staticmethod
    def save_uploaded_file(uploaded_file) -> str:
        """Salva arquivo carregado em arquivo temporário"""
        with tempfile.NamedTemporaryFile(delete=False, suffix=f".{uploaded_file.name.split('.')[-1]}") as tmp_file:
            tmp_file.write(uploaded_file.getvalue())
            return tmp_file.name
    
    @staticmethod
    def create_download_zip(files_dict: Dict[str, bytes], zip_name: str = "download.zip") -> bytes:
        """Cria arquivo ZIP em memória"""
        zip_buffer = BytesIO()
        
        with zipfile.ZipFile(zip_buffer, 'w', zipfile.ZIP_DEFLATED) as zip_file:
            for filename, file_data in files_dict.items():
                zip_file.writestr(filename, file_data)
        
        zip_buffer.seek(0)
        return zip_buffer.getvalue()
    
    @staticmethod
    def cleanup_temp_file(file_path: str):
        """Remove arquivo temporário"""
        try:
            if os.path.exists(file_path):
                os.unlink(file_path)
        except Exception:
            pass

class StreamlitSessionManager:
    """Gerenciador de estado da sessão Streamlit"""
    
    @staticmethod
    def init_session_state(key: str, default_value: Any):
        """Inicializa chave no session state se não existir"""
        if key not in st.session_state:
            st.session_state[key] = default_value
    
    @staticmethod
    def get_session_value(key: str, default_value: Any = None):
        """Obtém valor do session state"""
        return st.session_state.get(key, default_value)
    
    @staticmethod
    def set_session_value(key: str, value: Any):
        """Define valor no session state"""
        st.session_state[key] = value
    
    @staticmethod
    def clear_session_keys(keys: List[str]):
        """Limpa chaves específicas do session state"""
        for key in keys:
            if key in st.session_state:
                del st.session_state[key]
    
    @staticmethod
    def reset_processing_state():
        """Reseta estado de processamento"""
        keys_to_clear = [
            'processing_complete', 'sections_data', 'pdf_path',
            'filename_base', 'numero_processo', 'sections_to_download',
            'optimized_pdf_data', 'ocr_pdf_data'
        ]
        StreamlitSessionManager.clear_session_keys(keys_to_clear)

class StreamlitUIHelpers:
    """Helpers para UI no Streamlit"""
    
    @staticmethod
    def show_file_info(uploaded_file):
        """Mostra informações do arquivo carregado"""
        file_size = len(uploaded_file.getvalue())
        st.success(f"📄 Arquivo carregado: {uploaded_file.name}")
        st.info(f"📊 Tamanho: {file_size / (1024*1024):.2f} MB")
        return file_size
    
    @staticmethod
    def show_error_with_details(error_message: str, error_details: str = None):
        """Mostra erro com detalhes opcionais"""
        st.error(error_message)
        if error_details:
            with st.expander("🔍 Detalhes do Erro"):
                st.code(error_details)
    
    @staticmethod
    def show_processing_results(original_size: int, processed_size: int, 
                              operation: str = "processamento"):
        """Mostra resultados de processamento"""
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.metric("📊 Tamanho Original", f"{original_size / (1024*1024):.2f} MB")
        
        with col2:
            st.metric(f"📄 Após {operation}", f"{processed_size / (1024*1024):.2f} MB")
        
        with col3:
            if processed_size < original_size:
                reduction = ((original_size - processed_size) / original_size) * 100
                st.metric("💾 Redução", f"{reduction:.1f}%")
            else:
                increase = ((processed_size - original_size) / original_size) * 100
                st.metric("📈 Aumento", f"{increase:.1f}%")
    
    @staticmethod
    def create_download_button(data: bytes, filename: str, label: str = "📥 Baixar Arquivo"):
        """Cria botão de download padronizado"""
        mime_type = "application/pdf" if filename.endswith('.pdf') else "application/octet-stream"
        
        return st.download_button(
            label=label,
            data=data,
            file_name=filename,
            mime=mime_type,
            type="primary"
        )
    
    @staticmethod
    def show_sections_table(sections: List[Dict], allow_selection: bool = True) -> List[Dict]:
        """Mostra tabela de seções com seleção opcional"""
        if not sections:
            st.warning("⚠️ Nenhuma seção encontrada")
            return []
        
        selected_sections = []
        
        # Checkbox para selecionar todas
        if allow_selection:
            col1, col2 = st.columns([1, 3])
            with col1:
                select_all = st.checkbox("✅ Selecionar todas", value=False)
        
        st.markdown("---")
        
        # Cabeçalho da tabela
        cols = st.columns([0.5, 1, 2, 4, 2, 1, 1] if allow_selection else [1, 2, 4, 2, 1, 1])
        
        headers = ["Sel.", "ID", "Data", "Documento", "Tipo", "Pág. Inicial", "Pág. Final"]
        if not allow_selection:
            headers = headers[1:]  # Remove coluna de seleção
        
        for i, header in enumerate(headers):
            with cols[i]:
                st.markdown(f"**{header}**")
        
        st.markdown("---")
        
        # Linhas de dados
        for i, section in enumerate(sections):
            cols = st.columns([0.5, 1, 2, 4, 2, 1, 1] if allow_selection else [1, 2, 4, 2, 1, 1])
            
            col_idx = 0
            
            # Checkbox de seleção
            if allow_selection:
                with cols[col_idx]:
                    selected = st.checkbox(
                        f"sel_{i}", 
                        value=select_all, 
                        key=f"section_{i}", 
                        label_visibility="collapsed"
                    )
                    if selected:
                        selected_sections.append(section)
                col_idx += 1
            
            # Dados da seção
            data_fields = [
                section.get("id", ""),
                section.get("data", ""),
                (section.get("documento", "")[:40] + "..." 
                 if len(section.get("documento", "")) > 40 
                 else section.get("documento", "")),
                section.get("tipo", ""),
                section.get("pagina_inicial", ""),
                section.get("pagina_final", "")
            ]
            
            for field in data_fields:
                with cols[col_idx]:
                    st.text(str(field))
                col_idx += 1
        
        if allow_selection and selected_sections:
            st.success(f"📊 {len(selected_sections)} seção(ões) selecionada(s)")
        
        return selected_sections

class StreamlitDataPersistence:
    """Gerenciamento de persistência de dados no Streamlit"""
    
    @staticmethod
    def save_processing_data(filename: str, data: Dict[str, Any]):
        """Salva dados de processamento"""
        try:
            data_dir = Path("data")
            data_dir.mkdir(exist_ok=True)
            
            file_path = data_dir / f"{filename}.json"
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
            
            return str(file_path)
        except Exception as e:
            st.error(f"Erro ao salvar dados: {e}")
            return None
    
    @staticmethod
    def load_processing_data(filename: str) -> Optional[Dict[str, Any]]:
        """Carrega dados de processamento"""
        try:
            data_dir = Path("data")
            file_path = data_dir / f"{filename}.json"
            
            if file_path.exists():
                with open(file_path, 'r', encoding='utf-8') as f:
                    return json.load(f)
            return None
        except Exception as e:
            st.error(f"Erro ao carregar dados: {e}")
            return None
    
    @staticmethod
    def list_saved_data() -> List[str]:
        """Lista dados salvos"""
        try:
            data_dir = Path("data")
            if data_dir.exists():
                return [f.stem for f in data_dir.glob("*.json")]
            return []
        except Exception:
            return []

# Decorador para funções que processam arquivos
def streamlit_file_processor(cleanup_temp_files: bool = True):
    """Decorador para processamento de arquivos no Streamlit"""
    def decorator(func):
        def wrapper(*args, **kwargs):
            temp_files = []
            try:
                result = func(*args, **kwargs)
                return result
            except Exception as e:
                StreamlitUIHelpers.show_error_with_details(
                    f"Erro durante {func.__name__}",
                    str(e)
                )
                return None
            finally:
                if cleanup_temp_files:
                    for temp_file in temp_files:
                        StreamlitFileManager.cleanup_temp_file(temp_file)
        return wrapper
    return decorator