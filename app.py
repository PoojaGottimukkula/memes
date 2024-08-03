from flask import Flask, request, render_template, send_file
from werkzeug.utils import secure_filename
from PIL import Image, ImageDraw, ImageFont
import numpy as np
import tensorflow as tf
import os
import logging

app = Flask(__name__)
model = tf.keras.models.load_model('emotiondetector.h5')
UPLOAD_FOLDER = 'uploads'
STATIC_FOLDER = 'static'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['STATIC_FOLDER'] = STATIC_FOLDER

logging.basicConfig(level=logging.DEBUG)

def preprocess_image(image_path):
    image = Image.open(image_path).resize((48, 48)).convert('L')
    image_array = np.array(image) / 255.0
    return np.expand_dims(image_array, axis=0)

def predict_emotion(image_array):
    prediction = model.predict(image_array)
    emotion_labels = ['angry', 'disgust', 'fear', 'happy', 'neutral', 'sad', 'surprise']
    return emotion_labels[np.argmax(prediction)]

def create_meme(image_path, text):
    image = Image.open(image_path)
    draw = ImageDraw.Draw(image)
    font = ImageFont.load_default()
    text_position = (10, 10)
    draw.text(text_position, text, font=font, fill='white')
    meme_path = os.path.join(app.config['STATIC_FOLDER'], 'meme_output.jpg')
    image.save(meme_path)
    return meme_path

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/upload', methods=['POST'])
def upload_file():
    if 'file' not in request.files:
        app.logger.error('No file part')
        return 'No file part', 400
    file = request.files['file']
    if file.filename == '':
        app.logger.error('No selected file')
        return 'No selected file', 400
    if file:
        filename = secure_filename(file.filename)
        file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        try:
            file.save(file_path)
        except Exception as e:
            app.logger.error(f'Failed to save file: {e}')
            return 'Failed to save file', 500
        
        try:
            image_array = preprocess_image(file_path)
            emotion = predict_emotion(image_array)
            text = f"Feeling {emotion.capitalize()}"
            meme_path = create_meme(file_path, text)
            return send_file(meme_path, mimetype='image/jpeg')
        except Exception as e:
            app.logger.error(f'Failed to process image: {e}')
            return 'Failed to process image', 500

@app.route('/generate', methods=['POST'])
def generate_meme():
    text = request.form.get('text')
    if not text:
        app.logger.error('No text provided')
        return 'No text provided', 400
    try:
        emotion = text_to_emotion(text)
        image_path = select_image(emotion)
        meme_path = create_meme(image_path, text)
        return send_file(meme_path, mimetype='image/jpeg')
    except Exception as e:
        app.logger.error(f'Failed to generate meme: {e}')
        return 'Failed to generate meme', 500

def text_to_emotion(text):
    # Implement your logic to determine emotion from text
    return 'happy'  # Example

def select_image(emotion, image_folder='dataset2/images'):
    for filename in os.listdir(image_folder):
        if emotion in filename:
            return os.path.join(image_folder, filename)
    return os.path.join(image_folder, 'default_image.jpg')

if __name__ == '__main__':
    if not os.path.exists(UPLOAD_FOLDER):
        os.makedirs(UPLOAD_FOLDER)
    if not os.path.exists(STATIC_FOLDER):
        os.makedirs(STATIC_FOLDER)
    app.run(debug=True)
