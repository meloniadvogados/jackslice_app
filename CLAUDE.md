# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

Jack PDF Slicer is a web-based application for processing PDF documents, particularly legal documents. Originally a desktop application, it has been migrated to Streamlit for better accessibility and modern UI. It provides features for:
- PDF slicing/splitting based on document indexes
- PDF optimization
- OCR (Optical Character Recognition) application
- PDF merging with drag & drop and thumbnails
- PDF conversion to multiple formats (Word, Excel, Images, Text)
- PDF splitting with multiple modes
- Automatic extraction of legal process numbers

## Key Commands

### Development (Streamlit Web App)
```bash
# Install dependencies
pip install -r requirements.txt

# Run the web application
streamlit run app.py
# OR use the launcher script (auto-installs missing dependencies)
python run_streamlit.py

# Run with network access (LAN deployment)
python run_network.py
# Access at: http://10.10.3.1:8501

# Test installation and configuration
python test_migration.py

# Access the application
# Browser: http://localhost:8501
```

### Legacy Commands (Desktop)
```bash
# Run legacy desktop GUI (if customtkinter is installed)
python main.py

# Run CLI mode for processing a single PDF
python main.py path/to/file.pdf

# Build Windows executable (legacy)
python build_exe.py
pyinstaller Jack.spec
```

## Architecture Overview

### Core Processing Pipeline

The application follows a sequential processing pipeline orchestrated by `XPTO.py`:

1. **Index Extraction** (`PDFIndexExtractor`)
   - Scans PDF for summary table (SUMÁRIO) starting from last page
   - Extracts structured data: ID, Date, Document, Type
   - Validates date formats (dd/mm/yyyy, yyyy-mm-dd)
   - Saves extracted index as JSON in `data/` directory

2. **Page Block Extraction** (`PDFPageBlockExtractor`)
   - Extracts text blocks from all PDF pages
   - Provides progress callback for GUI updates
   - Saves page blocks as JSON for range matching

3. **Range Matching** (`PageRangeExtractor`)
   - Correlates index entries with actual page locations
   - Determines start/end pages for each document section
   - Saves final mapping with page ranges

4. **PDF Splitting** (`PDFExtractRunner`)
   - Creates individual PDFs for selected sections
   - Uses PyMuPDF for high-performance processing
   - Applies filename sanitization for safe file operations

### Web Interface Architecture (Streamlit)

The application uses Streamlit for modern web-based UI:

- **Main App** (`app.py`): Central web application with navigation sidebar
- **PDF Slicer** (`modules/pdf_slicer_new.py`): Core slicing interface with file upload/download
- **PDF Converter** (`modules/pdf_converter.py`): Multi-format conversion with automatic OCR
- **PDF Splitter** (`modules/pdf_splitter.py`): PDF splitting with multiple modes
- **PDF Optimizer** (`modules/pdf_optimizer.py`): PDF compression and optimization
- **OCR** (`modules/ocr.py`): OCR application for scanned documents
- **PDF Merger** (`modules/pdf_merger_final.py`): PDF merging with drag & drop and thumbnails
- **Settings** (`modules/settings.py`): Configuration management with persistence

### Legacy GUI Architecture (Desktop)

Original CustomTkinter desktop interface (preserved for backward compatibility):

- **Main Hub** (`main.py`): Desktop launcher with module selection
- **GUI Components** (`UI/`): Original desktop interface modules

### Data Management

- **Settings** (`SettingsManager`): Centralized configuration in `data/settings.json`
- **Output Structure**: Processed PDFs saved in `output_pdf/` directory
- **Intermediate Data**: JSON files in `data/` for pipeline state
- **Logging**: Application logs stored in `logs/` directory

## Key Dependencies

### Web Application (Primary)
- **streamlit**: Modern web framework for data applications
- **PyPDF2**: PDF manipulation
- **pdfplumber**: PDF text extraction and table parsing
- **PyMuPDF (fitz)**: High-performance PDF processing
- **pikepdf**: PDF repair and optimization
- **OCRmyPDF**: OCR functionality
- **Pillow**: Image processing
- **psutil**: System utilities

### Conversion Dependencies
- **pdf2docx**: PDF to Word conversion maintaining layout
- **python-docx**: Word document creation
- **openpyxl**: Excel spreadsheet creation
- **pypandoc**: Document format conversion
- **ebooklib**: E-book format support
- **lxml**: XML processing
- **beautifulsoup4**: HTML parsing

### Legacy Desktop (Optional)
- **customtkinter**: Modern desktop GUI framework
- **PyInstaller**: Executable packaging

## Main Modules

### 1. PDF Converter (`modules/pdf_converter.py`)
**Purpose**: Convert PDFs to multiple formats with automatic OCR

**Features**:
- **Document Formats**: Word (.docx), Excel (.xlsx), Text (.txt), PowerPoint (.pptx)
- **Image Formats**: PNG, JPEG, TIFF with quality settings
- **Web Formats**: HTML, ePub, XML (in development)
- **Automatic OCR**: Detects digitized PDFs and applies OCR automatically
- **Layout preservation**: Word conversion maintains exact PDF layout
- **Quality options**: DPI settings, compression levels
- **Page selection**: Specific pages or ranges

**Key Functions**:
- `pdf_converter_page()`: Main interface
- `convert_to_word()`: Word conversion with automatic OCR
- `convert_to_excel()`: Excel conversion with table detection
- `convert_to_text()`: Text extraction with layout options
- `convert_to_image_format()`: Image conversion with quality control
- `apply_ocr_to_pdf()`: Automatic OCR application

### 2. PDF Splitter (`modules/pdf_splitter.py`)
**Purpose**: Split PDFs in multiple ways with user-friendly interface

**Features**:
- **By Pages**: Fixed intervals, equal parts, custom ranges
- **Extract/Remove**: Specific pages selection
- **By Size**: Maximum file size limits
- **For dummies interface**: Examples and clear explanations
- **Smart validation**: Page range and format validation
- **ZIP downloads**: Multiple files in compressed format

**Key Functions**:
- `pdf_splitter_page()`: Main interface with tabs
- `split_by_pages()`: Page-based splitting
- `extract_remove_pages()`: Page extraction/removal
- `split_by_size()`: Size-based splitting

### 3. PDF Merger (`modules/pdf_merger_final.py`)
**Purpose**: Merge multiple PDFs with drag & drop interface

**Features**:
- **Drag & Drop**: Visual file reordering
- **Thumbnails**: First page preview
- **Advanced options**: Bookmarks, separators, metadata
- **Real-time updates**: Dynamic file list management
- **Reset functionality**: "Começar Novamente" button

### 4. OCR (`modules/ocr.py`)
**Purpose**: Apply Optical Character Recognition to scanned PDFs

**Features**:
- **Multiple languages**: Portuguese, English, Spanish, French, German, Italian
- **Advanced settings**: Force OCR, deskew, optimization
- **Quality control**: JPEG quality, thread count
- **Progress tracking**: Real-time processing updates

### 5. PDF Optimizer (`modules/pdf_optimizer.py`)
**Purpose**: Compress PDFs while maintaining quality

**Features**:
- **Compression modes**: Light (ebook), Turbo (screen)
- **Ghostscript integration**: Professional PDF optimization
- **Size comparison**: Before/after file sizes
- **Quality preservation**: Configurable compression levels

## User Interface Features

### Navigation
- **Sidebar menu**: Fixed navigation with module icons
- **Responsive design**: Works on desktop and mobile
- **Session state**: Maintains user workflow across interactions
- **Progress indicators**: Real-time processing feedback

### File Handling
- **Web-optimized**: In-memory processing
- **200MB upload limit**: Configurable in Streamlit settings
- **Direct download**: Browser-native file downloads
- **Temporary cleanup**: Automatic file cleanup

### User Experience
- **"For dummies" interface**: Clear examples and explanations
- **Information expanders**: Detailed help for each module
- **Error handling**: User-friendly error messages
- **Progress bars**: Visual feedback for long operations

## Recent Updates & Optimizations

### Code Cleanup (2024-07-08)
- **Removed 13 unnecessary MD documentation files** (development artifacts)
- **Cleaned up 8 unused imports** across multiple files
- **Removed temporary JSON files** from `/data/` directory
- **Eliminated Python cache files** (`__pycache__/`)
- **Fixed code formatting** and indentation issues
- **Consolidated duplicate imports** in app.py

### Major Features Added (2024-07-15)
- **PDF Converter Module** (`modules/pdf_converter.py`) - Complete multi-format conversion
- **Automatic OCR Integration** - Seamless OCR application during conversion
- **PDF Splitter Module** (`modules/pdf_splitter.py`) - Multiple splitting modes
- **Enhanced PDF Merger** - Drag & drop interface with thumbnails
- **Comprehensive Documentation** - Complete system documentation with web interface
- **Unified Information System** - Consistent help expanders across all modules

### Performance Improvements
- **Automatic OCR**: No manual steps required - OCR applied automatically when needed
- **Layout preservation**: Word conversion maintains exact PDF appearance
- **Progress bars**: Single progress indicator instead of multiple status messages
- **Memory optimization**: Efficient temporary file handling
- **Error resilience**: Graceful handling of processing failures

### UI/UX Improvements
- **Consistent interfaces**: All modules follow same design patterns
- **Better file management**: Proper filename generation and MIME types
- **Documentation integration**: Complete help system accessible from main page
- **Status indicators**: Clear feedback for all operations
- **Responsive design**: Works across different screen sizes

## Conversion System Architecture

### Automatic OCR Pipeline
```
PDF Upload → Text Detection → OCR (if needed) → Format Conversion → Download
```

### Format-Specific Processing
- **Word**: pdf2docx for layout preservation + automatic OCR
- **Excel**: pdfplumber for table extraction + automatic OCR
- **Text**: pdfplumber for text extraction + automatic OCR
- **Images**: PyMuPDF for high-quality rendering
- **Other formats**: Specialized libraries for each format

### Quality Assurance
- **File validation**: Proper MIME types and extensions
- **Size verification**: Non-empty file checks
- **Error handling**: Graceful degradation on failures
- **User feedback**: Clear status messages and warnings

## External Dependencies

### Required for full functionality:

#### OCR Functionality
- **Tesseract OCR**: Required for OCRmyPDF
  - Windows: Download from GitHub releases
  - Linux: `sudo apt-get install tesseract-ocr tesseract-ocr-por`
  - macOS: `brew install tesseract tesseract-lang`

#### PDF Optimization
- **Ghostscript**: Required for advanced PDF compression
  - Windows: Download from official website
  - Linux: `sudo apt-get install ghostscript`
  - macOS: `brew install ghostscript`

#### Document Conversion
- **LibreOffice**: For advanced document conversions (optional)
- **Pandoc**: For format conversions (optional)

## System State & Architecture

### Current Status
- **All syntax verified** - no compilation errors
- **Architecture maintained** - all core functionality preserved
- **Performance optimized** - faster loading and processing
- **Code quality improved** - cleaner, more maintainable codebase
- **Documentation complete** - comprehensive help system
- **OCR automated** - seamless integration without manual steps

### Directory Structure
```
pdf_slicer/
├── app.py                 # Main Streamlit application
├── DOCUMENTACAO.md        # Complete system documentation
├── CLAUDE.md             # This file - Claude instructions
├── requirements.txt      # Python dependencies
├── modules/              # Feature modules
│   ├── pdf_converter.py   # Multi-format conversion
│   ├── pdf_splitter.py    # PDF splitting
│   ├── pdf_merger_final.py # PDF merging
│   ├── ocr.py             # OCR processing
│   ├── pdf_optimizer.py   # PDF optimization
│   └── settings.py        # Configuration
├── core/                 # Core processing
│   ├── XPTO.py           # Main processing pipeline
│   └── ui_components.py  # UI components
├── static/               # Static assets
│   └── styles.css        # Custom CSS
├── data/                 # Processing data (auto-created)
├── logs/                 # Application logs (auto-created)
└── output_pdf/          # Output directory (auto-created)
```

## Important Instructions

### Development Guidelines
- **NEVER create files unless absolutely necessary** for achieving your goal
- **ALWAYS prefer editing existing files** to creating new ones
- **NEVER proactively create documentation files** unless explicitly requested
- **Follow existing code patterns** and conventions
- **Maintain consistency** across all modules

### Key Principles
- **Web-first architecture**: All new features should be web-optimized
- **Automatic processing**: Minimize manual steps (like OCR automation)
- **User-friendly interfaces**: Clear examples and explanations
- **Error resilience**: Graceful handling of edge cases
- **Performance optimization**: Efficient memory and processing

### Testing Notes
- **OCR integration**: Test with both text and image PDFs
- **File downloads**: Verify correct MIME types and extensions
- **Large files**: Test with files near 200MB limit
- **Error conditions**: Test with corrupted or invalid PDFs
- **Cross-browser**: Test download functionality across browsers

## Security Considerations

### Data Handling
- **Stateless processing**: No persistent file storage
- **Session isolation**: Each user session is independent
- **Memory cleanup**: Automatic cleanup of temporary data
- **No content logging**: PDF contents are never logged

### Upload Security
- **File type validation**: Only PDF files accepted
- **Size limits**: 200MB maximum upload
- **Timeout protection**: Processing time limits
- **Sanitized filenames**: Safe filename generation

This system represents a modern, web-based PDF processing solution optimized for legal document workflows with comprehensive conversion capabilities and automated OCR integration.