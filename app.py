import streamlit as st
import openai
import os
from google_speech import Speech
import speech_recognition as sr
from transformers import pipeline

# Ensure API key is set up correctly in the environment
openai.api_key = os.getenv('OPENAI_API_KEY')  # Use environment variable for security

# Initialize the transformer model for summarization
summarizer = pipeline("summarization")

# Function to transcribe speech to text
def transcribe_audio():
    r = sr.Recognizer()
    with sr.Microphone() as source:
        st.write("Listening for speech...")
        audio = r.listen(source)
    try:
        st.write("Recognizing speech...")
        text = r.recognize_google(audio)
        st.write(f"Recognized text: {text}")
        return text
    except sr.UnknownValueError:
        st.write("Sorry, I could not understand the audio.")
        return None
    except sr.RequestError:
        st.write("Sorry, there was an error with the speech recognition service.")
        return None

# Function to generate medical notes from conversation
def generate_medical_notes(conversation):
    prompt = f"Summarize this doctor-patient conversation into medical notes: {conversation}"
    response = openai.Completion.create(
        model="text-davinci-003",
        prompt=prompt,
        max_tokens=200
    )
    return response.choices[0].text.strip()

# Streamlit App Interface
st.title('AI Medical Note Generator')
st.write('This app converts doctor-patient interactions into medical notes.')

# Option for speech-to-text or text input
option = st.radio('Select input type:', ['Text', 'Speech'])

if option == 'Text':
    conversation = st.text_area('Enter conversation here:')
    if st.button('Generate Medical Notes'):
        if conversation:
            notes = generate_medical_notes(conversation)
            st.write("### Medical Notes:")
            st.write(notes)
        else:
            st.write("Please enter a conversation.")

elif option == 'Speech':
    if st.button('Start Recording'):
        conversation = transcribe_audio()
        if conversation:
            notes = generate_medical_notes(conversation)
            st.write("### Medical Notes:")
            st.write(notes)

# To run the app:
# streamlit run app.py
