import streamlit as st
from google import genai
from google.genai import types

st.set_page_config(page_title="Elliot AI - Game Dev Expert", page_icon="🎮", layout="wide")

# --- API KEY ---
if "GEMINI_API_KEY" in st.secrets:
    api_key = st.secrets["GEMINI_API_KEY"]
else:
    api_key = st.sidebar.text_input("Voer je Gemini API Key in:", type="password")

# --- ELLIOT'S SETUP ---
ELLIOT_SYSTEM_PROMPT = "Je bent Elliot AI, een expert in Unity (C#) en Roblox (Luau). Geef altijd code-voorbeelden."

with st.sidebar:
    st.header("Elliot's Instellingen")
    # We gebruiken hier de specifieke Thinking-model naam
    model_id = st.selectbox(
        "Kies Model:", 
        ["gemini-2.0-flash-thinking-preview-01-21", "gemini-2.0-flash"]
    )
    
    # In plaats van HIGH/LOW gebruiken we een numeriek budget (hoeveel tokens mag hij 'denken')
    thinking_budget = st.slider("Thinking Budget (tokens):", 1024, 32768, 4096, step=1024)
    include_thoughts = st.checkbox("Toon Elliot's denkproces", value=True)

# --- CHAT LOGICA ---
if "messages" not in st.session_state:
    st.session_state.messages = []

for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

if prompt := st.chat_input("Vraag Elliot iets over game dev..."):
    if not api_key:
        st.error("Vul je API-key in!")
    else:
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)

        try:
            client = genai.Client(api_key=api_key)
            
            with st.chat_message("assistant", avatar="👨‍💻"):
                with st.spinner("Elliot is aan het rekenen..."):
                    # DE FIX: Gebruik de juiste configuratie-structuur
                    config_params = {
                        "system_instruction": ELLIOT_SYSTEM_PROMPT,
                        "temperature": 0.2
                    }

                    # Alleen thinking_config toevoegen als het model het ondersteunt
                    if "thinking" in model_id:
                        config_params["thinking_config"] = types.ThinkingConfig(
                            include_thoughts=include_thoughts,
                            include_thoughts_in_response=include_thoughts
                        )

                    response = client.models.generate_content(
                        model=model_id,
                        contents=prompt,
                        config=types.GenerateContentConfig(**config_params)
                    )
                    
                    full_response = response.text
                    st.markdown(full_response)
                    
            st.session_state.messages.append({"role": "assistant", "content": full_response})
            
        except Exception as e:
            st.error(f"Fout in Elliot's brein: {e}")
