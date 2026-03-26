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
    
    # We gebruiken nu de nieuwste, officiële modelnamen
    model_id = st.selectbox(
        "Kies Model:", 
        [
            "gemini-2.5-flash",       # Snel en efficiënt voor code
            "gemini-3.1-pro-preview", # Het krachtigste model van dit moment
            "gemini-2.5-pro"
        ],
        index=0
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
if prompt := st.chat_input("Vraag Elliot iets over Unity of Roblox..."):
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

                    # Thinking logica
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
            
            # Slimme foutafhandeling in de chat
            if "404" in error_msg or "NOT_FOUND" in error_msg:
                st.error(f"⚠️ **Model niet gevonden (404 Error)**\n\nGoogle herkent het model `{model_id}` niet. Waarschijnlijk hebben ze de naam geüpdatet. Check Google AI Studio voor de exacte, huidige namen.")
            elif "429" in error_msg or "RESOURCE_EXHAUSTED" in error_msg:
                st.warning("🛑 **Quota Bereikt of Geblokkeerd (429 Error)**\n\nGoogle weigert dit model uit te voeren. **Belangrijk voor Europese gebruikers:** Om de nieuwste modellen (zoals de 2.5 en 3.0 series) gratis te gebruiken, vereist Google AI Studio vaak dat je een betaalprofiel koppelt ter verificatie, zelfs als je onder de gratis limiet blijft. \n\n*Probeer een ander model in de sidebar of check je limieten op aistudio.google.com.*")
            else:
                st.error(f"Er is iets misgegaan: {error_msg}")
