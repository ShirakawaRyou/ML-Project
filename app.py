from flask import Flask, request, jsonify
import pytesseract
from PIL import Image
import numpy as np
import joblib
import os

app = Flask(__name__)

# Load the models
MODEL_PATH = os.path.join('models', 'language_model.pkl')
VECTORIZER_PATH = os.path.join('models', 'vectorizer.pkl')

def load_models():
    try:
        model = joblib.load(MODEL_PATH)
        vectorizer = joblib.load(VECTORIZER_PATH)
        return model, vectorizer
    except:
        return None, None

def perform_ocr(image_path):
    """
    Perform OCR on the image and return the extracted text
    """
    try:
        # Try different languages
        lang_string = 'eng+chi_sim+chi_tra+fra+deu+spa+ita+rus+jpn+kor+ara+...'
        text = pytesseract.image_to_string(Image.open(image_path), lang=lang_string)
        
        return {
            'traditional_chinese': text.strip(),
            'simplified_chinese': text.strip(),
            'english': text.strip()
        }
    except Exception as e:
        return {'error': str(e)}

@app.route('/', methods=['GET'])
def upload_form():
    return '''
    <html>
        <head><title>Upload Image for OCR</title></head>
        <body>
            <h2>Upload an Image for OCR Language Identification</h2>
            <form method="POST" action="/identify" enctype="multipart/form-data">
                <input type="file" name="image" accept="image/*" required><br><br>
                <input type="submit" value="Upload and Identify">
            </form>
        </body>
    </html>
    '''

@app.route('/identify', methods=['GET', 'POST'])
def identify_language():
    if request.method == 'GET':
        return '<h3>This endpoint is for image upload via POST. Please use the form on the home page.</h3>', 200
    if 'image' not in request.files:
        return '<h3>No image file provided. Please go back and select a file.</h3>', 400
    image_file = request.files['image']
    if image_file.filename == '':
        return '<h3>No selected file. Please go back and select a file.</h3>', 400
    # Save the uploaded image temporarily
    temp_path = 'static/temp_image.jpg'
    os.makedirs('static', exist_ok=True)
    image_file.save(temp_path)
    # Perform OCR (use all languages for best extraction)
    extracted_text = pytesseract.image_to_string(Image.open(temp_path), lang='chi_sim+chi_tra+eng').strip()
    # Load model and vectorizer
    model, vectorizer = load_models()
    if not model or not vectorizer:
        os.remove(temp_path)
        return '<h3>Model or vectorizer not found. Please check your setup.</h3>', 500
    # Predict language
    X = vectorizer.transform([extracted_text])
    predicted_language = model.predict(X)[0]
    # Render result as HTML
    result_html = f'''
    <html>
        <head><title>OCR Result</title></head>
        <body>
            <h2>Uploaded Image</h2>
            <img src="/static/temp_image.jpg" alt="Uploaded Image" style="max-width:400px;"><br><br>
            <h2>Extracted Text</h2>
            <pre style="background:#f4f4f4;padding:10px;">{extracted_text}</pre>
            <h2>Identified Language</h2>
            <p style="font-size:1.2em;font-weight:bold;">{predicted_language}</p>
            <a href="/">Upload another image</a>
        </body>
    </html>
    '''
    return result_html

@app.route('/health', methods=['GET'])
def health_check():
    return jsonify({'status': 'healthy'})

if __name__ == '__main__':
    app.run(debug=True)
