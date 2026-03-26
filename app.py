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
ELLIOT_SYSTEM_PROMPT = """Je bent Elliot AI, een expert in Unity (C#) en Roblox (Luau). 
Geef altijd werkende code-voorbeelden en leg complexe concepten simpel uit."""

with st.sidebar:
    st.header("Elliot's Instellingen")
    # Zorg dat je een model kiest dat 'thinking' ondersteunt
    model_id = st.selectbox(
        "Kies Model:", 
        ["gemini-2.0-flash-thinking-preview-01-21", "gemini-2.0-flash"]
    )
    
    include_thoughts = st.checkbox("Toon Elliot's denkproces", value=True)
    
    if st.button("Reset Chat"):
        st.session_state.messages = []
        st.rerun()

# --- CHAT GESCHIEDENIS ---
if "messages" not in st.session_state:
    st.session_state.messages = []

for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        # Als er gedachten zijn opgeslagen, toon ze in een expander
        if "thought" in msg and msg["thought"]:
            with st.expander("Bekijk denkproces"):
                st.write(msg["thought"])
        st.markdown(msg["content"])

# --- CHAT INPUT & LOGICA ---
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
                with st.spinner("Elliot analyseert de code..."):
                    
                    # Configuratie opbouwen
                    config_args = {
                        "system_instruction": ELLIOT_SYSTEM_PROMPT,
                        "temperature": 0.2
                    }

                    # Alleen thinking_config toevoegen als het model 'thinking' in de naam heeft
                    if "thinking" in model_id:
                        config_args["thinking_config"] = types.ThinkingConfig(
                            include_thoughts=include_thoughts
                        )

                    response = client.models.generate_content(
                        model=model_id,
                        contents=prompt,
                        config=types.GenerateContentConfig(**config_args)
                    )
                    
                    # Haal de gedachten en de tekst op
                    thought_process = getattr(response, 'thought', None)
                    final_text = response.text

                    # Toon gedachten in een mooie UI
                    if thought_process and include_thoughts:
                        with st.expander("🤔 Elliot's Gedachtegang", expanded=False):
                            st.info(thought_process)
                    
                    st.markdown(final_text)
                    
            # Sla op in geschiedenis
            st.session_state.messages.append({
                "role": "assistant", 
                "content": final_text, 
                "thought": thought_process
            })
            
        except Exception as e:
            st.error(f"Fout in Elliot's brein: {e}")
