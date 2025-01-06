import streamlit as st
from google.generativeai import configure, GenerativeModel
from dotenv import load_dotenv
import os
from pydub import AudioSegment
import tempfile
import speech_recognition as sr

# Load environment variables
load_dotenv()
configure(api_key=os.getenv("GOOGLE_API_KEY"))

# Initialize Gemini model (optional for post-processing)
model = GenerativeModel("gemini-1.5-flash")

def split_audio(audio_path, chunk_length_ms=60000, overlap_ms=2000):
    """Split audio into smaller chunks with overlap."""
    audio = AudioSegment.from_file(audio_path)
    chunks = []
    for i in range(0, len(audio), chunk_length_ms - overlap_ms):
        chunks.append(audio[i:i + chunk_length_ms])
    return chunks

def convert_audio_to_wav(input_path, output_path):
    """Convert audio to 16 kHz, mono WAV."""
    audio = AudioSegment.from_file(input_path)
    audio = audio.set_frame_rate(16000).set_channels(1)
    audio.export(output_path, format="wav")

def transcribe_chunk(chunk, recognizer, language="en-US"):
    """Transcribe a single chunk of audio."""
    if not isinstance(language, str):
        raise ValueError(f"Invalid language parameter: {language}")

    with tempfile.NamedTemporaryFile(delete=False, suffix=".wav") as temp_chunk_file:
        chunk.export(temp_chunk_file.name, format="wav")
        with sr.AudioFile(temp_chunk_file.name) as source:
            audio_data = recognizer.record(source)
            try:
                # Pass language to Google Speech API
                return recognizer.recognize_google(audio_data, language=language)
            except sr.RequestError:
                return "[Error: API unavailable or unresponsive]"
            except sr.UnknownValueError:
                return "[Error: Unable to recognize speech]"

def transcribe_audio_with_google(audio_path, chunk_length_ms=60000, overlap_ms=2000, language="en-US"):
    """Transcribe a long audio file by splitting it into smaller chunks."""
    recognizer = sr.Recognizer()
    chunks = split_audio(audio_path, chunk_length_ms, overlap_ms)
    transcription = []

    progress_bar = st.progress(0)
    for idx, chunk in enumerate(chunks):
        #st.write(f"Transcribing chunk {idx + 1}/{len(chunks)}...")
        text = transcribe_chunk(chunk, recognizer, language=language)
        transcription.append(text)
        progress_bar.progress((idx + 1) / len(chunks))

    return " ".join(transcription)

# Streamlit UI
st.title("Lina's Audio to Text Transcription")
st.write("Upload an audio file, and we'll transcribe it into text using chunk processing.")

# Dropdown for language selection
language_options = {
    "English (US)": "en-US",
    "Dutch": "nl-NL",
    "English (UK)": "en-GB",
    "Spanish": "es-ES",
    "French": "fr-FR",
    "German": "de-DE",
    "Hindi": "hi-IN",
    "Chinese (Mandarin)": "zh-CN",
    "Arabic": "ar-SA",
}
language_name = st.selectbox("Select the language for transcription:", list(language_options.keys()))
language = language_options.get(language_name)
st.write(f"Selected language: {language} (from {language_name})")

# File uploader
uploaded_file = st.file_uploader("Upload an audio file", type=["mp3", "wav", "m4a", "ogg"])

if uploaded_file:
    # Save uploaded file temporarily
    with tempfile.NamedTemporaryFile(delete=False, suffix=".wav") as temp_file:
        temp_file.write(uploaded_file.read())
        temp_path = temp_file.name

    # Convert audio file to compatible WAV
    try:
        converted_path = temp_path + "_converted.wav"
        convert_audio_to_wav(temp_path, converted_path)
        temp_path = converted_path
        st.audio(uploaded_file)
        st.success("Audio file successfully processed!")
    except Exception as e:
        st.error(f"Error processing audio: {e}")

    # Transcribe the audio file
    if st.button("Transcribe"):
        with st.spinner("Transcribing..."):
            transcription = transcribe_audio_with_google(temp_path, chunk_length_ms=60000, overlap_ms=2000, language=language)
            st.write("### Transcription")
            st.text_area("Transcription Output", transcription, height=300)

            # Download transcription
            st.download_button(
                label="Download Transcription",
                data=transcription,
                file_name="transcription.txt",
                mime="text/plain",
            )
