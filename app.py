import streamlit as st
from transformers import T5ForConditionalGeneration, T5Tokenizer

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

# Input text area
conversation = st.text_area("Enter the conversation here:")

if st.button("Generate Medical Notes"):
    if conversation:
        notes = summarize_conversation(conversation)
        st.write("### Medical Notes:")
        st.write(notes)
    else:
        st.write("Please enter a conversation to process.")
