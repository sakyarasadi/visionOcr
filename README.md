# News OCR - Sinhala and English Text Extraction

A Flask-based OCR API that extracts text from images containing Sinhala or English news articles.

## Features

- Extract text from images containing Sinhala and English text
- RESTful API endpoint
- Works as standalone EXE
- No hardcoded file paths - automatically finds Tesseract

## Installation

1. Install Python dependencies:
```bash
pip install -r requirements.txt
```

2. Install Tesseract OCR:
   - Download from: https://github.com/UB-Mannheim/tesseract/wiki
   - During installation, make sure to add Tesseract to your system PATH
   - Or place `tesseract.exe` in the same directory as your application

3. Install Tesseract language data for Sinhala:
   - Download `sin.traineddata` from: https://github.com/tesseract-ocr/tessdata
   - Place it in Tesseract's `tessdata` folder

## Running the Application

### Development Mode:
```bash
python app.py
```

The API will be available at: `http://localhost:5000`

### API Endpoints

**GET /** - API information
```bash
curl http://localhost:5000/
```

**POST /ocr** - Extract text from image
```bash
curl -X POST -F "image=@your_image.jpg" http://localhost:5000/ocr
```

## Building EXE

1. Install PyInstaller:
```bash
pip install pyinstaller
```

2. Build the EXE:
```bash
python build_exe.py
```

Or manually:
```bash
pyinstaller --onefile --name=NewsOCR app.py
```

3. For EXE deployment:
   - Place `tesseract.exe` in the same directory as your EXE
   - Or ensure Tesseract is in the system PATH
   - The application will automatically find Tesseract

## Notes

- The application automatically detects Tesseract from:
  1. System PATH
  2. Same directory as the executable (for EXE)
  3. Default pytesseract detection

- No hardcoded paths are used, making it portable across different systems

