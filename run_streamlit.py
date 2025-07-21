#!/usr/bin/env python3
"""
🚀 Launcher para Jack PDF Slicer - Versão Streamlit
Executa a aplicação web do PDF Slicer
"""

import subprocess
import sys
import os
from pathlib import Path

def main():
    print("🚀 Jack PDF Slicer - Versão Web")
    print("=" * 50)
    
    # Verificar se estamos no diretório correto
    if not Path("app.py").exists():
        print("❌ Erro: app.py não encontrado")
        print("Execute este script no diretório do projeto")
        return 1
    
    # Verificar se Streamlit está instalado
    try:
        import streamlit
        print(f"✅ Streamlit {streamlit.__version__} encontrado")
    except ImportError:
        print("❌ Streamlit não encontrado")
        print("Instalando Streamlit...")
        try:
            subprocess.check_call([sys.executable, "-m", "pip", "install", "streamlit>=1.28.0"])
            print("✅ Streamlit instalado com sucesso")
        except subprocess.CalledProcessError:
            print("❌ Erro ao instalar Streamlit")
            return 1
    
    # Verificar outras dependências essenciais
    print("\n🔍 Verificando dependências...")
    dependencies = {
        "PyPDF2": "PyPDF2",
        "pdfplumber": "pdfplumber",
        "PyMuPDF": "fitz",
        "pikepdf": "pikepdf",
        "Pillow": "PIL"
    }
    
    missing_deps = []
    for name, module in dependencies.items():
        try:
            __import__(module)
            print(f"✅ {name}")
        except ImportError:
            print(f"❌ {name}")
            missing_deps.append(name.lower())
    
    # Instalar dependências em falta
    if missing_deps:
        print(f"\n📦 Instalando dependências em falta: {', '.join(missing_deps)}")
        try:
            subprocess.check_call([
                sys.executable, "-m", "pip", "install"
            ] + missing_deps)
            print("✅ Dependências instaladas com sucesso")
        except subprocess.CalledProcessError:
            print("❌ Erro ao instalar dependências")
            print("Tente instalar manualmente com: pip install -r requirements.txt")
            return 1
    
    # Criar diretórios necessários
    print("\n📁 Criando diretórios necessários...")
    directories = ["output_pdf", "data", "logs", ".streamlit"]
    for dir_name in directories:
        os.makedirs(dir_name, exist_ok=True)
        print(f"✅ {dir_name}/")
    
    # Criar configuração do Streamlit se não existir
    streamlit_config_path = Path(".streamlit/config.toml")
    if not streamlit_config_path.exists():
        print("⚙️ Criando configuração do Streamlit...")
        config_content = '''[theme]
primaryColor = "#FF6B6B"
backgroundColor = "#FFFFFF"
secondaryBackgroundColor = "#F0F2F6"
textColor = "#262730"

[server]
port = 8501
maxUploadSize = 200

[browser]
gatherUsageStats = false
'''
        with open(streamlit_config_path, 'w') as f:
            f.write(config_content)
        print("✅ Configuração criada")
    
    # Executar Streamlit
    print("\n🌐 Iniciando aplicação web...")
    print("📱 A aplicação estará disponível na rede")
    print("🔗 URL local: http://localhost:8501")
    print("🌐 URL rede: http://10.10.3.1:8501")
    print("⏹️ Para parar: Ctrl+C")
    print("=" * 50)
    
    try:
        # Comando para executar Streamlit
        cmd = [sys.executable, "-m", "streamlit", "run", "app.py"]
        
        # Adicionar opções do Streamlit para acesso externo
        cmd.extend([
            "--server.port", "8501",
            "--server.address", "10.10.3.1",
            "--browser.gatherUsageStats", "false",
            "--server.enableCORS", "false",
            "--server.enableXsrfProtection", "false"
        ])
        
        # Executar
        subprocess.run(cmd)
        
    except KeyboardInterrupt:
        print("\n\n👋 Aplicação encerrada pelo usuário")
        return 0
    except Exception as e:
        print(f"\n❌ Erro ao executar aplicação: {e}")
        return 1

if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)