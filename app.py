from flask import Flask, render_template, request, redirect, url_for
import os
import json
import logging
from werkzeug.utils import secure_filename
from main import extract_entities, extract_text_from_pdf, clean_text  # import your existing functions

app = Flask(__name__)

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# Allowed file extensions for uploading
ALLOWED_EXTENSIONS = {'pdf'}

# Define the upload folder
UPLOAD_FOLDER = 'uploads'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER


def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


@app.route('/')
def upload_file():
    return render_template('upload.html')


@app.route('/upload', methods=['POST'])
def handle_file_upload():
    if 'file' not in request.files:
        logging.error('No file part')
        return redirect(request.url)
    file = request.files['file']
    if file.filename == '':
        logging.error('No selected file')
        return redirect(request.url)
    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(filepath)

        # Extract text and entities from the uploaded PDF
        text = extract_text_from_pdf(filepath, use_ocr=True)
        if not text:
            logging.warning("No text extracted from the PDF.")
            return redirect(request.url)

        text = clean_text(text)
        entities = extract_entities(text)

        # Save the extracted entities to JSON
        json_file_name = os.path.splitext(filename)[0] + "_extracted_data.json"
        with open(json_file_name, 'w', encoding='utf-8') as json_file:
            json.dump(entities, json_file, ensure_ascii=False, indent=4)

        return render_template('entities.html', entities=entities)


if __name__ == '__main__':
    app.run(debug=True)
