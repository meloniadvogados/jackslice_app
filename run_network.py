#!/usr/bin/env python3
"""
🌐 Jack PDF Slicer - Network Server Launcher
Configura e executa o PDF Slicer para acesso via rede local
"""

import subprocess
import sys
import os
import socket
from pathlib import Path

def get_local_ip():
    """Obtém IP local da máquina"""
    try:
        # Conecta a um endereço externo para descobrir IP local
        with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as s:
            s.connect(("8.8.8.8", 80))
            return s.getsockname()[0]
    except Exception:
        return "127.0.0.1"

def check_ip_availability(ip_address):
    """Verifica se o IP está disponível na máquina"""
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.bind((ip_address, 0))
            return True
    except OSError:
        return False

def create_network_config(ip_address, port=8501):
    """Cria configuração de rede para Streamlit"""
    config_dir = Path(".streamlit")
    config_dir.mkdir(exist_ok=True)
    
    config_content = f'''[theme]
primaryColor = "#FF6B6B"
backgroundColor = "#FFFFFF"
secondaryBackgroundColor = "#F0F2F6"
textColor = "#262730"

[server]
port = {port}
address = "{ip_address}"
maxUploadSize = 200
enableCORS = false
enableXsrfProtection = false
headless = true

[browser]
gatherUsageStats = false
serverAddress = "{ip_address}"
serverPort = {port}

[global]
developmentMode = false
'''
    
    config_path = config_dir / "config.toml"
    with open(config_path, 'w') as f:
        f.write(config_content)
    
    return config_path

def main():
    """Função principal"""
    print("🌐 JACK PDF SLICER - SERVIDOR DE REDE")
    print("=" * 60)
    
    # IP desejado
    target_ip = "10.10.3.1"
    port = 8501
    
    # Verificar diretório
    if not Path("app.py").exists():
        print("❌ Erro: Execute no diretório do projeto")
        return 1
    
    # Verificar IP local
    local_ip = get_local_ip()
    print(f"🔍 IP local detectado: {local_ip}")
    
    # Verificar se o IP target está disponível
    print(f"🔍 Verificando disponibilidade do IP {target_ip}...")
    
    if not check_ip_availability(target_ip):
        print(f"⚠️ IP {target_ip} não está disponível nesta máquina")
        print(f"💡 Usando IP local: {local_ip}")
        target_ip = local_ip
    else:
        print(f"✅ IP {target_ip} disponível")
    
    # Verificar porta
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.bind((target_ip, port))
            print(f"✅ Porta {port} disponível")
    except OSError:
        print(f"❌ Porta {port} já está em uso")
        # Tentar encontrar porta disponível
        for test_port in range(8501, 8510):
            try:
                with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                    s.bind((target_ip, test_port))
                    port = test_port
                    print(f"💡 Usando porta alternativa: {port}")
                    break
            except OSError:
                continue
        else:
            print("❌ Nenhuma porta disponível encontrada")
            return 1
    
    # Criar configuração de rede
    print(f"\n⚙️ Criando configuração para {target_ip}:{port}...")
    config_path = create_network_config(target_ip, port)
    print(f"✅ Configuração criada: {config_path}")
    
    # Verificar dependências básicas
    print("\n📦 Verificando Streamlit...")
    try:
        import streamlit
        print(f"✅ Streamlit {streamlit.__version__}")
    except ImportError:
        print("❌ Streamlit não encontrado")
        print("📥 Instalando...")
        try:
            subprocess.check_call([sys.executable, "-m", "pip", "install", "streamlit>=1.28.0"])
            print("✅ Streamlit instalado")
        except subprocess.CalledProcessError:
            print("❌ Falha na instalação")
            return 1
    
    # Informações de rede
    print("\n🌐 INFORMAÇÕES DE ACESSO:")
    print("=" * 40)
    print(f"🔗 URL Principal: http://{target_ip}:{port}")
    print(f"🏠 URL Local: http://localhost:{port}")
    if target_ip != local_ip:
        print(f"💻 URL IP Local: http://{local_ip}:{port}")
    print("=" * 40)
    
    # Instruções de firewall
    print("\n🔒 CONFIGURAÇÃO DE REDE:")
    print("Para acesso externo, configure:")
    print(f"• Firewall: Liberar porta {port}")
    print(f"• Router: Port forward {port} → este computador")
    print("• Antivírus: Permitir conexões na porta")
    
    # Executar servidor
    print(f"\n🚀 Iniciando servidor em {target_ip}:{port}...")
    print("⏹️ Para parar: Ctrl+C")
    print("=" * 60)
    
    try:
        # Comando Streamlit otimizado para rede
        cmd = [
            sys.executable, "-m", "streamlit", "run", "app.py",
            "--server.port", str(port),
            "--server.address", target_ip,
            "--browser.gatherUsageStats", "false",
            "--server.enableCORS", "false",
            "--server.enableXsrfProtection", "false",
            "--server.headless", "true"
        ]
        
        # Executar
        subprocess.run(cmd)
        
    except KeyboardInterrupt:
        print("\n\n👋 Servidor encerrado")
        return 0
    except Exception as e:
        print(f"\n❌ Erro ao executar servidor: {e}")
        return 1

if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)