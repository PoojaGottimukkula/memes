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

print(emotions_dialogues)
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
    if expression in emotions_dialogues:
        return random.choice(emotions_dialogues[expression])
    else:
        return "unrecognisable!!!!!!!!!!!!!!"

# Function to detect emotion from text using a simple heuristic (or a model)
def detect_text_emotion(text):
    text = text.lower()

    emotion_keywords = {
        'happy': {'happy', 'joy', 'glad', 'pleased', 'content', 'delighted'},
        'sad': {'sad', 'cry', 'upset', 'down', 'depressed', 'unhappy'},
        'angry': {'angry', 'mad', 'furious', 'irate', 'annoyed', 'outraged'},
        'fear': {'fear', 'scared', 'afraid', 'terrified', 'frightened', 'anxious'},
        'disgust': {'disgust', 'gross', 'revolted', 'nauseated', 'repulsed'},
        'surprise': {'surprise', 'shock', 'astonished', 'amazed', 'startled'},
        'neutral': {'neutral', 'okay', 'fine', 'alright', 'meh'}
    }

    for emotion, keywords in emotion_keywords.items():
        if any(word in text for word in keywords):
            return emotion.capitalize()

    return 'Neutral'

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

@app.route('/templates/main.html')
def main():
    return render_template('main.html')

@app.route('/templates/index.html')
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

# Function to create meme using Imgflip API
import requests

def create_meme_imgflip(template_id, top_text):
    payload = {
        'template_id': template_id,
        'username': 'pooja_G',  # Replace with your actual Imgflip username
        'password': 'pooja15d',  # Replace with your actual Imgflip password
        'text0': top_text,
    }
    response = requests.post('https://api.imgflip.com/caption_image', data=payload)
    if response.status_code == 200 and response.json().get('success'):
        return response.json()['data']['url']
    else:
        error_message = response.json().get('error_message', 'Unknown error')
        print('Error:', error_message)
        return None

# Map emotions to Imgflip meme template IDs
emotion_to_template = {
    'Angry': '259680',
    'Disgust': '175540452',
    'Fear': '226297822',
    'Happy': '12403754',
    'Sad': '61539',
    'Surprise': '155067746',
    'Neutral': '8072285'
}

@app.route('/generate', methods=['POST'])
def generate_meme():
    text = request.form.get('text')
    if not text:
        app.logger.error('No text provided')
        flash('No text provided')
        return redirect(url_for('index'))
    try:
        emotion = detect_text_emotion(text)
        # Get the template ID based on the emotion
        template_id = emotion_to_template.get(emotion, '21604248')  # Default to blank template if not found
        meme_url = create_meme_imgflip(template_id, text)
        if meme_url:
            return render_template('meme.html', meme_url=meme_url)
        else:
            flash('Failed to generate meme using Imgflip API')
            return redirect(url_for('index'))
    except Exception as e:
        app.logger.error(f'Failed to generate meme: {e}')
        flash('Failed to generate meme')
        return redirect(url_for('index'))


@app.route('/templates/meme.html')
def display_meme():
    meme_url = request.args.get('meme_url')
    return render_template('meme.html', meme_url=meme_url)


if __name__ == '__main__':
    if not os.path.exists(UPLOAD_FOLDER):
        os.makedirs(UPLOAD_FOLDER)
    if not os.path.exists(STATIC_FOLDER):
        os.makedirs(STATIC_FOLDER)
    app.run(debug=True,port=5501)
