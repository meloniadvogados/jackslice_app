# 📚 Documentação Completa - Jack PDF Slicer

## 🎯 Visão Geral

O **Jack PDF Slicer** é uma ferramenta web completa para processamento de PDFs, especialmente otimizada para documentos legais. Desenvolvido em **Streamlit**, oferece uma interface moderna e intuitiva para todas as operações com PDFs.

---

## 🚀 Funcionalidades Principais

### 1. 🔪 **Fatiar PDF**
Extrai automaticamente documentos individuais de PDFs grandes baseado em índices/sumários.

**Como funciona:**
- Detecta automaticamente sumários (SUMÁRIO)
- Extrai dados estruturados: ID, Data, Documento, Tipo
- Valida formatos de data (dd/mm/yyyy, yyyy-mm-dd)
- Gera PDFs individuais para cada seção

**Uso típico:**
- Processos legais com múltiplos documentos
- Autos processuais digitalizados
- Documentos com índice estruturado

### 2. 🪄 **Converter PDF**
Converte PDFs para múltiplos formatos com OCR automático.

**Formatos suportados:**

#### 📄 **Documentos:**
- **Word (.docx)**: Layout idêntico ao PDF + texto editável
- **Excel (.xlsx)**: Tabelas e dados estruturados
- **PowerPoint (.pptx)**: Cada página como slide *(em desenvolvimento)*
- **Texto (.txt)**: Texto puro extraído

#### 🖼️ **Imagens:**
- **PNG**: Melhor qualidade, suporte a transparência
- **JPEG**: Menor tamanho, ideal para fotos
- **TIFF**: Qualidade profissional

#### 🌐 **Web & Outros:**
- **HTML**: Páginas web navegáveis *(em desenvolvimento)*
- **ePub**: E-books compatíveis *(em desenvolvimento)*
- **XML**: Dados estruturados *(em desenvolvimento)*

**Recursos especiais:**
- **OCR automático**: Detecta PDFs digitalizados e aplica OCR automaticamente
- **Múltiplas qualidades**: Configurações de DPI e qualidade
- **Seleção de páginas**: Específicas ou intervalos
- **Detecção inteligente**: Identifica se PDF tem texto pesquisável

### 3. ✂️ **Dividir PDF**
Divide PDFs de várias formas com interface "for dummies".

**Modos de divisão:**

#### 📄 **Por Páginas:**
- **A cada X páginas**: Divide em partes fixas (ex: 10 páginas cada)
- **Em partes iguais**: Divide em N partes de tamanho similar
- **Intervalos customizados**: Define páginas específicas para cada arquivo

#### ✂️ **Extrair/Remover:**
- **Extrair específicas**: Cria PDF apenas com páginas selecionadas
- **Remover específicas**: Cria PDF removendo páginas indesejadas
- **Formato flexível**: Use vírgulas (1,3,5) e hífens (5-10)

#### 📦 **Por Tamanho:**
- **Limite de tamanho**: Divide quando atingir tamanho máximo
- **Ideal para email**: Respeita limites de anexo
- **Estimativa inteligente**: Calcula número provável de arquivos

### 4. 🔗 **Unir PDFs**
Combina múltiplos PDFs em um único arquivo com drag & drop.

**Recursos:**
- **Interface drag & drop**: Reordene arquivos visualmente
- **Visualização**: Thumbnails da primeira página
- **Opções avançadas**: Bookmarks, separadores, metadata
- **Controle total**: Adicione, remova e reordene facilmente

### 5. 🧠 **Aplicar OCR**
Aplica reconhecimento óptico de caracteres em PDFs digitalizados.

**Configurações:**
- **Múltiplos idiomas**: Português, Inglês, Espanhol, Francês, Alemão, Italiano
- **Forçar OCR**: Aplica OCR mesmo em páginas que já têm texto
- **Otimizar saída**: Reduz tamanho do arquivo final
- **Corrigir inclinação**: Corrige automaticamente páginas tortas
- **Threads**: Processamento paralelo para velocidade
- **Qualidade JPEG**: Controla qualidade das imagens

### 6. ⚡ **Otimizar PDF**
Comprime PDFs para reduzir tamanho mantendo qualidade.

**Modos de compressão:**
- **Leve (Ebook)**: Mantém boa qualidade, compressão moderada
- **Turbo (Screen)**: Máxima compressão, qualidade reduzida

**Técnicas utilizadas:**
- Recompressão de imagens
- Otimização de fontes
- Remoção de metadados desnecessários
- Simplificação de elementos gráficos

---

## 🛠️ Tecnologias Utilizadas

### **Backend:**
- **Streamlit**: Framework web para interface
- **PyPDF2**: Manipulação básica de PDFs
- **pdfplumber**: Extração de texto e tabelas
- **PyMuPDF (fitz)**: Processamento avançado de PDFs
- **pikepdf**: Reparação e otimização de PDFs

### **Conversão:**
- **pdf2docx**: Conversão para Word mantendo layout
- **python-docx**: Criação de documentos Word
- **openpyxl**: Criação de planilhas Excel
- **Pillow**: Processamento de imagens

### **OCR:**
- **OCRmyPDF**: Motor principal de OCR
- **Tesseract**: Engine de reconhecimento de texto

### **Otimização:**
- **Ghostscript**: Compressão e otimização de PDFs

---

## 📋 Requisitos do Sistema

### **Dependências Python:**
```bash
pip install -r requirements.txt
```

### **Ferramentas Externas:**

#### **OCR (Opcional):**
- **Tesseract OCR**
  - Windows: [Download oficial](https://github.com/UB-Mannheim/tesseract/wiki)
  - Linux: `sudo apt-get install tesseract-ocr tesseract-ocr-por`
  - macOS: `brew install tesseract tesseract-lang`

#### **Otimização (Opcional):**
- **Ghostscript**
  - Windows: [Download oficial](https://www.ghostscript.com/download/gsdnld.html)
  - Linux: `sudo apt-get install ghostscript`
  - macOS: `brew install ghostscript`

---

## 🚀 Instalação e Execução

### **1. Instalação:**
```bash
# Clonar repositório
git clone <repositório>
cd pdf_slicer

# Instalar dependências
pip install -r requirements.txt
```

### **2. Execução:**
```bash
# Modo local
streamlit run app.py

# Modo rede (LAN)
python run_network.py

# Com launcher automático
python run_streamlit.py
```

### **3. Acesso:**
- **Local**: http://localhost:8501
- **Rede**: http://IP_DA_MÁQUINA:8501

---

## 💡 Guia de Uso

### **Upload de Arquivos:**
1. Selecione o módulo desejado no menu lateral
2. Faça upload do arquivo PDF
3. Configure as opções disponíveis
4. Execute o processamento
5. Baixe os resultados

### **Configurações Recomendadas:**

#### **Para Documentos Legais:**
- **Fatiar PDF**: Use para processos com sumário
- **OCR**: Aplique em documentos digitalizados
- **Converter para Word**: Para editar petições e contratos

#### **Para Documentos Grandes:**
- **Dividir PDF**: Use "Por Tamanho" para email
- **Otimizar PDF**: Use modo "Leve" para manter qualidade

#### **Para Digitalização:**
- **OCR**: Configure idioma português
- **Qualidade**: Use configurações altas para documentos importantes

---

## 🔧 Configurações Avançadas

### **Limites de Upload:**
- **Tamanho máximo**: 200MB (configurável)
- **Formatos aceitos**: PDF apenas
- **Páginas**: Sem limite técnico

### **Performance:**
- **Threads OCR**: 2-8 threads (padrão: 4)
- **Qualidade JPEG**: 50-100% (padrão: 85%)
- **Cache**: Otimizado para sessões múltiplas

### **Armazenamento:**
- **Temporário**: Processamento em memória
- **Logs**: Diretório `logs/`
- **Dados**: Diretório `data/` (para fatiamento)
- **Saída**: Diretório `output_pdf/` (para fatiamento)

---

## 🐛 Solução de Problemas

### **Problemas Comuns:**

#### **"OCRmyPDF não encontrado"**
```bash
# Instalar OCRmyPDF
pip install ocrmypdf

# Instalar Tesseract
# Windows: Baixar instalador oficial
# Linux: sudo apt-get install tesseract-ocr
# macOS: brew install tesseract
```

#### **"Ghostscript não encontrado"**
```bash
# Instalar Ghostscript
# Windows: Baixar instalador oficial
# Linux: sudo apt-get install ghostscript
# macOS: brew install ghostscript
```

#### **"Arquivo baixa como PDF ao invés de Word/Excel"**
- Renomeie o arquivo baixado para `.docx` ou `.xlsx`
- Problema conhecido em alguns browsers

#### **"Erro de memória com PDFs grandes"**
- Divida o PDF em partes menores primeiro
- Use otimização antes de outros processamentos

### **Logs e Debug:**
- Logs armazenados em `logs/`
- Erros mostrados na interface
- Informações detalhadas nos expanders

---

## 📊 Arquitetura do Sistema

### **Fluxo Principal:**
```
Upload → Validação → Processamento → Resultado → Download
```

### **Módulos:**
```
app.py (Principal)
├── modules/
│   ├── pdf_slicer_new.py (Fatiamento)
│   ├── pdf_converter.py (Conversão)
│   ├── pdf_splitter.py (Divisão)
│   ├── pdf_merger_final.py (União)
│   ├── ocr.py (OCR)
│   ├── pdf_optimizer.py (Otimização)
│   └── settings.py (Configurações)
├── core/
│   ├── XPTO.py (Pipeline de fatiamento)
│   └── ui_components.py (Componentes UI)
└── static/
    └── styles.css (Estilos)
```

### **Processamento:**
- **Stateless**: Cada sessão independente
- **In-memory**: Processamento em memória
- **Temporary files**: Apenas quando necessário
- **Parallel**: OCR e processamento paralelo

---

## 🔒 Segurança

### **Dados:**
- **Não persistente**: Arquivos não ficam no servidor
- **Sessão isolada**: Cada usuário tem dados isolados
- **Limpeza automática**: Arquivos temporários removidos
- **Sem logging**: Conteúdo dos PDFs não é logado

### **Uploads:**
- **Validação**: Apenas PDFs aceitos
- **Limite de tamanho**: 200MB máximo
- **Timeout**: Processamento limitado por tempo

---

## 📈 Performance

### **Otimizações:**
- **Cache inteligente**: Resultados em cache com TTL
- **Lazy loading**: Componentes carregados sob demanda
- **Parallel processing**: OCR e conversão paralela
- **Memory management**: Limpeza automática de memória

### **Métricas:**
- **Upload**: Instantâneo até 200MB
- **OCR**: ~1-3 páginas/minuto
- **Conversão**: ~10-50 páginas/minuto
- **Otimização**: ~20-100 páginas/minuto

---

## 🔄 Atualizações

### **Versão Atual:**
- **Web-first**: Migrado de desktop para web
- **OCR automático**: Integração transparente
- **Interface moderna**: Streamlit com componentes customizados
- **Multi-formato**: Suporte a múltiplos formatos de saída

### **Próximas Funcionalidades:**
- **PowerPoint**: Conversão completa para PPTX
- **HTML**: Páginas web navegáveis
- **ePub**: E-books completos
- **XML**: Dados estruturados
- **API**: Interface programática

---

## 📞 Suporte

### **Documentação:**
- **Expanders informativos**: Em cada módulo
- **Tooltips**: Ajuda contextual
- **Exemplos**: Casos de uso práticos

### **Troubleshooting:**
- **Mensagens claras**: Erros explicados
- **Soluções**: Passos para resolver
- **Logs detalhados**: Para debug avançado

---

## 📄 Licença

Este projeto é desenvolvido para uso interno e processamento de documentos legais. Todas as dependências externas mantêm suas respectivas licenças.

---

## 🔗 Links Úteis

- **Tesseract OCR**: https://github.com/tesseract-ocr/tesseract
- **Ghostscript**: https://www.ghostscript.com/
- **Streamlit**: https://streamlit.io/
- **PyMuPDF**: https://pymupdf.readthedocs.io/
- **OCRmyPDF**: https://ocrmypdf.readthedocs.io/

---

*Documentação atualizada em: 2024-07-15*
*Versão do sistema: Web 2.0*