import streamlit as st
from google import genai
from google.genai import types
from huggingface_hub import InferenceClient
import requests

st.set_page_config(page_title="Elliot AI - Game Dev Expert", page_icon="🎮", layout="wide")

# --- VEILIGE API KEYS (SECRETS) ---
# We halen ze uit st.secrets, of we vragen erom via de sidebar als ze ontbreken.
gemini_api_key = st.secrets.get("GEMINI_API_KEY", "")
hf_token = st.secrets.get("HF_TOKEN", "")

# --- ELLIOT'S SETUP ---
ELLIOT_SYSTEM_PROMPT = """Je bent Elliot AI, een expert in Unity (C#) en Roblox (Luau). 
Geef altijd werkende code-voorbeelden en leg complexe concepten simpel uit. Houd je antwoorden efficiënt."""

with st.sidebar:
    st.header("⚙️ Elliot's Instellingen")
    
    if not gemini_api_key:
        gemini_api_key = st.text_input("Voer je Gemini API Key in:", type="password")
    if not hf_token:
        hf_token = st.text_input("Voer je Hugging Face Token in:", type="password")
        
    st.divider()
    
    # De Master-Keuzelijst
    actie_keuze = st.radio(
        "Wat moet Elliot doen?",
        ["Code & Chat (Gemini)", "Concept Art (Nano Banana 2)", "3D Preview (Shap-E)"]
    )
    
    if st.button("🗑️ Reset Chat"):
        st.session_state.messages = []
        st.rerun()

# --- CHAT GESCHIEDENIS ---
if "messages" not in st.session_state:
    st.session_state.messages = []

# Teken alle oude berichten opnieuw op het scherm
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])
        if "thought" in msg and msg["thought"]:
            with st.expander("🤔 Bekijk denkproces"):
                st.write(msg["thought"])
        if "image" in msg and msg["image"]:
            st.image(msg["image"])

# --- CHAT INPUT & LOGICA ---
if prompt := st.chat_input("Vraag om code, een texture, of een 3D-model..."):
    
    # 1. Toon het bericht van de gebruiker
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    # 2. Reageer als Assistant
    with st.chat_message("assistant", avatar="👨‍💻"):
        
        # --- OPTIE 1: CODE & CHAT ---
        if actie_keuze == "Code & Chat (Gemini)":
            if not gemini_api_key:
                st.error("Je hebt een Gemini API key nodig voor deze functie!")
            else:
                with st.spinner("Elliot schrijft code... ⌨️"):
                    try:
                        client = genai.Client(api_key=gemini_api_key)
                        response = client.models.generate_content(
                            model="gemini-2.5-flash",
                            contents=prompt,
                            config=types.GenerateContentConfig(
                                system_instruction=ELLIOT_SYSTEM_PROMPT,
                                temperature=0.2
                            )
                        )
                        st.markdown(response.text)
                        st.session_state.messages.append({
                            "role": "assistant", 
                            "content": response.text
                        })
                    except Exception as e:
                        st.error(f"Fout bij code genereren: {e}")

        # --- OPTIE 2: CONCEPT ART (NANO BANANA 2) ---
        elif actie_keuze == "Concept Art (Nano Banana 2)":
            if not gemini_api_key:
                st.error("Je hebt een Gemini API key nodig voor deze functie!")
            else:
                with st.spinner("Elliot tekent game assets... 🎨"):
                    try:
                        client = genai.Client(api_key=gemini_api_key)
                        response = client.models.generate_images(
                            model="gemini-3-flash-image",
                            prompt=prompt,
                            config=types.GenerateImagesConfig(number_of_images=1, output_mime_type="image/jpeg")
                        )
                        image_bytes = response.generated_images[0].image.image_bytes
                        st.image(image_bytes)
                        st.markdown("*Concept art klaar voor gebruik!*")
                        
                        st.session_state.messages.append({
                            "role": "assistant", 
                            "content": "*Concept art gegenereerd.*",
                            "image": image_bytes
                        })
                    except Exception as e:
                        st.error(f"Fout bij afbeelding genereren: {e}")

# --- OPTIE 3: 3D MODEL VIA HUGGING FACE SPACES (GRADIO) ---
        elif actie_keuze == "3D Preview (Shap-E)":
            with st.spinner("Elliot omzeilt de limieten via Hugging Face Spaces... 🔨"):
                try:
                    from gradio_client import Client
                    
                    # We maken stiekem verbinding met de publieke Shap-E app op Hugging Face
                    client = Client("hysts/Shap-E")
                    
                    # We roepen de text-to-3d functie van de app aan
                    result_path = client.predict(
                        prompt=prompt,
                        seed=0,
                        guidance_scale=15.0,
                        num_inference_steps=64,
                        api_name="/text-to-3d"
                    )
                    
                    # De Space geeft een bestandspad terug naar de .glb file
                    with open(result_path, "rb") as file:
                        model_bytes = file.read()
                        
                    st.success("Gelukt! Je gratis 3D-bestand is binnengehaald.")
                    st.download_button(
                        label="📥 Download .GLB Bestand voor Unity/Roblox",
                        data=model_bytes,
                        file_name="elliot_3d_model.glb",
                        mime="model/gltf-binary"
                    )
                    
                    st.session_state.messages.append({
                        "role": "assistant", 
                        "content": f"*3D model gegenereerd voor: '{prompt}'. Gebruik de downloadknop!*"
                    })
                except Exception as e:
                    st.error(f"Helaas, de openbare server is momenteel overbelast of slaapt: {e}")
