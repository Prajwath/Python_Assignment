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

# Set Tesseract path if needed (only for Windows)
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
        img = Image.open(io.BytesIO(pix.tobytes())).convert('L')  # Convert to grayscale for better OCR accuracy
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
    """Clean and normalize the text to add spaces where needed and remove extra spaces."""
    # Add space before capital letters in concatenated words
    text = re.sub(r'([a-z])([A-Z])', r'\1 \2', text)
    # Ensure there is a space after punctuation marks that don't already have one
    text = re.sub(r'([a-zA-Z0-9])([,.!?;])', r'\1 \2', text)
    # Remove any extra spaces and normalize
    text = re.sub(r'\s+', ' ', text).strip()
    return text


def split_text_into_paragraphs(text):
    """Split cleaned text into paragraphs based on sentences."""
    sentences = re.split(r'(?<=[.!?]) +', text.strip())
    paragraphs = []
    current_paragraph = []

    for i, sentence in enumerate(sentences):
        current_paragraph.append(sentence)
        if len(current_paragraph) == 3 or i == len(sentences) - 1:
            paragraphs.append(' '.join(current_paragraph))
            current_paragraph = []

    return paragraphs


def save_text_to_docx(paragraphs, docx_file_name):
    """Save paragraphs to a .docx file."""
    doc = Document()
    for para in paragraphs:
        doc.add_paragraph(para)
    doc.save(docx_file_name)
    logging.info(f"Document saved to {docx_file_name}")


def extract_entities(text):
    """Extract specified entities using regular expressions."""
    entities = {}

    # Extract Beneficiary Name
    match = re.search(r"(?:To|in\s*favor\s*of)\s*,?\s*([\w\s&'-]+)", text, re.IGNORECASE)
    if match:
        entities["Beneficiary Name"] = match.group(1).strip()
    else:
        entities["Beneficiary Name"] = None

    # Extract Applicant Name
    match = re.search(r"(?:Applicant|Bidder|M/s)\.?\s*([\w\s&'-]+?(?=,|having|and|with|$))", text, re.IGNORECASE)
    if match:
        entities["Applicant Name"] = match.group(1).strip()
    else:
        entities["Applicant Name"] = None

    # Extract BG Number
    match = re.search(r"(BG NO|BG Number)[:\-\s]?\s*([\w\d]+)", text, re.IGNORECASE)
    if match:
        entities["BG Number"] = match.group(2).strip()
    else:
        entities["BG Number"] = None

    # Extract Claim Date
    matches = re.findall(r"i\.e\.([\d]{1,2}[-/][\d]{1,2}[-/][\d]{4})", text, re.IGNORECASE)
    if matches:
        entities["Claim Date"] = matches
    else:
        entities["Claim Date"] = None

    # Extract Expiry Date
    matches = re.findall(r"till\s*([\d]{1,2}[-/][\d]{1,2}[-/][\d]{4})", text, re.IGNORECASE)
    if matches:
        entities["Expiry Date"] = matches
    else:
        entities["Expiry Date"] = None

    # Extract Currency
    matches = re.findall(r"INR|EUR|USD|GBP", text, re.IGNORECASE)
    if matches:
        entities["Currency"] = list(set(matches))
    else:
        entities["Currency"] = None

    # Extract Issue Date
    matches = re.findall(r"Issuance Date[:\-]?\s*([\d]{1,2}[-/][\d]{1,2}[-/][\d]{4})", text, re.IGNORECASE)
    if matches:
        entities["Issue Date"] = list(set(matches))
    else:
        entities["Issue Date"] = None

    # Extract Beneficiary Country
    matches = re.findall(r"Beneficiary Country:\s*(.*?)[,.\n]", text, re.IGNORECASE)
    if matches:
        entities["Beneficiary Country"] = matches
    else:
        entities["Beneficiary Country"] = None

    # Extract Applicant Country
    matches = re.findall(r"Applicant Country:\s*(.*?)[,.\n]", text, re.IGNORECASE)
    if matches:
        entities["Applicant Country"] = matches
    else:
        entities["Applicant Country"] = None

    # Extract Issuing Bank Name
    matches = re.findall(r"made by\s*(.*?),", text, re.IGNORECASE)
    if matches:
        entities["Issuing Bank Name"] = matches
    else:
        entities["Issuing Bank Name"] = None

    # Extract BG Amount (in Words)
    matches = re.findall(r"\(Rupees([A-Za-z\s]+)only\)", text, re.IGNORECASE)
    if matches:
        entities["BG Amount (in Words)"] = list(set(matches))
    else:
        entities["BG Amount (in Words)"] = None

    # Extract BG Amount (in Numbers)
    matches = re.findall(r"(\d[0-9],\d[0-9]*)", text, re.IGNORECASE)
    if matches:
        entities["BG Amount (in Numbers)"] = list(set(matches))
    else:
        entities["BG Amount (in Numbers)"] = None

    # Extract Applicant Address
    matches = re.findall(r"M/s\.\s*[A-Za-z\s,&]+,\s*.*?at\s*(.+)", text, re.IGNORECASE)
    if matches:
        entities["Applicant Address"] = matches
    else:
        entities["Applicant Address"] = None

    # Extract Beneficiary Address
    matches = re.findall(r"Beneficiary Address:\s*(.*?)[.\n]", text, re.IGNORECASE)
    if matches:
        entities["Beneficiary Address"] = matches
    else:
        entities["Beneficiary Address"] = None

    return entities


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
        logging.info(f"{key}: {value if value else 'Not Found'}")


if __name__ == "__main__":
    main()