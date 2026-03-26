import streamlit as st
from google import genai
from google.genai import types

# Pagina configuratie
st.set_page_config(page_title="Gemini Thinking App", page_icon="🧠", layout="wide")

# Styling voor een schone interface
st.markdown("""
    <style>
    .stChatMessage { border-radius: 15px; margin-bottom: 10px; }
    </style>
    """, unsafe_allow_html=True)

st.title("🧠 Gemini 3 Flash: Thinking & Reasoning")
st.caption("Gebruik de nieuwste Gemini modellen via Streamlit en GitHub.")

# --- API KEY CONFIGURATIE ---
# Controleer of de key in Streamlit Secrets staat, anders vraag erom in de sidebar
if "GEMINI_API_KEY" in st.secrets:
    api_key = st.secrets["GEMINI_API_KEY"]
else:
    with st.sidebar:
        api_key = st.text_input("Voer je Gemini API Key in:", type="password")
        st.info("Tip: Voeg je key toe aan Streamlit Secrets om dit veld te verbergen.")

# --- SIDEBAR INSTELLINGEN ---
with st.sidebar:
    st.header("Model Instellingen")
    model_id = st.selectbox(
        "Kies een model:", 
        ["gemini-2.5-flash", "gemini-3.1-pro-preview"],
        index=0
    )
    
    thinking_level = st.select_slider(
        "Thinking Budget (Diepgang):",
        options=["MINIMAL", "LOW", "MEDIUM", "HIGH"],
        value="MEDIUM"
    )
    
    if st.button("Wis Geschiedenis"):
        st.session_state.messages = []
        st.rerun()

# --- CHAT LOGICA ---
if "messages" not in st.session_state:
    st.session_state.messages = []

# Toon eerdere berichten
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# Chat input
if prompt := st.chat_input("Waar kan ik je bij helpen?"):
    if not api_key:
        st.error("Voeg eerst een API-key toe!")
    else:
        # Toon gebruikersbericht
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)

        # Genereer antwoord
        try:
            client = genai.Client(api_key=api_key)
            
            with st.chat_message("assistant"):
                with st.spinner("Aan het nadenken..."):
                    response = client.models.generate_content(
                        model=model_id,
                        contents=prompt,
                        config=types.GenerateContentConfig(
                            thinking_level=thinking_level
                        )
                    )
                    
                    full_response = response.text
                    st.markdown(full_response)
                    
            st.session_state.messages.append({"role": "assistant", "content": full_response})
            
        except Exception as e:
            st.error(f"Er is een fout opgetreden: {e}")
