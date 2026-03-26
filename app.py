import streamlit as st
import tempfile
from PIL import Image
from google import genai
from google.genai import types
from gradio_client import Client, handle_file
from huggingface_hub import InferenceClient

st.set_page_config(page_title="Elliot AI - Game Dev Expert", page_icon="🎮", layout="wide")

# ==========================================
# 1. ELLIOT SETUP & MENU
# ==========================================
gemini_api_key = st.secrets.get("GEMINI_API_KEY", "")
hf_token = st.secrets.get("HF_TOKEN", "")

ELLIOT_SYSTEM_PROMPT = """Je bent Elliot AI, een expert in Unity (C#) en Roblox (Luau). 
Geef altijd werkende code-voorbeelden en leg complexe concepten simpel uit. Houd je antwoorden efficiënt."""

with st.sidebar:
    st.header("⚙️ Elliot's Dashboard")
    
    if not gemini_api_key:
        gemini_api_key = st.text_input("Gemini API Key (Code):", type="password")
    if not hf_token:
        hf_token = st.text_input("Hugging Face Token (Art & 3D):", type="password")
        
    st.divider()
    
    actie_keuze = st.radio(
        "Wat moet Elliot doen?",
        ["Code & Chat (Gemini)", "Concept Art (FLUX)", "3D Meesterwerk (TripoSR)"]
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
        
        # --- OPTIE 1: CODE & CHAT ---
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

        # --- OPTIE 2: CONCEPT ART ---
        elif actie_keuze == "Concept Art (FLUX)":
            if not hf_token:
                st.error("Vul je Hugging Face token in de sidebar in!")
            else:
                with st.spinner("Elliot rendert een high-res design met FLUX... 🎨"):
                    try:
                        hf_client = InferenceClient(model="black-forest-labs/FLUX.1-schnell", token=hf_token)
                        image = hf_client.text_to_image(f"{prompt}, high quality game asset, masterpiece, ultra detailed")
                        st.image(image)
                        st.session_state.messages.append({"role": "assistant", "content": "*Concept art gegenereerd.*", "image": image})
                    except Exception as e:
                        st.error(f"Fout bij tekenen: {e}")

        # --- OPTIE 3: 3D MEESTERWERK (FLUX + TripoSR) ---
        elif actie_keuze == "3D Meesterwerk (TripoSR)":
            if not hf_token:
                st.error("Je hebt je Hugging Face token nodig voor deze magie!")
            else:
                try:
                    # STAP 1: FLUX maakt de blauwdruk
                    with st.spinner("Stap 1: FLUX tekent een perfecte blauwdruk... 🎨"):
                        hf_client = InferenceClient(model="black-forest-labs/FLUX.1-schnell", token=hf_token)
                        strakke_prompt = f"A perfect 3D render of {prompt}, isolated on a pure white background, masterpiece game asset, simple clear shapes"
                        
                        image = hf_client.text_to_image(strakke_prompt)
                        st.image(image, caption="Basis Blueprint (FLUX)")
                        
                        # Sla tijdelijk op
                        with tempfile.NamedTemporaryFile(delete=False, suffix=".png") as tmp_file:
                            image.save(tmp_file, format="PNG")
                            tijdelijk_pad = tmp_file.name

                    # STAP 2: Gradio stuurt het naar TripoSR
                    with st.spinner("Stap 2: TripoSR smeedt de 3D mesh (Dit gaat supersnel!)... ⚡"):
                        try:
                            # We stappen over naar de veel stabielere TripoSR Space
                            space_client = Client("stabilityai/TripoSR")
                            
                            # TripoSR heeft meestal genoeg aan 1 predict call die alles doet
                            final_result = space_client.predict(
                                image_in=handle_file(tijdelijk_pad),
                                do_remove_background=True,
                                foreground_ratio=0.85,
                                api_name="/process" # De standaard API naam voor TripoSR
                            )
                            
                            # Resultaat is vaak een pad naar een .obj of .glb
                            glb_pad = final_result[1] if isinstance(final_result, tuple) else final_result
                            
                            with open(glb_pad, "rb") as f:
                                mesh_data = f.read()
                                
                            st.success("Meesterwerk voltooid! 🎉")
                            st.download_button("📥 Download 3D Bestand", mesh_data, "tripo_meesterwerk.glb")
                            
                        except Exception as space_err:
                            st.error(f"Ook deze 3D server ligt er helaas uit: {space_err}")
                            st.warning("Ultimate Backup: Sla de blauwdruk (hierboven) op met rechtermuisknop en upload hem gratis op: huggingface.co/spaces/stabilityai/TripoSR")
                            
                except Exception as e:
                    st.error(f"Fout tijdens het proces: {e}")
