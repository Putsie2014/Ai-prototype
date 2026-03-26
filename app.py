import streamlit as st
from google import genai
from google.genai import types

# Pagina configuratie voor een tech-look
st.set_page_config(page_title="Elliot AI - Game Dev Expert", page_icon="🎮", layout="wide")

# Custom CSS voor een 'Dark Mode' game-dev vibe
st.markdown("""
    <style>
    .stApp { background-color: #0e1117; color: #ffffff; }
    .stChatMessage { border-radius: 10px; border: 1px solid #383d47; }
    </style>
    """, unsafe_allow_html=True)

st.title("👨‍💻 Elliot AI")
st.caption("Jouw gespecialiseerde expert voor Unity (C#), Roblox Studio (Luau) en algemene game-logica.")

# --- API KEY CONFIGURATIE ---
if "GEMINI_API_KEY" in st.secrets:
    api_key = st.secrets["GEMINI_API_KEY"]
else:
    with st.sidebar:
        api_key = st.text_input("Voer je Gemini API Key in:", type="password")
        st.info("Tip: Voeg je key toe aan Streamlit Secrets op GitHub.")

# --- ELLIOT'S PERSOONLIJKHEID (System Instruction) ---
ELLIOT_SYSTEM_PROMPT = """
Je bent 'Elliot AI', een wereldklasse expert in game development. 
Je specialisaties zijn:
1. Unity (C#): Je schrijft efficiënte scripts, legt uit hoe componenten werken en helpt met debugging.
2. Roblox Studio (Luau): Je bent een expert in DataStores, RemoteEvents en geoptimaliseerde server-client communicatie.
3. Wiskunde voor games: Vectoren, raycasting en quaternions leg je simpel uit.

Stijlregels:
- Antwoord altijd met concrete code-voorbeelden.
- Gebruik 'Clean Code' principes.
- Als je code schrijft voor Roblox, gebruik dan Luau. Voor Unity gebruik je C#.
- Wees kortaf maar behulpzaam, zoals een ervaren lead developer.
"""

with st.sidebar:
    st.header("Elliot's Brein")
    model_id = "gemini-2.5-flash" # Flash is perfect voor snelle code-suggesties
    
    thinking_level = st.select_slider(
        "Complexiteit van logica:",
        options=["MINIMAL", "LOW", "MEDIUM", "HIGH"],
        value="HIGH" # Voor code willen we diepe logica
    )
    
    if st.button("Reset Sessie"):
        st.session_state.messages = []
        st.rerun()

# --- CHAT LOGICA ---
if "messages" not in st.session_state:
    st.session_state.messages = []

# Toon geschiedenis
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# Chat input
if prompt := st.chat_input("Vraag Elliot om een script of debug hulp..."):
    if not api_key:
        st.error("Elliot heeft een API-key nodig om na te denken!")
    else:
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)

        try:
            client = genai.Client(api_key=api_key)
            
            with st.chat_message("assistant", avatar="👨‍💻"):
                with st.spinner("Elliot schrijft code..."):
                    # Hier voegen we de Systeemprompt samen met de gebruikersvraag
                    response = client.models.generate_content(
                        model=model_id,
                        contents=[ELLIOT_SYSTEM_PROMPT, prompt],
                        config=types.GenerateContentConfig(
                            thinking_level=thinking_level,
                            temperature=0.2 # Lager is beter voor accurate code
                        )
                    )
                    
                    full_response = response.text
                    st.markdown(full_response)
                    
            st.session_state.messages.append({"role": "assistant", "content": full_response})
            
        except Exception as e:
            st.error(f"Fout in Elliot's brein: {e}")
