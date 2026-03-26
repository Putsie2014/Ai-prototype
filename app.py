import streamlit as st
import tempfile
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
        gemini_api_key = st.text_input("Voer je Gemini API Key in:", type="password")
        
    st.divider()
    
    actie_keuze = st.radio(
        "Wat moet Elliot doen?",
        ["Code & Chat (Gemini)", "Concept Art (Nano Banana 2)", "3D Meesterwerk (InstantMesh)"]
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
        
        # --- OPTIE 1: CODE & CHAT ---
        if actie_keuze == "Code & Chat (Gemini)":
            if not gemini_api_key:
                st.error("Je hebt een Gemini API key nodig!")
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
        elif actie_keuze == "Concept Art (Nano Banana 2)":
            if not gemini_api_key:
                st.error("Je hebt een Gemini API key nodig!")
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
                        st.session_state.messages.append({"role": "assistant", "content": "*Concept art gegenereerd.*", "image": image_bytes})
                    except Exception as e:
                        st.error(f"Fout: {e}")

        # --- OPTIE 3: 3D MEESTERWERK (DE HACKER METHODE) ---
        elif actie_keuze == "3D Meesterwerk (InstantMesh)":
            if not gemini_api_key:
                st.error("Gemini is nodig voor stap 1. Vul je key in!")
            else:
                try:
                    # STAP 1: AI tekent een strak plaatje voor het 3D model
                    with st.spinner("Stap 1: Elliot tekent een blauwdruk met Nano Banana... 🎨"):
                        client = genai.Client(api_key=gemini_api_key)
                        # We forceren een strakke achtergrond voor betere 3D
                        strakke_prompt = f"A perfect 3D render of {prompt}, isolated on a pure white background, masterpiece game asset"
                        res_img = client.models.generate_images(
                            model="gemini-3-flash-image",
                            prompt=strakke_prompt,
                            config=types.GenerateImagesConfig(number_of_images=1, output_mime_type="image/jpeg")
                        )
                        img_bytes = res_img.generated_images[0].image.image_bytes
                        st.image(img_bytes, caption="Basis Blueprint")
                        
                        # Sla het plaatje tijdelijk op voor Gradio
                        with tempfile.NamedTemporaryFile(delete=False, suffix=".jpg") as tmp_file:
                            tmp_file.write(img_bytes)
                            tijdelijk_pad = tmp_file.name

                    # STAP 2: Stuur het plaatje naar de InstantMesh Space
                    with st.spinner("Stap 2: InstantMesh smeedt de 3D mesh (Dit kan 60 seconden duren!)... 🔨"):
                        try:
                            hf_client = Client("TencentARC/InstantMesh")
                            
                            # API calls voor InstantMesh (Preprocess -> MultiView -> 3D)
                            st.info("Achtergrond verwijderen...")
                            processed_img = hf_client.predict(input_image=handle_file(tijdelijk_pad), do_remove_background=True, api_name="/preprocess")
                            
                            st.info("Diepte berekenen...")
                            mvs_images = hf_client.predict(api_name="/generate_mvs")
                            
                            st.info("3D Mesh bouwen...")
                            final_result = hf_client.predict(api_name="/make3d")
                            
                            # Gradio spaces geven vaak een tuple/lijst terug. We pakken het bestand.
                            glb_pad = final_result[2] if isinstance(final_result, tuple) else final_result
                            
                            with open(glb_pad, "rb") as f:
                                mesh_data = f.read()
                                
                            st.success("Meesterwerk voltooid! 🎉")
                            st.download_button("📥 Download .OBJ/.GLB", mesh_data, "game_meesterwerk.glb")
                            
                        except Exception as space_err:
                            st.error(f"De gratis Space is momenteel overbelast of de makers hebben de API veranderd: {space_err}")
                            st.warning("Hack: Download het plaatje hierboven en sleep het zélf even in: huggingface.co/spaces/TencentARC/InstantMesh")
                            
                except Exception as e:
                    st.error(f"Fout tijdens het proces: {e}")
