import streamlit as st
from dotenv import load_dotenv
import os
from pydub import AudioSegment
import tempfile
import speech_recognition as sr
import concurrent.futures

# Load environment variables
load_dotenv()

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

def transcribe_chunk_indexed(indexed_chunk_language):
    """Helper for multiprocessing - receives tuple of (index, chunk, language)."""
    index, chunk, language = indexed_chunk_language
    recognizer = sr.Recognizer()
    try:
        with tempfile.NamedTemporaryFile(delete=False, suffix=".wav") as temp_chunk_file:
            chunk.export(temp_chunk_file.name, format="wav")
            with sr.AudioFile(temp_chunk_file.name) as source:
                audio_data = recognizer.record(source)
                text = recognizer.recognize_google(audio_data, language=language)
        os.remove(temp_chunk_file.name)
        return index, text
    except sr.RequestError:
        return index, "[Error: API unavailable or unresponsive]"
    except sr.UnknownValueError:
        return index, "[Error: Unable to recognize speech]"
    except Exception as e:
        return index, f"[Error: {str(e)}]"

def transcribe_audio_with_google_parallel(audio_path, chunk_length_ms=60000, overlap_ms=2000, language="en-US"):
    """Parallel transcription using threading to speed up the process."""
    chunks = split_audio(audio_path, chunk_length_ms, overlap_ms)
    indexed_chunks = [(i, chunk, language) for i, chunk in enumerate(chunks)]
    
    transcription = [""] * len(indexed_chunks)

    with concurrent.futures.ThreadPoolExecutor(max_workers=4) as executor:
        futures = {executor.submit(transcribe_chunk_indexed, ic): ic[0] for ic in indexed_chunks}

        progress_bar = st.progress(0)
        completed = 0

        for future in concurrent.futures.as_completed(futures):
            idx, text = future.result()
            transcription[idx] = text
            completed += 1
            progress_bar.progress(completed / len(indexed_chunks))

    return " ".join(transcription)

# Streamlit UI
st.title("Lina's Audio to Text Transcription")
st.text("       - Developed By: Mohammad Ayaz Alam")
st.write("Upload an audio file, and we'll transcribe it into text using chunk processing.")

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
        st.success("Audio file successfully processed!")
    except Exception as e:
        st.error(f"Error processing audio: {e}")

    if st.button("Transcribe"):
        with st.spinner("Transcribing (parallel)..."):
            transcription = transcribe_audio_with_google_parallel(temp_path, chunk_length_ms=60000, overlap_ms=2000, language=language)
            st.write("### Transcription")
            st.text_area("Transcription Output", transcription, height=300)

            st.download_button(
                label="Download Transcription",
                data=transcription,
                file_name="transcription.txt",
                mime="text/plain",
            )
