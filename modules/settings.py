import streamlit as st
import os
import json
import hashlib
from pathlib import Path
from core.settings_manager import SettingsManager

def check_password():
    """Verifica se a senha está correta"""
    
    # Carregar configuração da senha
    password_file = Path("data/password.json")
    
    # Criar senha padrão se não existir
    if not password_file.exists():
        os.makedirs("data", exist_ok=True)
        default_password = "admin123"
        password_hash = hashlib.sha256(default_password.encode()).hexdigest()
        
        with open(password_file, "w") as f:
            json.dump({"password_hash": password_hash}, f)
        
        st.warning(f"⚠️ Senha padrão criada: **{default_password}**")
        st.info("💡 Altere a senha nas configurações após fazer login")
    
    # Carregar hash da senha
    try:
        with open(password_file, "r") as f:
            config = json.load(f)
            stored_hash = config.get("password_hash", "")
    except:
        stored_hash = ""
    
    # Verificar se já está autenticado na sessão
    if st.session_state.get("authenticated", False):
        return True
    
    # Tela de login
    st.title("🔒 Acesso às Configurações")
    st.markdown("---")
    
    col1, col2, col3 = st.columns([1, 2, 1])
    
    with col2:
        st.markdown("### 🔑 Digite a senha para acessar")
        
        password = st.text_input(
            "Senha:",
            type="password",
            placeholder="Digite sua senha...",
            key="login_password"
        )
        
        col_a, col_b = st.columns(2)
        
        with col_a:
            if st.button("🚀 Entrar", type="primary", use_container_width=True):
                if password:
                    input_hash = hashlib.sha256(password.encode()).hexdigest()
                    if input_hash == stored_hash:
                        st.session_state.authenticated = True
                        st.success("✅ Acesso liberado!")
                        st.rerun()
                    else:
                        st.error("❌ Senha incorreta!")
                else:
                    st.warning("⚠️ Digite uma senha")
        
        with col_b:
            if st.button("🏠 Voltar", use_container_width=True):
                st.switch_page("app.py")
    
    return False

def settings_page():
    # Verificar autenticação
    if not check_password():
        return
    
    st.title("⚙️ Configurações")
    
    # Botão de logout
    col1, col2 = st.columns([4, 1])
    with col2:
        if st.button("🚪 Sair", type="secondary"):
            st.session_state.authenticated = False
            st.rerun()
    
    st.markdown("---")
    
    # Inicializar settings manager
    if 'settings_manager' not in st.session_state:
        st.session_state.settings_manager = SettingsManager()
    
    settings_manager = st.session_state.settings_manager
    current_settings = settings_manager.get_all()
    
    
    # Seção de Arquivos e Limites
    st.markdown("## 📁 Arquivos e Limites")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("### 📤 Upload de Arquivos")
        max_upload_size = st.slider(
            "Tamanho máximo de upload (MB):",
            min_value=10,
            max_value=500,
            value=current_settings.get("max_upload_size", 100),
            help="Tamanho máximo permitido para upload de PDFs"
        )
        
        session_timeout = st.slider(
            "Timeout de sessão (minutos):",
            min_value=5,
            max_value=120,
            value=current_settings.get("session_timeout", 1800) // 60,
            help="Tempo antes da sessão expirar"
        )
    
    with col2:
        st.markdown("### 🗂️ Arquivos Temporários")
        
        temp_retention = st.slider(
            "Retenção de temporários (minutos):",
            min_value=5,
            max_value=120,
            value=current_settings.get("temp_file_retention", 3600) // 60,
            help="Tempo para manter arquivos temporários"
        )
        
        # Mostrar uso atual
        try:
            temp_dir = settings_manager.get_temp_dir()
            if os.path.exists(temp_dir):
                files = list(Path(temp_dir).rglob("*"))
                file_count = len([f for f in files if f.is_file()])
                st.metric("Arquivos temporários", f"{file_count} arquivos")
        except:
            st.metric("Arquivos temporários", "N/A")
    
    st.markdown("---")
    
    # Seção de Processamento
    st.markdown("## 🔧 Processamento")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("### 📦 Compressão")
        compress_output = st.checkbox(
            "Comprimir PDFs de saída",
            value=current_settings.get("compress_output", False),
            help="Aplica compressão automática aos PDFs gerados"
        )
        
        if compress_output:
            compression_level = st.slider(
                "Nível de compressão:",
                min_value=1,
                max_value=9,
                value=5,
                help="1=Rápido, 9=Máximo"
            )
    
    with col2:
        st.markdown("### 🖱️ Comportamento")
        
        show_advanced = st.checkbox(
            "Mostrar opções avançadas",
            value=current_settings.get("show_advanced_options", False),
            help="Exibe opções avançadas nas telas"
        )
        
        auto_clean = st.checkbox(
            "Limpeza automática",
            value=True,
            help="Remove arquivos temporários antigos automaticamente"
        )
    
    st.markdown("---")
    
    # Seção de Performance
    st.markdown("## ⚡ Performance")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("### 🔄 Processamento Paralelo")
        max_threads = st.slider(
            "Máximo de threads:",
            min_value=1,
            max_value=16,
            value=4,
            help="Número máximo de threads para processamento paralelo"
        )
        
        chunk_size = st.slider(
            "Tamanho do chunk (MB):",
            min_value=1,
            max_value=100,
            value=10,
            help="Tamanho dos chunks para processamento de arquivos grandes"
        )
    
    with col2:
        st.markdown("### 💾 Cache")
        enable_cache = st.checkbox(
            "Habilitar cache",
            value=True,
            help="Armazena resultados para acelerar processamentos futuros"
        )
        
        if enable_cache:
            cache_size = st.slider(
                "Tamanho do cache (MB):",
                min_value=10,
                max_value=1000,
                value=100,
                help="Tamanho máximo do cache em disco"
            )
    
    st.markdown("---")
    
    # Seção de Logs e Debug
    st.markdown("## 📝 Logs e Debug")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("### 📋 Configurações de Log")
        log_level = st.selectbox(
            "Nível de log:",
            ["DEBUG", "INFO", "WARNING", "ERROR"],
            index=1,
            help="Nível de detalhamento dos logs"
        )
        
        log_to_file = st.checkbox(
            "Salvar logs em arquivo",
            value=True,
            help="Salva logs na pasta logs/"
        )
    
    with col2:
        st.markdown("### 🔍 Debug")
        debug_mode = st.checkbox(
            "Modo debug",
            value=False,
            help="Habilita informações detalhadas de debug"
        )
        
        if debug_mode:
            st.warning("⚠️ Modo debug pode gerar muitos logs")
    
    # Mostrar logs recentes
    if st.checkbox("📄 Mostrar logs recentes"):
        show_recent_logs()
    
    st.markdown("---")
    
    # Botões de ação
    col1, col2, col3 = st.columns(3)
    
    with col1:
        if st.button("💾 Salvar Configurações", type="primary"):
            save_settings(settings_manager, {
                "max_upload_size": max_upload_size,
                "session_timeout": session_timeout * 60,  # converter para segundos
                "temp_file_retention": temp_retention * 60,  # converter para segundos
                "compress_output": compress_output,
                "show_advanced_options": show_advanced,
                "max_threads": max_threads,
                "chunk_size": chunk_size,
                "enable_cache": enable_cache,
                "cache_size": cache_size if enable_cache else 0,
                "log_level": log_level,
                "log_to_file": log_to_file,
                "debug_mode": debug_mode
            })
    
    with col2:
        if st.button("🔄 Restaurar Padrões"):
            restore_defaults(settings_manager)
    
    with col3:
        if st.button("🗑️ Limpar Cache"):
            clear_cache()
    
    st.markdown("---")
    
    # Seção de Segurança
    st.markdown("## 🔒 Segurança")
    
    with st.expander("🔑 Alterar Senha de Acesso", expanded=False):
        st.markdown("### Alterar Senha das Configurações")
        
        col1, col2 = st.columns(2)
        
        with col1:
            current_password = st.text_input(
                "Senha atual:",
                type="password",
                key="current_pwd"
            )
        
        with col2:
            new_password = st.text_input(
                "Nova senha:",
                type="password",
                key="new_pwd"
            )
        
        confirm_password = st.text_input(
            "Confirmar nova senha:",
            type="password",
            key="confirm_pwd"
        )
        
        col_a, col_b = st.columns([1, 3])
        
        with col_a:
            if st.button("🔄 Alterar Senha", type="primary"):
                change_password(current_password, new_password, confirm_password)
        
        with col_b:
            st.info("💡 Use uma senha segura para proteger as configurações")
    
    st.markdown("---")
    
    # Seção de Informações do Sistema
    with st.expander("ℹ️ Informações do Sistema"):
        show_system_info()

def change_password(current_password, new_password, confirm_password):
    """Altera a senha de acesso às configurações"""
    
    # Validações
    if not current_password or not new_password or not confirm_password:
        st.error("❌ Preencha todos os campos!")
        return
    
    if new_password != confirm_password:
        st.error("❌ A confirmação de senha não confere!")
        return
    
    if len(new_password) < 4:
        st.error("❌ A nova senha deve ter pelo menos 4 caracteres!")
        return
    
    # Verificar senha atual
    password_file = Path("data/password.json")
    try:
        with open(password_file, "r") as f:
            config = json.load(f)
            stored_hash = config.get("password_hash", "")
        
        current_hash = hashlib.sha256(current_password.encode()).hexdigest()
        
        if current_hash != stored_hash:
            st.error("❌ Senha atual incorreta!")
            return
        
        # Salvar nova senha
        new_hash = hashlib.sha256(new_password.encode()).hexdigest()
        
        with open(password_file, "w") as f:
            json.dump({"password_hash": new_hash}, f)
        
        st.success("✅ Senha alterada com sucesso!")
        st.info("🔄 Faça logout e login novamente para aplicar a mudança")
        
    except Exception as e:
        st.error(f"❌ Erro ao alterar senha: {e}")

def save_settings(settings_manager, new_settings):
    """Salva as configurações"""
    try:
        # Usar o método genérico set() para cada configuração
        for key, value in new_settings.items():
            settings_manager.set(key, value)
        
        st.success("✅ Configurações salvas com sucesso!")
        
        # Recarregar página para aplicar mudanças
        st.rerun()
        
    except Exception as e:
        st.error(f"❌ Erro ao salvar configurações: {e}")

def restore_defaults(settings_manager):
    """Restaura configurações padrão"""
    try:
        settings_manager.reset_to_defaults()
        st.success("✅ Configurações restauradas para os padrões!")
        st.rerun()
        
    except Exception as e:
        st.error(f"❌ Erro ao restaurar configurações: {e}")

def clear_cache():
    """Limpa o cache do sistema"""
    try:
        from core.settings_manager import SettingsManager
        settings_mgr = SettingsManager()
        temp_dir = settings_mgr.get_temp_dir()
        
        cleared_files = 0
        
        # Limpar arquivos temporários
        if os.path.exists(temp_dir):
            for root, dirs, files in os.walk(temp_dir):
                for file in files:
                    try:
                        file_path = os.path.join(root, file)
                        # Remover arquivos mais antigos que a configuração
                        file_age = os.path.getctime(file_path)
                        current_time = __import__('time').time()
                        retention = settings_mgr.get('temp_file_retention', 3600)
                        
                        if current_time - file_age > retention:
                            os.remove(file_path)
                            cleared_files += 1
                    except:
                        pass
        
        # Limpar logs antigos
        logs_dir = "logs"
        if os.path.exists(logs_dir):
            for root, dirs, files in os.walk(logs_dir):
                for file in files:
                    if file.endswith(('.log', '.tmp')):
                        try:
                            file_path = os.path.join(root, file)
                            file_age = os.path.getctime(file_path)
                            current_time = __import__('time').time()
                            
                            # Manter logs dos últimos 7 dias
                            if current_time - file_age > 7 * 24 * 3600:
                                os.remove(file_path)
                                cleared_files += 1
                        except:
                            pass
        
        st.success(f"✅ Cache e arquivos antigos limpos! {cleared_files} arquivos removidos.")
        
    except Exception as e:
        st.error(f"❌ Erro ao limpar cache: {e}")

def show_recent_logs():
    """Mostra logs recentes"""
    try:
        logs_dir = Path("logs")
        if logs_dir.exists():
            log_files = list(logs_dir.glob("*.log"))
            if log_files:
                # Pegar o arquivo de log mais recente
                latest_log = max(log_files, key=os.path.getctime)
                
                with open(latest_log, 'r', encoding='utf-8') as f:
                    lines = f.readlines()
                    # Mostrar últimas 20 linhas
                    recent_lines = lines[-20:] if len(lines) > 20 else lines
                    
                st.code(''.join(recent_lines), language='log')
            else:
                st.info("📄 Nenhum arquivo de log encontrado")
        else:
            st.info("📁 Diretório de logs não existe")
            
    except Exception as e:
        st.error(f"❌ Erro ao ler logs: {e}")

def show_system_info():
    """Mostra informações do sistema"""
    import platform
    import sys
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("**Sistema:**")
        st.text(f"OS: {platform.system()} {platform.release()}")
        st.text(f"Python: {sys.version.split()[0]}")
        st.text(f"Streamlit: {st.__version__}")
    
    with col2:
        st.markdown("**Recursos:**")
        try:
            import psutil
            st.text(f"CPU: {psutil.cpu_count()} cores")
            st.text(f"RAM: {psutil.virtual_memory().total / (1024**3):.1f} GB")
            st.text(f"Disco: {psutil.disk_usage('/').free / (1024**3):.1f} GB livres")
        except ImportError:
            st.text("psutil não disponível")
    
    # Verificar dependências
    st.markdown("**Dependências:**")
    dependencies = {
        "PyPDF2": "PyPDF2",
        "pdfplumber": "pdfplumber", 
        "PyMuPDF": "fitz",
        "pikepdf": "pikepdf"
    }
    
    for name, module in dependencies.items():
        try:
            __import__(module)
            st.text(f"✅ {name}")
        except ImportError:
            st.text(f"❌ {name}")
    
    # Verificar ferramentas externas
    st.markdown("**Ferramentas Externas:**")
    external_tools = {
        "Ghostscript": "gswin64c" if os.name == 'nt' else "gs",
        "OCRmyPDF": "ocrmypdf",
        "Tesseract": "tesseract"
    }
    
    for name, command in external_tools.items():
        try:
            import subprocess
            result = subprocess.run([command, "--version"], 
                                  capture_output=True, text=True)
            st.text(f"✅ {name}")
        except:
            st.text(f"❌ {name}")