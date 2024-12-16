import streamlit as st
import pyaudio
import wave
from google.cloud import speech
import io
import threading
import os

# Ensure credentials are set
if not os.getenv('GOOGLE_APPLICATION_CREDENTIALS'):
    st.error("Google Cloud credentials not found. Set the environment variable GOOGLE_APPLICATION_CREDENTIALS.")
    st.stop()

# Set up the Google Cloud Speech client
client = speech.SpeechClient()

# Select the correct microphone device index (change this to the device you want)
selected_device_index = 1  # Use the correct index for the microphone you want (from the list you posted)

# Function to get the available microphone devices
def list_microphone_devices():
    p = pyaudio.PyAudio()
    devices = []
    for i in range(p.get_device_count()):
        info = p.get_device_info_by_index(i)
        devices.append(f"Device {i}: {info['name']}")
    return devices

# Function to record audio from the microphone
def record_audio(stream, buffer_size=1024):
    frames = []
    try:
        while True:
            data = stream.read(buffer_size)
            frames.append(data)
    except Exception as e:
        print(f"Error during recording: {e}")
    return frames

# Function to transcribe audio from microphone
def transcribe_audio(frames):
    audio = b''.join(frames)
    audio_stream = io.BytesIO(audio)

    audio_content = audio_stream.read()

    # Configure Google Speech API
    audio = speech.RecognitionAudio(content=audio_content)
    config = speech.RecognitionConfig(
        encoding=speech.RecognitionConfig.AudioEncoding.LINEAR16,
        sample_rate_hertz=16000,
        language_code="en-US",
    )

    # Perform speech recognition
    try:
        response = client.recognize(config=config, audio=audio)
    except Exception as e:
        print(f"Error during transcription: {e}")
        return "Error during transcription"
    
    # Process the response and display the transcript
    transcript = ""
    for result in response.results:
        transcript += result.alternatives[0].transcript + "\n"
    return transcript

# Streamlit App
st.title("Live Transcription App")

# Show available devices
devices = list_microphone_devices()
device_choice = st.selectbox("Choose Microphone", devices)

# Get the device index
device_index = int(device_choice.split(":")[0].split(" ")[1])

# Start/Stop recording functionality
start_button = st.button("Start Recording")
stop_button = st.button("Stop Recording")

# Transcription display
transcript_display = st.empty()

# Global variables to handle stream
frames = []
stream = None
recording_thread = None

# Handle start/stop recording
if start_button:
    try:
        p = pyaudio.PyAudio()
        stream = p.open(format=pyaudio.paInt16,
                        channels=1,
                        rate=16000,
                        input=True,
                        input_device_index=device_index,
                        frames_per_buffer=1024)
        
        # Start a background thread to record audio
        frames = []
        recording_thread = threading.Thread(target=record_audio, args=(stream,))
        recording_thread.start()
        st.info("Recording started...")
    except Exception as e:
        st.error(f"Error starting recording: {e}")

if stop_button:
    if recording_thread and recording_thread.is_alive():
        stream.stop_stream()
        stream.close()
        recording_thread.join()
        st.info("Recording stopped.")

    # Transcribe recorded audio
    if frames:
        transcript = transcribe_audio(frames)
        transcript_display.text_area("Transcript", transcript, height=300)
