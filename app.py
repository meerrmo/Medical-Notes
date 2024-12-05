import requests
import streamlit as st
from transformers import T5ForConditionalGeneration, T5Tokenizer
from dotenv import load_dotenv
import os

# Load environment variables from the .env file
load_dotenv()

# Retrieve the GitHub API key from environment variables
api_key = os.getenv("GITHUB_API_KEY")

# Function to get GitHub User Data
def get_github_user_data():
    url = "https://api.github.com/user"
    headers = {"Authorization": f"Bearer {api_key}"}
    response = requests.get(url, headers=headers)

    if response.status_code == 200:
        return response.json()
    else:
        return f"Failed to fetch data. Status Code: {response.status_code}"

# Load T5 model and tokenizer (pre-trained model from Hugging Face)
model_name = "t5-small"  # Small and lightweight for free usage
model = T5ForConditionalGeneration.from_pretrained(model_name)
tokenizer = T5Tokenizer.from_pretrained(model_name)

# Function to summarize conversations
def summarize_conversation(conversation):
    try:
        # Preprocess input
        input_text = f"summarize: {conversation}"
        input_ids = tokenizer.encode(input_text, return_tensors="pt", max_length=512, truncation=True)

        # Generate summary
        summary_ids = model.generate(input_ids, max_length=150, min_length=30, length_penalty=2.0, num_beams=4, early_stopping=True)
        summary = tokenizer.decode(summary_ids[0], skip_special_tokens=True)
        return summary
    except Exception as e:
        return f"Error: {str(e)}"

# Streamlit App Interface
st.title("AI Medical Note Generator (Google NLP)")
st.write("This app converts doctor-patient conversations into structured medical notes using Google's free NLP resources.")

# Display GitHub User Info (Optional)
if st.button("Fetch GitHub User Data"):
    github_data = get_github_user_data()
    st.write("### GitHub User Data:")
    st.write(github_data)

# Input text area for conversation
conversation = st.text_area("Enter the conversation here:")

if st.button("Generate Medical Notes"):
    if conversation:
        notes = summarize_conversation(conversation)
        st.write("### Medical Notes:")
        st.write(notes)
    else:
        st.write("Please enter a conversation to process.")
