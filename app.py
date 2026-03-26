import streamlit as st
import tempfile
import urllib.parse
import urllib.request
from google import genai
from google.genai import types
from gradio_client import Client, handle_file

st.set_page_config(page_title="Elliot AI - Game Dev Expert", page_icon="🎮", layout="wide")

# ==========================================
# 1. ELLIOT SETUP & MENU
# ==========================================
gemini_api_key = st.secrets.get("GEMINI_API_KEY", "")

ELLIOT_SYSTEM_PROMPT = """Je bent Elliot AI, een expert in Unity (C#) en Roblox (Luau). 
Geef altijd werkende code-voorbeelden en leg complexe concepten simpel uit. Houd je antwoorden efficiënt."""

with st.sidebar:
    st.header("⚙️ Elliot's Dashboard")
    
    if not gemini_api_key:
        gemini_api_key = st.text_input("Voer je Gemini API Key in (Voor Code):", type="password")
        
    st.divider()
    
    actie_keuze = st.radio(
        "Wat moet Elliot doen?",
        ["Code & Chat (Gemini)", "Concept Art (Gratis AI)", "3D Meesterwerk (InstantMesh)"]
    )
    
    if st.button("🗑️ Reset Chat"):
        st.session_state.messages = []
        st.rerun()

# ==========================================
# 2. CHAT GESCHIEDENIS
# ==========================================
if "messages" not in st.session_state:
    st.session_state.messages = []

for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])
        if "thought" in msg and msg["thought"]:
            with st.expander("🤔 Bekijk denkproces"):
                st.write(msg["thought"])
        if "image" in msg and msg["image"]:
            st.image(msg["image"])

# ==========================================
# 3. CHAT INPUT & LOGICA
# ==========================================
if prompt := st.chat_input("Wat gaan we vandaag bouwen?"):
    
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant", avatar="👨‍💻"):
        
        # --- OPTIE 1: CODE & CHAT (Blijft Gemini) ---
        if actie_keuze == "Code & Chat (Gemini)":
            if not gemini_api_key:
                st.error("Je hebt een Gemini API key nodig voor code!")
            else:
                with st.spinner("Elliot schrijft code... ⌨️"):
                    try:
                        client = genai.Client(api_key=gemini_api_key)
                        response = client.models.generate_content(
                            model="gemini-2.5-flash",
                            contents=prompt,
                            config=types.GenerateContentConfig(system_instruction=ELLIOT_SYSTEM_PROMPT)
                        )
                        st.markdown(response.text)
                        st.session_state.messages.append({"role": "assistant", "content": response.text})
                    except Exception as e:
                        st.error(f"Fout: {e}")

        # --- OPTIE 2: CONCEPT ART (Pollinations - 100% Gratis) ---
        elif actie_keuze == "Concept Art (Gratis AI)":
            with st.spinner("Elliot omzeilt de blokkades en tekent... 🎨"):
                try:
                    # We gebruiken de open Pollinations API, geen key nodig!
                    veilig_prompt = urllib.parse.quote(prompt + ", high quality game asset, masterpiece")
                    image_url = f"https://image.pollinations.ai/prompt/{veilig_prompt}?nologo=true"
                    
                    # Haal de afbeelding op
                    req = urllib.request.Request(image_url, headers={'User-Agent': 'Elliot-Game-App'})
                    with urllib.request.urlopen(req) as response:
                        image_bytes = response.read()
                        
                    st.image(image_bytes)
                    st.session_state.messages.append({"role": "assistant", "content": "*Concept art gegenereerd.*", "image": image_bytes})
                except Exception as e:
                    st.error(f"Fout bij tekenen: {e}")

        # --- OPTIE 3: 3D MEESTERWERK (DE ULTIEME HACKER METHODE) ---
        elif actie_keuze == "3D Meesterwerk (InstantMesh)":
            try:
                # STAP 1: AI tekent een strak plaatje (Via Pollinations)
                with st.spinner("Stap 1: Blauwdruk tekenen (Regio-vrij)... 🎨"):
                    strakke_prompt = f"A perfect 3D render of {prompt}, isolated on a pure white background, masterpiece game asset"
                    veilig_prompt = urllib.parse.quote(strakke_prompt)
                    image_url = f"https://image.pollinations.ai/prompt/{veilig_prompt}?nologo=true"
                    
                    req = urllib.request.Request(image_url, headers={'User-Agent': 'Elliot-Game-App'})
                    with urllib.request.urlopen(req) as response:
                        img_bytes = response.read()
                        
                    st.image(img_bytes, caption="Basis Blueprint")
                    
                    # Sla het plaatje tijdelijk op voor Gradio
                    with tempfile.NamedTemporaryFile(delete=False, suffix=".jpg") as tmp_file:
                        tmp_file.write(img_bytes)
                        tijdelijk_pad = tmp_file.name

                # STAP 2: Stuur het plaatje naar de InstantMesh Space
                with st.spinner("Stap 2: InstantMesh smeedt de 3D mesh (Dit kan 60 seconden duren!)... 🔨"):
                    try:
                        hf_client = Client("TencentARC/InstantMesh")
                        
                        st.info("Achtergrond verwijderen...")
                        processed_img = hf_client.predict(input_image=handle_file(tijdelijk_pad), do_remove_background=True, api_name="/preprocess")
                        
                        st.info("Diepte berekenen...")
                        mvs_images = hf_client.predict(api_name="/generate_mvs")
                        
                        st.info("3D Mesh bouwen...")
                        final_result = hf_client.predict(api_name="/make3d")
                        
                        glb_pad = final_result[2] if isinstance(final_result, tuple) else final_result
                        
                        with open(glb_pad, "rb") as f:
                            mesh_data = f.read()
                            
                        st.success("Meesterwerk voltooid! 🎉")
                        st.download_button("📥 Download .OBJ/.GLB", mesh_data, "game_meesterwerk.glb")
                        
                    except Exception as space_err:
                        st.error(f"De gratis Space is momenteel overbelast: {space_err}")
                        st.warning("Hack: Download het plaatje hierboven en sleep het zélf even in: huggingface.co/spaces/TencentARC/InstantMesh")
                        
            except Exception as e:
                st.error(f"Fout tijdens het proces: {e}")
