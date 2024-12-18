import streamlit as st
import pyaudio
from google.cloud import speech
import io
import threading
import os

# Set the path to Google Cloud credentials
os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = r"C:\Users\Alarm City\Desktop\med\Medical-Notes\config\v-to-t-api-dc497a9c3e43.json"

# Initialize the Google Cloud Speech client
client = speech.SpeechClient()

# Function to get available microphone devices
def list_microphone_devices():
    p = pyaudio.PyAudio()
    devices = []
    for i in range(p.get_device_count()):
        info = p.get_device_info_by_index(i)
        devices.append(f"Device {i}: {info['name']}")
    p.terminate()
    return devices

# Function to record audio from the microphone
def record_audio(stream, frames, buffer_size=1024):
    try:
        while stream.is_active():  # Ensure that the stream is still active
            data = stream.read(buffer_size)
            frames.append(data)
    except Exception as e:
        print(f"Error during recording: {e}")
    return frames

# Function to transcribe audio from the frames
def transcribe_audio(frames):
    audio_data = b''.join(frames)
    audio_stream = io.BytesIO(audio_data)

    # Configure Google Speech API
    audio = speech.RecognitionAudio(content=audio_stream.read())
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
        return "Error during transcription."

    # Extract and return the transcript
    transcript = ""
    for result in response.results:
        transcript += result.alternatives[0].transcript + "\n"
    return transcript

# Streamlit App
st.title("Live Transcription App")

# Display available microphone devices
st.subheader("Select a Microphone")
devices = list_microphone_devices()
device_choice = st.selectbox("Choose Microphone", devices)

# Parse device index
device_index = int(device_choice.split(":")[0].split(" ")[1])

# Start/Stop recording buttons
start_button = st.button("Start Recording")
stop_button = st.button("Stop Recording")

# Area to display the transcript
transcript_display = st.empty()

# Global variables for recording
frames = []
stream = None
recording_thread = None

# PyAudio setup
p = pyaudio.PyAudio()

# Handle start/stop recording
if start_button:
    try:
        # Open audio stream
        stream = p.open(
            format=pyaudio.paInt16,
            channels=1,
            rate=16000,
            input=True,
            input_device_index=device_index,
            frames_per_buffer=1024
        )
        frames = []
        # Start recording in a thread
        recording_thread = threading.Thread(target=record_audio, args=(stream, frames))
        recording_thread.start()
        st.info("Recording started...")
    except Exception as e:
        st.error(f"Error starting recording: {e}")

if stop_button:
    if stream and recording_thread and recording_thread.is_alive():
        # Stop the stream properly
        stream.stop_stream()
        stream.close()
        recording_thread.join()
        st.info("Recording stopped.")

    # Transcribe the recorded audio
    if frames:
        transcript = transcribe_audio(frames)
        transcript_display.text_area("Transcript", transcript, height=300)
    else:
        st.warning("No audio recorded.")

# Clean up resources when Streamlit stops the script
def cleanup():
    if stream:
        stream.stop_stream()
        stream.close()
    p.terminate()

# Call cleanup at the end of the script to ensure proper shutdown
cleanup()
