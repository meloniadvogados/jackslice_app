#!/usr/bin/env python3
"""
🔒 Session Manager - Isolamento Multi-Usuário
Gerencia sessões de usuário para evitar conflitos em ambiente multi-usuário
"""

import os
import uuid
import time
import tempfile
import shutil
import threading
from pathlib import Path
from typing import Dict, Optional
import streamlit as st

class SessionManager:
    """Gerenciador de sessões para isolamento multi-usuário"""
    
    _instance = None
    _lock = threading.Lock()
    
    def __new__(cls):
        if cls._instance is None:
            with cls._lock:
                if cls._instance is None:
                    cls._instance = super().__new__(cls)
        return cls._instance
    
    def __init__(self):
        if not hasattr(self, 'initialized'):
            self.sessions: Dict[str, Dict] = {}
            self.base_temp_dir = Path(tempfile.gettempdir()) / "jack_pdf_slicer"
            self.base_temp_dir.mkdir(exist_ok=True)
            self.cleanup_interval = 3600  # 1 hora
            self.last_cleanup = time.time()
            self.initialized = True
    
    def get_session_id(self) -> str:
        """Obtém ou cria session ID único"""
        if 'session_id' not in st.session_state:
            st.session_state.session_id = str(uuid.uuid4())
        return st.session_state.session_id
    
    def get_session_dir(self, session_id: Optional[str] = None) -> Path:
        """Obtém diretório específico da sessão"""
        if session_id is None:
            session_id = self.get_session_id()
        
        session_dir = self.base_temp_dir / f"session_{session_id}"
        session_dir.mkdir(exist_ok=True)
        
        # Criar subdiretórios
        (session_dir / "uploads").mkdir(exist_ok=True)
        (session_dir / "output").mkdir(exist_ok=True)
        (session_dir / "data").mkdir(exist_ok=True)
        
        return session_dir
    
    def save_uploaded_file(self, uploaded_file, session_id: Optional[str] = None) -> str:
        """Salva arquivo uploadado na sessão específica"""
        if session_id is None:
            session_id = self.get_session_id()
        
        session_dir = self.get_session_dir(session_id)
        upload_dir = session_dir / "uploads"
        
        # Nome único do arquivo
        file_id = str(uuid.uuid4())[:8]
        filename = f"{file_id}_{uploaded_file.name}"
        file_path = upload_dir / filename
        
        # Salvar arquivo
        with open(file_path, 'wb') as f:
            f.write(uploaded_file.getvalue())
        
        # Registrar na sessão
        if session_id not in self.sessions:
            self.sessions[session_id] = {
                'created_at': time.time(),
                'files': [],
                'last_access': time.time()
            }
        
        self.sessions[session_id]['files'].append({
            'file_id': file_id,
            'original_name': uploaded_file.name,
            'path': str(file_path),
            'size': len(uploaded_file.getvalue()),
            'uploaded_at': time.time()
        })
        
        self.sessions[session_id]['last_access'] = time.time()
        
        return str(file_path)
    
    def get_session_info(self, session_id: Optional[str] = None) -> Dict:
        """Obtém informações da sessão"""
        if session_id is None:
            session_id = self.get_session_id()
        
        return self.sessions.get(session_id, {
            'created_at': time.time(),
            'files': [],
            'last_access': time.time()
        })
    
    def cleanup_session(self, session_id: str):
        """Limpa dados de uma sessão específica"""
        try:
            # Remover diretório da sessão
            session_dir = self.base_temp_dir / f"session_{session_id}"
            if session_dir.exists():
                shutil.rmtree(session_dir)
            
            # Remover do registro
            if session_id in self.sessions:
                del self.sessions[session_id]
                
        except Exception as e:
            print(f"Erro ao limpar sessão {session_id}: {e}")
    
    def cleanup_old_sessions(self, max_age: int = 3600):
        """Limpa sessões antigas (padrão: 1 hora)"""
        current_time = time.time()
        expired_sessions = []
        
        for session_id, session_data in self.sessions.items():
            if current_time - session_data['last_access'] > max_age:
                expired_sessions.append(session_id)
        
        for session_id in expired_sessions:
            self.cleanup_session(session_id)
            print(f"Sessão expirada removida: {session_id}")
    
    def auto_cleanup(self):
        """Limpeza automática se necessário"""
        current_time = time.time()
        if current_time - self.last_cleanup > self.cleanup_interval:
            self.cleanup_old_sessions()
            self.last_cleanup = current_time
    
    def get_stats(self) -> Dict:
        """Estatísticas do sistema"""
        total_sessions = len(self.sessions)
        total_files = sum(len(session['files']) for session in self.sessions.values())
        
        # Calcular uso de disco
        total_size = 0
        for session_id in self.sessions:
            session_dir = self.base_temp_dir / f"session_{session_id}"
            if session_dir.exists():
                for file_path in session_dir.rglob('*'):
                    if file_path.is_file():
                        try:
                            total_size += file_path.stat().st_size
                        except:
                            pass
        
        return {
            'total_sessions': total_sessions,
            'total_files': total_files,
            'total_size_mb': total_size / (1024 * 1024),
            'base_dir': str(self.base_temp_dir)
        }

class StatelessFileManager:
    """Gerenciador de arquivos stateless para operações em memória"""
    
    @staticmethod
    def process_pdf_in_memory(pdf_data: bytes, filename: str) -> Dict:
        """Processa PDF completamente em memória"""
        import tempfile
        import os
        from core.XPTO import XPTO
        from core.processo_numero_extractor import ProcessoNumeroExtractor
        
        # Criar arquivo temporário que persiste durante todo o processamento
        tmp_file = tempfile.NamedTemporaryFile(delete=False, suffix='.pdf')
        try:
            tmp_file.write(pdf_data)
            tmp_file.flush()
            tmp_file.close()  # Fechar para liberar handle
            
            # Verificar se arquivo foi criado corretamente
            if not os.path.exists(tmp_file.name):
                raise FileNotFoundError(f"Arquivo temporário não foi criado: {tmp_file.name}")
            
            # Verificar permissões
            if not os.access(tmp_file.name, os.R_OK):
                raise PermissionError(f"Sem permissão de leitura: {tmp_file.name}")
            
            # Extrair número do processo
            try:
                numero_processo = ProcessoNumeroExtractor(tmp_file.name).extrair_numero()
            except Exception as e:
                print(f"[WARNING] Erro ao extrair número do processo: {e}")
                numero_processo = ""
            
            # Executar pipeline
            pipeline = XPTO(tmp_file.name)
            sections = pipeline.run()
            
            return {
                'filename': filename,
                'numero_processo': numero_processo,
                'sections': sections,
                'processed_at': time.time(),
                'temp_file_path': tmp_file.name  # Retornar path para uso posterior
            }
            
        except Exception as e:
            # Limpar arquivo em caso de erro
            try:
                if os.path.exists(tmp_file.name):
                    os.unlink(tmp_file.name)
            except:
                pass
            raise e
    
    @staticmethod
    def extract_sections_to_zip(pdf_data: bytes, sections: list, temp_file_path: str = None) -> bytes:
        """Extrai seções e retorna ZIP em memória"""
        import tempfile
        import zipfile
        import os
        from io import BytesIO
        from core.pdf_extract_runner import PDFExtractRunner
        from core.utils import sanitize_filename
        
        zip_buffer = BytesIO()
        
        # Usar arquivo temporário existente ou criar novo
        if temp_file_path and os.path.exists(temp_file_path):
            # Usar arquivo existente
            pdf_path = temp_file_path
            cleanup_main = False
        else:
            # Criar novo arquivo temporário
            tmp_file = tempfile.NamedTemporaryFile(delete=False, suffix='.pdf')
            try:
                tmp_file.write(pdf_data)
                tmp_file.flush()
                pdf_path = tmp_file.name
                cleanup_main = True
            finally:
                tmp_file.close()
        
        try:
            runner = PDFExtractRunner(pdf_path)
            
            with zipfile.ZipFile(zip_buffer, 'w', zipfile.ZIP_DEFLATED) as zip_file:
                for i, section in enumerate(sections):
                    start_page = int(section.get("pagina_inicial", 1))
                    end_page = int(section.get("pagina_final", start_page))
                    doc_name = sanitize_filename(section.get("documento", f"secao_{i+1}"))
                    
                    # Extrair seção - o PDFExtractRunner retorna bytes em memória
                    try:
                        pdf_bytes = runner.extrair_intervalo(start_page, end_page)
                        
                        # Verificar se os bytes foram gerados
                        if pdf_bytes and len(pdf_bytes) > 0:
                            zip_file.writestr(f"{doc_name}.pdf", pdf_bytes)
                        else:
                            print(f"[WARNING] Seção {doc_name} não pôde ser extraída")
                    except Exception as e:
                        print(f"[ERROR] Erro ao extrair seção {doc_name}: {e}")
            
            zip_buffer.seek(0)
            return zip_buffer.getvalue()
            
        finally:
            # Limpar arquivo principal se criado aqui
            if cleanup_main:
                try:
                    os.unlink(pdf_path)
                except:
                    pass

# Instância global (singleton)
session_manager = SessionManager()

def get_session_manager() -> SessionManager:
    """Obtém instância do gerenciador de sessão"""
    return session_manager

# Instância global do SettingsManager
from core.settings_manager import SettingsManager
_settings_manager = None

def get_settings_manager() -> SettingsManager:
    """Obtém instância do gerenciador de configurações"""
    global _settings_manager
    if _settings_manager is None:
        _settings_manager = SettingsManager()
    return _settings_manager

def cleanup_on_exit():
    """Limpeza ao encerrar aplicação"""
    try:
        session_manager.cleanup_old_sessions(max_age=0)  # Limpar tudo
    except:
        pass