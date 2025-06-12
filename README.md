# Audio to Text Transcription App

This application was inspired by my friend, who needed a free and reliable tool to convert audio files into text. She struggled to find a suitable application that met her requirements, so I built this app to help her out and make audio transcription accessible to everyone.

This is a Streamlit-based application that transcribes audio files into text using Google Speech Recognition. It supports multiple languages and processes long audio files by splitting them into smaller chunks.

---

## Features
- Upload audio files in formats like `.mp3`, `.wav`, `.m4a`, and `.ogg`.
- Choose transcription language from a dropdown menu.
- Automatic audio conversion to compatible WAV format (16 kHz, mono).
- Handles long audio files by splitting them into smaller chunks.
- Progress bar to track transcription status.
- Download the transcription output as a `.txt` file.

---

## Supported Languages
- English (US)
- Dutch
- English (UK)
- Spanish
- French
- German
- Hindi
- Chinese (Mandarin)
- Arabic
- Turkish

---

## Installation

1. Clone the repository:
   ```bash
   git clone https://github.com/<your-username>/audio-to-text-app.git
   cd audio-to-text-app
   ```

2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

3. Install `ffmpeg`:
   - **Windows**: Follow [this guide](https://ffmpeg.org/download.html).
   - **macOS**: Use Homebrew:
     ```bash
     brew install ffmpeg
     ```
   - **Linux**: Use your package manager, e.g.,
     ```bash
     sudo apt install ffmpeg
     ```

4. Create a `.env` file with your Google API Key:
   ```
   GOOGLE_API_KEY=your-google-api-key
   ```

---

## Usage

1. Run the Streamlit app:
   ```bash
   streamlit run app.py
   ```

2. Open the app in your browser at `http://localhost:8501`.

3. Upload an audio file, select the language, and click the "Transcribe" button.

4. View the transcription and download it as a `.txt` file.

---

## Repository Structure
```
.
├── app.py              # Main Streamlit application
├── requirements.txt    # Python dependencies
├── .env                # Environment variables
├── README.md           # Project documentation
```

---

## License
This project is licensed under the MIT License. See the LICENSE file for details.

---

## Contributing
Contributions are welcome! Feel free to submit a pull request or open an issue.

---

## Acknowledgments
- [Google Speech Recognition](https://cloud.google.com/speech-to-text)
- [Streamlit](https://streamlit.io)
- [pydub](https://github.com/jiaaro/pydub)
- [SpeechRecognition Library](https://pypi.org/project/SpeechRecognition/)
```
