# core/settings_manager.py

import json
import os
from pathlib import Path
import tempfile

class SettingsManager:
    """
    Classe responsável por gerenciar as configurações globais do sistema PDF Slicer.
    
    As configurações são armazenadas em um arquivo JSON.
    """

    def __init__(self, settings_file: str = None):
        """
        Inicializa o SettingsManager.

        Args:
            settings_file (str): Caminho para o arquivo JSON de configurações.
        """
        if settings_file is None:
            # Usar diretório temporário para configurações de usuário
            settings_dir = os.path.join(tempfile.gettempdir(), "pdf_slicer_settings")
            os.makedirs(settings_dir, exist_ok=True)
            settings_file = os.path.join(settings_dir, "settings.json")
            
        self.settings_path = Path(settings_file)
        
        # Configurações padrão relevantes para aplicação web
        self.settings = {
            # Processamento
            "max_threads": 4,
            "chunk_size": 1024,
            "compress_output": True,
            
            # Cache
            "enable_cache": True,
            "cache_size": 100,  # MB
            "cache_ttl": 3600,  # segundos
            
            # Arquivos temporários
            "temp_file_retention": 3600,  # segundos
            "max_upload_size": 100,  # MB
            "session_timeout": 1800,  # segundos
            
            # Logging
            "log_level": "INFO",
            "log_to_file": True,
            "debug_mode": False,
            
            # UI
            "show_advanced_options": False,
            "default_language": "pt-BR"
        }
        self.load_settings()

    def load_settings(self):
        """
        Carrega as configurações do arquivo JSON, se existir.
        """
        if self.settings_path.exists():
            try:
                with open(self.settings_path, "r", encoding="utf-8") as file:
                    saved_settings = json.load(file)
                    # Atualizar apenas configurações existentes
                    for key in self.settings:
                        if key in saved_settings:
                            self.settings[key] = saved_settings[key]
            except (json.JSONDecodeError, IOError) as e:
                print(f"[WARNING] Erro ao carregar configurações: {e}. Usando padrões.")

    def save_settings(self):
        """
        Salva as configurações atuais no arquivo JSON.
        """
        try:
            self.settings_path.parent.mkdir(parents=True, exist_ok=True)
            with open(self.settings_path, "w", encoding="utf-8") as file:
                json.dump(self.settings, file, indent=4, ensure_ascii=False)
        except IOError as e:
            print(f"[ERROR] Erro ao salvar configurações: {e}")

    def set(self, key: str, value):
        """
        Define uma configuração genérica.

        Args:
            key (str): Nome da configuração
            value: Valor da configuração
        """
        self.settings[key] = value
        self.save_settings()

    def get(self, key: str, default=None):
        """
        Obtém uma configuração.

        Args:
            key (str): Nome da configuração
            default: Valor padrão se a configuração não existir

        Returns:
            Valor da configuração ou default
        """
        return self.settings.get(key, default)

    def get_all(self) -> dict:
        """
        Retorna todas as configurações atuais.

        Returns:
            dict: Dicionário com as configurações.
        """
        return self.settings.copy()

    def reset_to_defaults(self):
        """
        Restaura todas as configurações para os valores padrão.
        """
        self.settings = {
            "max_threads": 4,
            "chunk_size": 1024,
            "compress_output": True,
            "enable_cache": True,
            "cache_size": 100,
            "cache_ttl": 3600,
            "temp_file_retention": 3600,
            "max_upload_size": 100,
            "session_timeout": 1800,
            "log_level": "INFO",
            "log_to_file": True,
            "debug_mode": False,
            "show_advanced_options": False,
            "default_language": "pt-BR"
        }
        self.save_settings()

    def get_temp_dir(self) -> str:
        """
        Retorna o diretório temporário para a aplicação.
        
        Returns:
            str: Caminho do diretório temporário
        """
        temp_dir = os.path.join(tempfile.gettempdir(), "pdf_slicer_temp")
        os.makedirs(temp_dir, exist_ok=True)
        return temp_dir
