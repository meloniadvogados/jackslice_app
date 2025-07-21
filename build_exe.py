#!/usr/bin/env python3
"""
🚀 BUSCA_ML - Gerador de Executável
Gera o executável completo do sistema mantendo arquivos externos (.env, CSV, etc)
"""

import os
import sys
import subprocess
import shutil
from pathlib import Path

def main():
    print("🚀 BUSCA_ML - Gerador de Executável")
    print("=" * 50)

    # Verificar se PyInstaller está instalado
    try:
        subprocess.run(["pyinstaller", "--version"], check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        print("✅ PyInstaller encontrado")
    except (subprocess.CalledProcessError, FileNotFoundError):
        print("❌ PyInstaller não encontrado. Instalando...")
        subprocess.check_call([sys.executable, "-m", "pip", "install", "pyinstaller"])
        print("✅ PyInstaller instalado")

    # Diretório atual
    projeto_dir = Path.cwd()
    dist_dir = projeto_dir / "dist"
    build_dir = projeto_dir / "build"

    print(f"📁 Diretório do projeto: {projeto_dir}")

    # Limpar builds anteriores
    if dist_dir.exists():
        print("🗑️ Removendo builds anteriores...")
        shutil.rmtree(dist_dir)
    if build_dir.exists():
        shutil.rmtree(build_dir)

    # Comando PyInstaller
    cmd = [
        "pyinstaller",
        "--onefile",
        "--windowed",
        "--name=Jack",
        "--hidden-import=selenium",
        "--hidden-import=webdriver_manager", 
        "--hidden-import=requests",
        "--hidden-import=dotenv",
        "--hidden-import=PIL",
        "--hidden-import=tkinter",
        "--collect-all=selenium",
        "--collect-all=webdriver_manager",
        "main.py"
    ]

    # Adicionar ícone apenas se existir
    if os.path.exists('icon.ico'):
        cmd.insert(-1, "--icon=icon.ico")
        print("✅ Ícone encontrado e será incluído")
    else:
        print("⚠️ Arquivo icon.ico não encontrado - executável será criado sem ícone")

    print("🔨 Gerando executável...")
    print(f"🛠️ Comando: {' '.join(cmd)}")

    try:
        # Executar PyInstaller
        result = subprocess.run(cmd, capture_output=True, text=True)

        if result.returncode == 0:
            print("✅ Executável gerado com sucesso!")

            # Copiar arquivos necessários para a pasta dist
            exe_dir = dist_dir

            print("📋 Copiando arquivos de configuração...")

            arquivos_copiar = [
                ".env",
                "dados_catalogo.csv", 
                "tokens.json"
            ]

            for arquivo in arquivos_copiar:
                if os.path.exists(arquivo):
                    shutil.copy2(arquivo, exe_dir / arquivo)
                    print(f"✅ {arquivo} copiado")
                else:
                    print(f"⚠️ {arquivo} não encontrado (será criado automaticamente)")

            chrome_profile_dist = exe_dir / "chrome-profile"
            if not chrome_profile_dist.exists():
                chrome_profile_dist.mkdir()
                print("✅ Pasta chrome-profile criada")

            print("\n🎉 BUILD CONCLUÍDO!")
            print(f"📁 Executável criado em: {exe_dir / 'BUSCA_ML.exe'}")
            print("\n📋 Estrutura final:")
            print("   📁 dist/")
            print("   ├── 🚀 BUSCA_ML.exe")
            print("   ├── ⚙️ .env")
            print("   ├── 📊 dados_catalogo.csv")
            print("   ├── 🔑 tokens.json")
            print("   └── 📁 chrome-profile/")
            print("\n✅ O executável lerá os arquivos .env e CSV da mesma pasta!")
        else:
            print("❌ Erro ao gerar executável:")
            print(result.stderr)

    except Exception as e:
        print(f"❌ Erro inesperado: {e}")

if __name__ == "__main__":
    main()
