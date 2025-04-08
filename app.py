import streamlit as st
import pandas as pd
import google.generativeai as genai 

# Set up the Streamlit app layout 
st.title("🐧My Chatbot and Data Analysis App") 
st.subheader("Conversation and Data Analysis") 

# ✅ ดึง API Key จาก secrets
gemini_api_key = st.secrets["gemini_api_key"]

# Initialize the Gemini Model 
model = None 
try:
    genai.configure(api_key=gemini_api_key) 
    model = genai.GenerativeModel("gemini-2.0-flash-lite") 
    st.success("Gemini API Key successfully configured.") 
except Exception as e: 
    st.error(f"An error occurred while setting up the Gemini model: {e}") 

# Initialize session state for storing chat history and data 
if "chat_history" not in st.session_state: 
    st.session_state.chat_history = []  
if "uploaded_data" not in st.session_state: 
    st.session_state.uploaded_data = None  

# Display previous chat history 
for role, message in st.session_state.chat_history: 
    st.chat_message(role).markdown(message) 

# Upload CSV Data
st.subheader("Upload CSV for Analysis") 
uploaded_file = st.file_uploader("Choose a CSV file", type=["csv"]) 
if uploaded_file is not None: 
    try: 
        st.session_state.uploaded_data = pd.read_csv(uploaded_file) 
        st.success("File successfully uploaded and read.") 
        st.write("### Uploaded Data Preview") 
        st.dataframe(st.session_state.uploaded_data.head()) 
    except Exception as e: 
        st.error(f"An error occurred while reading the file: {e}")

# Upload Data Dictionary
st.subheader("Upload Data Dictionary (CSV format)")
uploaded_dict_file = st.file_uploader("Choose a Data Dictionary CSV file", type=["csv"], key="dict_csv")
if uploaded_dict_file is not None:
    try:
        data_dict_df = pd.read_csv(uploaded_dict_file)
        st.success("Data dictionary file successfully uploaded and read.")
        st.write("### Data Dictionary Preview")
        st.dataframe(data_dict_df.head())
        st.session_state.data_dictionary = data_dict_df
    except Exception as e:
        st.error(f"An error occurred while reading the data dictionary file: {e}")

# Enable AI Analysis
analyze_data_checkbox = st.checkbox("Analyze CSV Data with AI")

# Chat Input and AI Response
if user_input := st.chat_input("Type your message here..."):
    st.session_state.chat_history.append(("user", user_input))
    st.chat_message("user").markdown(user_input)

    if model:
        try:
            if st.session_state.uploaded_data is not None and analyze_data_checkbox:
                if "analyze" in user_input.lower() or "insight" in user_input.lower():
                    data_description = st.session_state.uploaded_data.describe().to_string()
                    prompt = f"Analyze the following dataset and provide insights:\n\n{data_description}"
                    response = model.generate_content(prompt)
                    bot_response = response.text
                else:
                    response = model.generate_content(user_input)
                    bot_response = response.text
            elif not analyze_data_checkbox:
                bot_response = "Data analysis is disabled. Please select the 'Analyze CSV Data with AI' checkbox to enable analysis."
            else:
                bot_response = "Please upload a CSV file first, then ask me to analyze it."

            st.session_state.chat_history.append(("assistant", bot_response))
            st.chat_message("assistant").markdown(bot_response)
        except Exception as e:
            st.error(f"An error occurred while generating the response: {e}")
    else:
        st.warning("Please configure the Gemini API Key to enable chat responses.")
