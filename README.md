# MemeForge: A Comprehensive Tool for Memetic Creativity

MemeForge is a Flask-based web application that combines advanced emotion detection with automated meme generation. Users can upload images or input text, and the application generates personalized memes based on the detected emotions. The tool leverages a pre-trained Convolutional Neural Network (CNN) model for emotion detection and integrates with the Imgflip API for dynamic meme creation.

## Features

- **Emotion Detection**: Uses a pre-trained CNN model to detect emotions from uploaded images.
- **Meme Generation**: Automatically generates memes based on the detected emotions or user-provided text.
- **Imgflip API Integration**: Utilizes Imgflip API to generate memes using popular templates.
- **User-Friendly Interface**: Simple and intuitive web interface for easy image upload and meme creation.

## Installation

1. **Clone the repository**:
    ```sh
    git clone https://github.com/yourusername/MemeForge.git
    cd MemeForge
    ```

2. **Set up a virtual environment**:
    ```sh
    python -m venv venv
    source venv/bin/activate   # On Windows, use `venv\Scripts\activate`
    ```

3. **Install the dependencies**:
    ```sh
    pip install -r requirements.txt
    ```

4. **Place the pre-trained emotion detection model**:
    - Download the `emotiondetector.h5` model file and place it in the root directory of the project.

5. **Create necessary folders**:
    ```sh
    mkdir uploads static
    ```

## Configuration

Make sure to set the correct configurations for the Flask application:

- **`UPLOAD_FOLDER`**: Directory to store uploaded images.
- **`STATIC_FOLDER`**: Directory to store static files and generated memes.
- **Secret Key**: Set a secret key for Flask sessions.

## Running the Application

1. **Start the Flask server**:
    ```sh
    python app.py
    ```

2. **Access the application**:
    Open your web browser and navigate to `http://127.0.0.1:5500/templates/index.html` to view the sample.

## Usage

### Upload an Image

1. Go to `http://127.0.0.1:5500/templates/index.html`.
2. Use the image upload form to select and upload an image.
3. The application will process the image, detect the emotion, and generate a meme based on the detected emotion.

### Generate Meme from Text

1. Go to `http://127.0.0.1:5500/templates/index.html`.
2. Use the text input form to enter the text.
3. The application will detect the emotion from the text and generate a meme using the appropriate template from Imgflip.

## File Structure

```plaintext
MemeForge/
│
├── app.py                      # Main Flask application
├── emotiondetector.h5          # Pre-trained emotion detection model
├── requirements.txt            # Python dependencies
├── templates/
│   ├── index.html              # Main page for image upload and text input
│   └── meme.html               # Page to display the generated meme
├── uploads/                    # Directory for uploaded images
├── static/                     # Directory for static files and generated memes
```

## Contributing

Contributions are welcome! Please create an issue or submit a pull request for any features, bug fixes, or enhancements.

## Acknowledgments

- [Imgflip](https://api.imgflip.com/caption_image) for the meme generation API.
- OpenCV for image processing.
- TensorFlow and Keras for the emotion detection model.
