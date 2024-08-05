from flask import Flask, request, render_template, redirect, url_for, flash, send_file
from werkzeug.utils import secure_filename
import requests
import os
import random
import tensorflow as tf
import numpy as np
import cv2
import logging

app = Flask(__name__)
app.secret_key = 'supersecretkey'  # Needed for flashing messages
UPLOAD_FOLDER = 'uploads'
STATIC_FOLDER = 'static'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['STATIC_FOLDER'] = STATIC_FOLDER

logging.basicConfig(level=logging.DEBUG)

# Load the pre-trained emotion detection model
model = tf.keras.models.load_model('emotiondetector.h5')

# Define emotions
emotions = {
    0: "Angry",
    1: "Disgust",
    2: "Fear",
    3: "Happy",
    4: "Sadness",
    5: "Surprise",
    6: "Neutral"
}

# Load dialogues dataset
dataset_path = "dataset1/train.txt"
emotions_dialogues = {}

with open(dataset_path, 'r') as file:
    lines = file.readlines()

for line in lines:
    dialogue, emotion = line.strip().split(';')
    if emotion in emotions_dialogues:
        emotions_dialogues[emotion].append(dialogue)
    else:
        emotions_dialogues[emotion] = [dialogue]

# Google Custom Search API credentials
GOOGLE_API_KEY = 'YOUR_GOOGLE_API_KEY'
SEARCH_ENGINE_ID = 'YOUR_SEARCH_ENGINE_ID'

# Function to preprocess the image for emotion detection
def preprocess_image(image_path):
    image = cv2.imread(image_path)
    image = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    image = cv2.resize(image, (48, 48))
    image = np.expand_dims(image, axis=0)
    image = image / 255.0
    return image

# Function to predict the emotion from an image
def predict_emotion(image_array):
    prediction = model.predict(image_array)
    expression_class = np.argmax(prediction)
    return emotions[expression_class]

# Function to generate dialogue based on emotion
def generate_dialogue(expression):
    expression = expression.lower()
    if expression in emotions_dialogues:
        return random.choice(emotions_dialogues[expression])
    else:
        return "unrecognisable!!!!!!!!!!!!!!"

# Function to detect emotion from text using a simple heuristic (or a model)
def detect_text_emotion(text):
    text = text.lower()
    if 'happy' in text or 'joy' in text:
        return 'Happy'
    elif 'sad' in text or 'cry' in text:
        return 'Sadness'
    elif 'angry' in text or 'mad' in text:
        return 'Angry'
    elif 'fear' in text or 'scared' in text:
        return 'Fear'
    elif 'disgust' in text or 'gross' in text:
        return 'Disgust'
    elif 'surprise' in text or 'shock' in text:
        return 'Surprise'
    else:
        return 'Neutral'

# Function to fetch image from Google based on the emotion
def fetch_image_from_google(emotion):
    search_url = f"https://www.googleapis.com/customsearch/v1?q={emotion}&cx={SEARCH_ENGINE_ID}&key={GOOGLE_API_KEY}&searchType=image"
    response = requests.get(search_url)
    data = response.json()
    if 'items' in data:
        image_url = random.choice(data['items'])['link']
        return image_url
    return None

# Function to wrap text into multiple lines
def wrap_text(text, font, font_scale, font_thickness, max_width):
    words = text.split(' ')
    lines = []
    current_line = words[0]
    for word in words[1:]:
        test_line = current_line + ' ' + word
        size = cv2.getTextSize(test_line, font, font_scale, font_thickness)[0]
        if size[0] < max_width:
            current_line = test_line
        else:
            lines.append(current_line)
            current_line = word
    lines.append(current_line)
    return lines

# Function to overlay text on an image
def overlay_text(image_path, text):
    image = cv2.imread(image_path)
    font = cv2.FONT_HERSHEY_SIMPLEX
    font_scale = 1
    font_thickness = 2
    max_width = image.shape[1] - 20

    lines = wrap_text(text, font, font_scale, font_thickness, max_width)

    y = 50
    line_height = cv2.getTextSize("Test", font, font_scale, font_thickness)[0][1] + 10

    for line in lines:
        size = cv2.getTextSize(line, font, font_scale, font_thickness)[0]
        x = (image.shape[1] - size[0]) // 2
        cv2.putText(image, line, (x, y), font, font_scale, (255, 255, 255), font_thickness)
        y += line_height

    output_path = os.path.join(app.config['STATIC_FOLDER'], 'meme_output.jpg')
    cv2.imwrite(output_path, image)
    return output_path

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/upload', methods=['POST'])
def upload_file():
    if 'file' not in request.files:
        app.logger.error('No file part')
        flash('No file part')
        return redirect(url_for('index'))
    file = request.files['file']
    if file.filename == '':
        app.logger.error('No selected file')
        flash('No selected file')
        return redirect(url_for('index'))
    if file:
        filename = secure_filename(file.filename)
        file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        try:
            file.save(file_path)
        except Exception as e:
            app.logger.error(f'Failed to save file: {e}')
            flash('Failed to save file')
            return redirect(url_for('index'))

        try:
            preprocessed_image = preprocess_image(file_path)
            emotion = predict_emotion(preprocessed_image)
            dialogue = generate_dialogue(emotion)
            text = f"{dialogue} --- {emotion}"
            meme_path = overlay_text(file_path, text)
            return send_file(meme_path, mimetype='image/jpeg')
        except Exception as e:
            app.logger.error(f'Failed to process image: {e}')
            flash('Failed to process image')
            return redirect(url_for('index'))

@app.route('/generate', methods=['POST'])
def generate_meme():
    text = request.form.get('text')
    if not text:
        app.logger.error('No text provided')
        flash('No text provided')
        return redirect(url_for('index'))
    try:
        emotion = detect_text_emotion(text)
        image_url = fetch_image_from_google(emotion)
        if image_url:
            response = requests.get(image_url)
            image_path = os.path.join(app.config['STATIC_FOLDER'], 'text_image.jpg')
            with open(image_path, 'wb') as f:
                f.write(response.content)
            meme_path = overlay_text(image_path, text)
            return send_file(meme_path, mimetype='image/jpeg')
        else:
            app.logger.error('Failed to fetch image from Google')
            flash('Failed to fetch image from Google')
            return redirect(url_for('index'))
    except Exception as e:
        app.logger.error(f'Failed to generate meme: {e}')
        flash('Failed to generate meme')
        return redirect(url_for('index'))

@app.route('/meme')
def display_meme():
    meme_path = request.args.get('meme_path')
    return render_template('meme.html', meme_path=meme_path)

if __name__ == '__main__':
    if not os.path.exists(UPLOAD_FOLDER):
        os.makedirs(UPLOAD_FOLDER)
    if not os.path.exists(STATIC_FOLDER):
        os.makedirs(STATIC_FOLDER)
    app.run(debug=True)
