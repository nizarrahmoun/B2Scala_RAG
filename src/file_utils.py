"""
File processing utilities for handling PDFs and images.
"""
import PyPDF2
import io
import os
from PIL import Image
import streamlit as st

def extract_text_from_pdf(pdf_file):
    """Extract text from uploaded PDF file."""
    try:
        pdf_reader = PyPDF2.PdfReader(pdf_file)
        text = ""
        for page in pdf_reader.pages:
            text += page.extract_text() + "\n"
        return text
    except Exception as e:
        st.error(f"Error reading PDF: {str(e)}")
        return None

def extract_text_from_scala(scala_file):
    """Extract text from uploaded Scala file."""
    try:
        # Read the file content as text
        content = scala_file.read()
        # Try to decode as UTF-8, fallback to latin-1 if needed
        try:
            text = content.decode('utf-8')
        except UnicodeDecodeError:
            text = content.decode('latin-1')
        
        # Basic validation for Scala file
        if not any(keyword in text for keyword in ['object', 'class', 'def', 'val', 'var', 'import']):
            st.warning("⚠️ This doesn't appear to be a valid Scala file. Proceeding anyway...")
        
        return text
    except Exception as e:
        st.error(f"Error reading Scala file: {str(e)}")
        return None

def get_file_type_icon(file_type, file_name):
    """Get appropriate icon for file type."""
    if file_type == "application/pdf":
        return "📄"
    elif file_type in ["image/png", "image/jpeg", "image/jpg", "image/bmp", "image/tiff"]:
        return "🖼️"
    elif file_name.lower().endswith('.scala'):
        return "⚙️"
    else:
        return "📁"

def extract_text_from_image(image_file):
    """Extract text from uploaded image file using OCR."""
    try:
        # Check if Tesseract is available
        try:
            import pytesseract
        except ImportError:
            st.error("pytesseract is not installed. Please install it using: pip install pytesseract")
            return None
        
        # Open the image
        image = Image.open(image_file)
        
        # Convert to RGB if necessary
        if image.mode != 'RGB':
            image = image.convert('RGB')
        
        # Try to set Tesseract path for Windows
        import platform
        if platform.system() == "Windows":
            # Common Windows installation paths
            possible_paths = [
                r'C:\Program Files\Tesseract-OCR\tesseract.exe',
                r'C:\Program Files (x86)\Tesseract-OCR\tesseract.exe',
                r'C:\Tesseract-OCR\tesseract.exe'
            ]
            for path in possible_paths:
                if os.path.exists(path):
                    pytesseract.pytesseract.tesseract_cmd = path
                    break
        
        # Extract text using OCR
        text = pytesseract.image_to_string(image)
        
        if not text.strip():
            st.warning("No text was detected in the image. Please ensure the image contains clear, readable text.")
            return None
            
        return text
    except pytesseract.TesseractNotFoundError:
        st.error("Tesseract OCR is not installed or not found in PATH.")
        st.info("Please install Tesseract OCR. See TESSERACT_SETUP.md for installation instructions.")
        return None
    except Exception as e:
        st.error(f"Error processing image: {str(e)}")
        return None

def process_uploaded_file(uploaded_file):
    """Process uploaded file and extract text content."""
    if uploaded_file is None:
        return None
    
    file_type = uploaded_file.type
    file_name = uploaded_file.name.lower()
    
    if file_type == "application/pdf":
        return extract_text_from_pdf(uploaded_file)
    elif file_type in ["image/png", "image/jpeg", "image/jpg", "image/bmp", "image/tiff"]:
        return extract_text_from_image(uploaded_file)
    elif file_name.endswith('.scala') or file_type in ["text/plain", "application/octet-stream"]:
        # Handle .scala files (they might come as text/plain or application/octet-stream)
        return extract_text_from_scala(uploaded_file)
    else:
        st.error(f"Unsupported file type: {file_type}")
        st.info("Supported formats: PDF, PNG, JPG, JPEG, BMP, TIFF, SCALA")
        return None

def validate_file_size(uploaded_file, max_size_mb=10):
    """Validate uploaded file size."""
    if uploaded_file is None:
        return True
    
    file_size_mb = len(uploaded_file.getvalue()) / (1024 * 1024)
    if file_size_mb > max_size_mb:
        st.error(f"File size ({file_size_mb:.1f} MB) exceeds maximum allowed size ({max_size_mb} MB)")
        return False
    return True
