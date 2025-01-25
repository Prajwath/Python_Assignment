import re
import os
import pdfplumber
from docx import Document
import logging
import fitz  # PyMuPDF
import pytesseract
from PIL import Image
import io

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# Set tesseract path if needed (only for Windows)
pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'  # Change to your Tesseract path

def extract_text_from_pdf(pdf_file, use_ocr=False):
    """Extract text from a PDF file using pdfplumber or OCR."""
    try:
        if use_ocr:
            return extract_text_using_ocr(pdf_file)
        else:
            with pdfplumber.open(pdf_file) as pdf:
                text = ""
                for page in pdf.pages:
                    text += page.extract_text() + "\n"
            return text
    except Exception as e:
        logging.error(f"Failed to extract text from {pdf_file}: {e}")
        return ""

def extract_text_using_ocr(pdf_file):
    """Convert PDF pages to images and perform OCR to extract text."""
    pdf_document = fitz.open(pdf_file)
    extracted_text = ""
    for page_num in range(len(pdf_document)):
        page = pdf_document[page_num]
        pix = page.get_pixmap()
        img = Image.open(io.BytesIO(pix.tobytes()))
        text = pytesseract.image_to_string(img, lang='eng')
        extracted_text += text + "\n"
    return extracted_text

def save_text_to_file(text, file_name):
    """Save text to a .txt file."""
    try:
        with open(file_name, 'w', encoding='utf-8') as file:
            file.write(text)
        logging.info(f"Extracted text saved to {file_name}")
    except Exception as e:
        logging.error(f"Failed to save text to {file_name}: {e}")

def clean_text(text):
    """
    Clean and normalize the text to add spaces where needed and remove extra spaces.
    """
    # Add space before capital letters in concatenated words
    text = re.sub(r'([a-z])([A-Z])', r'\1 \2', text)
    # Ensure there is a space after punctuation marks that don't already have one
    text = re.sub(r'([a-zA-Z0-9])([,.!?;])', r'\1 \2', text)
    # Remove any extra spaces and normalize
    text = re.sub(r'\s+', ' ', text).strip()
    return text

def split_text_into_paragraphs(text):
    """
    Split cleaned text into paragraphs based on sentences.
    Group sentences into paragraphs after every 3 sentences or at the end of a sentence if it ends with a dot followed by a space.
    """
    # Normalize spaces by replacing multiple spaces or line breaks with a single space
    normalized_text = re.sub(r'\s+', ' ', text)
    # Split text into sentences using regex
    sentences = re.split(r'(?<=[.!?]) +', normalized_text.strip())
    paragraphs = []
    current_paragraph = []
    for i, sentence in enumerate(sentences):
        current_paragraph.append(sentence)
        # Check if we've reached 3 sentences or if the sentence ends with a dot followed by a space
        if len(current_paragraph) == 3 or (i < len(sentences) - 1 and sentences[i + 1].startswith(' ')):
            paragraphs.append(' '.join(current_paragraph))
            current_paragraph = []
    # Add any remaining sentences as a final paragraph
    if current_paragraph:
        paragraphs.append(' '.join(current_paragraph))
    return paragraphs

def save_text_to_docx(paragraphs, docx_file_name):
    """
    Save paragraphs to a .docx file.
    """
    doc = Document()
    for para in paragraphs:
        doc.add_paragraph(para)
    doc.save(docx_file_name)
    logging.info(f"Document saved to {docx_file_name}")

def extract_entities(text):
    """Extract specified entities using regular expressions."""
    entities = {
        "Beneficiary Name": re.search(r"(?:To|in\s*favor\s*of)\s*,?\s*([\w\s&'-]+)", text, re.IGNORECASE).group(1).strip(),
        "Applicant Name": re.findall(r"(?:M/s|Applicant\s*Name)\s*([\w\s]+)", text, re.IGNORECASE),
        "BG Number": list(set(re.findall(r"BGNO[:\-]?\s*([\w\d]+)", text, re.IGNORECASE))),
        "Claim Date": re.findall(r"i\s\.e\s\.([\d]{1,2}[-/][\d]{1,2}[-/][\d]{4})", text, re.IGNORECASE),
        "Expiry Date": re.findall(r"till\s*([\d]{1,2}[-/][\d]{1,2}[-/][\d]{4})", text, re.IGNORECASE),
        "Currency": list(set(re.findall(r"INR|EUR|USD|GBP", text, re.IGNORECASE))),
        "Issue Date": list(
            set(re.findall(r"IssuanceDate[:\-]?\s*([\d]{1,2}[-/][\d]{1,2}[-/][\d]{4})", text, re.IGNORECASE))),
        "Beneficiary Country": re.findall(r"Beneficiary Country:\s*(.*?)[,.\n]", text, re.IGNORECASE),
        "Applicant Country": re.findall(r"Applicant Country:\s*(.*?)[,.\n]", text, re.IGNORECASE),
        "Issuing Bank Name": re.findall(r"madeby\s*(.*?),", text, re.IGNORECASE),
        "BG Amount (in Words)": list(set(re.findall(r"\(Rupees([A-Za-z]+)only\)", text, re.IGNORECASE))),
        "BG Amount (in Numbers)": list(set(re.findall(r"(\d[0-9],\d[0-9]*)", text, re.IGNORECASE))),
        "Applicant Address": re.findall(r"M/s\.\s*[A-Za-z\s,&]+,\s*.*?at\s*(.+)", text, re.IGNORECASE),
        "Beneficiary Address": re.findall(r"Beneficiary Address:\s*(.*?)[.\n]", text, re.IGNORECASE),
    }
    return {key: value if value else None for key, value in entities.items()}  # Handle missing entities

def main():
    # Input PDF file
    pdf_file = "PS-7.pdf"  # Replace with your PDF file name
    use_ocr = True  # Set to True to use OCR extraction

    if not os.path.exists(pdf_file):
        logging.error(f"The file {pdf_file} does not exist.")
        return

    # Extract text from the PDF file (using OCR if needed)
    text = extract_text_from_pdf(pdf_file, use_ocr=use_ocr)
    if not text:
        logging.warning("No text extracted from the PDF.")
        return

    # Clean the text
    text = clean_text(text)

    # Save the extracted text to a .txt file
    txt_file_name = os.path.splitext(pdf_file)[0] + ".txt"
    save_text_to_file(text, txt_file_name)

    # Split text into paragraphs
    paragraphs = split_text_into_paragraphs(text)
    logging.info("\nParagraphs:")
    for i, para in enumerate(paragraphs, 1):
        logging.info(f"Paragraph {i}: {para}\n")

    # Save the paragraphs to a .docx file
    docx_file_name = os.path.splitext(pdf_file)[0] + ".docx"
    save_text_to_docx(paragraphs, docx_file_name)

    # Extract entities
    entities = extract_entities(text)
    logging.info("\nExtracted Entities:")
    for key, value in entities.items():
        logging.info(f"{key}: {value}")

if __name__ == "__main__":
    main()
