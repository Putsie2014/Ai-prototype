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
Geef altijd werkende code-voorbeelden en leg complexe concepten simpel uit. Houd je antwoorden efficiënt."""

with st.sidebar:
    st.header("Elliot's Instellingen")
    
    # FIX: 1.5-flash bovenaan gezet omdat deze wereldwijd wél een ruime Free Tier heeft
    model_id = st.selectbox(
        "Kies Model:", 
        [
            "gemini-1.5-flash", # Veiligste keuze (Gratis limiet)
            "gemini-1.5-pro",   # Slimmer, maar strengere limiet
            "gemini-2.0-flash-thinking-exp-01-21", # Let op: 0-limiet op gratis tier zonder billing!
            "gemini-2.0-flash"  # Let op: Vaak 0-limiet in de EU
        ],
        index=0 # Standaard op 1.5-flash
    )
    
    if st.button("Reset Chat"):
        st.session_state.messages = []
        st.rerun()

# --- CHAT GESCHIEDENIS ---
if "messages" not in st.session_state:
    st.session_state.messages = []

for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        if "thought" in msg and msg["thought"]:
            with st.expander("Bekijk denkproces"):
                st.write(msg["thought"])
        st.markdown(msg["content"])

# --- CHAT INPUT & LOGICA ---
if prompt := st.chat_input("Vraag Elliot iets over game dev..."):
    if not api_key:
        st.error("Vul je API-key in via het menu links!")
    else:
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)

        try:
            client = genai.Client(api_key=api_key)
            
            with st.chat_message("assistant", avatar="👨‍💻"):
                with st.spinner("Elliot schrijft code..."):
                    
                    config_args = {
                        "system_instruction": ELLIOT_SYSTEM_PROMPT,
                        "temperature": 0.2
                    }

                    # Alleen thinking aanzetten als het echt een thinking model is
                    if "thinking" in model_id:
                        config_args["thinking_config"] = types.ThinkingConfig(
                            include_thoughts=True
                        )

                    response = client.models.generate_content(
                        model=model_id,
                        contents=prompt,
                        config=types.GenerateContentConfig(**config_args)
                    )
                    
                    thought_process = getattr(response, 'thought', None)
                    final_text = response.text

                    if thought_process:
                        with st.expander("🤔 Elliot's Gedachtegang", expanded=False):
                            st.info(thought_process)
                    
                    st.markdown(final_text)
                    
            st.session_state.messages.append({
                "role": "assistant", 
                "content": final_text, 
                "thought": thought_process
            })
            
        except Exception as e:
            error_msg = str(e)
            # FIX: Vangt de 'uitgeput' foutmelding op en geeft direct de oplossing
            if "429" in error_msg or "RESOURCE_EXHAUSTED" in error_msg:
                st.error("⚠️ **Quota Bereikt (429 Error)**\n\nGoogle blokkeert dit verzoek omdat de limiet van dit specifieke model is bereikt (of op 0 staat in jouw regio). \n\n**Oplossing:** Selecteer `gemini-1.5-flash` in het menu links en probeer het nog een keer!")
            else:
                st.error(f"Er is iets misgegaan: {error_msg}")
