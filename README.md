
# Meme Generator

This project is a Meme Generator web application built using Flask. It allows users to upload an image and generate a meme by overlaying text based on the detected emotion from the image. Additionally, users can generate memes by providing text, and the application will fetch an image from Google based on the detected emotion in the text.

## Features

- Upload an image to detect the emotion and generate a meme with text from a predefined dataset.
- Generate a meme by providing text, which detects the emotion and fetches a relevant image from Google.
- Display the generated meme.

## Prerequisites

- Python 3.6 or higher
- TensorFlow
- OpenCV
- Flask
- Google Custom Search API Key and Search Engine ID

## Setup

1. **Clone the repository:**
    ```bash
    git clone https://github.com/yourusername/meme-generator.git
    cd meme-generator
    ```

2. **Install the required packages:**
    ```bash
    pip install -r requirements.txt
    ```

3. **Download or train an emotion detection model:**
    - Ensure you have a pre-trained model named `emotiondetector.h5` in the project directory.

4. **Set up Google Custom Search API:**
    - Obtain a Google API Key and a Search Engine ID from the Google Developer Console.
    - Replace the placeholder values in `app.py` with your API Key and Search Engine ID:
        ```python
        GOOGLE_API_KEY = 'YOUR_GOOGLE_API_KEY'
        SEARCH_ENGINE_ID = 'YOUR_SEARCH_ENGINE_ID'
        ```

5. **Prepare the dataset:**
    - Ensure you have a dataset file named `train.txt` in the `dataset2` directory. The file should contain dialogues and their corresponding emotions in the format:
        ```
        dialogue1;emotion1
        dialogue2;emotion2
        ```

6. **Create necessary directories:**
    ```bash
    mkdir uploads static
    ```

## Running the Application

1. **Start the Flask server:**
    ```bash
    python app.py
    ```

2. **Access the application:**
    - Open your web browser and navigate to `http://127.0.0.1:5000`.

## Usage

1. **Upload Image to Generate Meme:**
    - Select an image file and click the "Upload Image" button.
    - The application will detect the emotion from the image, generate a dialogue based on the emotion, and create a meme with the dialogue overlaid on the image.

2. **Generate Meme from Text:**
    - Enter some text and click the "Generate Meme" button.
    - The application will detect the emotion from the text, fetch a relevant image from Google, and create a meme with the provided text overlaid on the image.

## Project Structure

- `app.py`: The main Flask application file.
- `templates/`: Directory containing the HTML templates.
  - `index.html`: The main page for uploading images and generating memes.
  - `meme.html`: The page for displaying the generated meme.
- `uploads/`: Directory for storing uploaded images.
- `static/`: Directory for storing generated memes.
- `dataset2/train.txt`: The dataset file containing dialogues and their corresponding emotions.
- `emotiondetector.h5`: The pre-trained emotion detection model.
