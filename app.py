import streamlit as st
from dotenv import load_dotenv
import os
from pydub import AudioSegment
import tempfile
import speech_recognition as sr
from concurrent.futures import ThreadPoolExecutor
from deepmultilingualpunctuation import PunctuationModel
import yake
import time

# Load environment variables
load_dotenv()

# Initialize punctuation model and keyword extractor
punct_model = PunctuationModel()
kw_extractor = yake.KeywordExtractor(lan="en", n=2, top=10)

# Functions
def split_audio(audio_path, chunk_length_ms=60000, overlap_ms=2000):
    audio = AudioSegment.from_file(audio_path)
    chunks = []
    for i in range(0, len(audio), chunk_length_ms - overlap_ms):
        start = i
        end = min(i + chunk_length_ms, len(audio))
        chunks.append((start, end, audio[start:end]))
    return chunks

def convert_audio_to_wav(input_path, output_path):
    audio = AudioSegment.from_file(input_path)
    audio = audio.set_frame_rate(16000).set_channels(1)
    audio.export(output_path, format="wav")

def transcribe_chunk(chunk_data, recognizer, language="en-US"):
    start, end, chunk = chunk_data
    with tempfile.NamedTemporaryFile(delete=False, suffix=".wav") as temp_chunk_file:
        chunk.export(temp_chunk_file.name, format="wav")
        with sr.AudioFile(temp_chunk_file.name) as source:
            audio_data = recognizer.record(source)
            try:
                text = recognizer.recognize_google(audio_data, language=language)
                return (start / 1000, end / 1000, text)
            except sr.RequestError:
                return (start / 1000, end / 1000, "[Error: API unavailable or unresponsive]")
            except sr.UnknownValueError:
                return (start / 1000, end / 1000, "[Error: Unable to recognize speech]")

def transcribe_audio_parallel(audio_path, chunk_length_ms=60000, overlap_ms=2000, language="en-US"):
    recognizer = sr.Recognizer()
    chunks = split_audio(audio_path, chunk_length_ms, overlap_ms)
    
    with ThreadPoolExecutor(max_workers=4) as executor:
        results = list(executor.map(lambda chunk: transcribe_chunk(chunk, recognizer, language), chunks))
    
    return results

# Streamlit App UI
st.set_page_config(page_title="Fast Audio Transcriber", layout="centered")
st.title("Fast Audio Transcriber")
st.markdown("Developed by **Mohammad Ayaz Alam**")

# Language selection
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
language_name = st.selectbox("Select language:", list(language_options.keys()))
language = language_options[language_name]

uploaded_file = st.file_uploader("Upload an audio file", type=["mp3", "wav", "m4a", "ogg"])

if uploaded_file:
    with tempfile.NamedTemporaryFile(delete=False, suffix=".wav") as temp_file:
        temp_file.write(uploaded_file.read())
        temp_path = temp_file.name

    try:
        converted_path = temp_path + "_converted.wav"
        convert_audio_to_wav(temp_path, converted_path)
        temp_path = converted_path
        st.audio(uploaded_file)
        st.success("Audio file converted and ready.")
    except Exception as e:
        st.error(f"Error processing audio: {e}")

    if st.button("Transcribe"):
        with st.spinner("Transcribing with multi-threading..."):
            start_time = time.time()
            results = transcribe_audio_parallel(temp_path, language=language)
            full_transcript = " ".join([r[2] for r in results])

            # Punctuate
            punctuated = punct_model.restore_punctuation(full_transcript)

            # Keyword Extraction
            keywords = kw_extractor.extract_keywords(punctuated)

            st.markdown("### \u270F\ufe0f Transcription Output")
            for start, end, text in results:
                st.markdown(f"**[{start:.2f}s - {end:.2f}s]** {text}")

            st.markdown("### \u2728 Punctuated Text")
            st.text_area("Punctuated Transcription", punctuated, height=300)

            st.markdown("### Keywords")
            st.write(", ".join([kw[0] for kw in keywords]))

            st.download_button("Download Transcription", data=punctuated, file_name="transcription.txt", mime="text/plain")
            st.success(f"Transcription completed in {time.time() - start_time:.2f} seconds")
