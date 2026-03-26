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
    
    # gemini-3-flash-image toegevoegd voor beeldgeneratie!
    model_id = st.selectbox(
        "Kies Model:", 
        [
            "gemini-2.5-flash",       # Snel en efficiënt voor code
            "gemini-3.1-pro-preview", # Het krachtigste model voor complexe logica
            "gemini-2.5-pro",
            "gemini-3-flash-image"    # Nano Banana 2 voor concept art!
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
        # Nieuw: Toon de afbeelding als deze in de geschiedenis staat
        if "image" in msg:
            st.image(msg["image"])

# --- CHAT INPUT & LOGICA ---
if prompt := st.chat_input("Vraag Elliot iets over code, of vraag om concept art..."):
    if not api_key:
        st.error("Vul je API-key in via het menu links!")
    else:
        # Voeg gebruikersbericht toe aan UI en geschiedenis
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)

        try:
            client = genai.Client(api_key=api_key)
            
            with st.chat_message("assistant", avatar="👨‍💻"):
                
                # --- BEELDGENERATIE LOGICA ---
                if model_id == "gemini-3-flash-image":
                    with st.spinner("Elliot tekent game assets... 🎨"):
                        # Gebruik generate_images voor het Nano Banana 2 model
                        response = client.models.generate_images(
                            model=model_id,
                            prompt=prompt,
                            config=types.GenerateImagesConfig(
                                number_of_images=1,
                                output_mime_type="image/jpeg"
                            )
                        )
                        
                        # Haal de afbeeldingsdata op
                        generated_image = response.generated_images[0]
                        image_bytes = generated_image.image.image_bytes
                        
                        # Toon in UI
                        st.image(image_bytes)
                        st.markdown("*Concept art gegenereerd door Elliot.*")
                        
                        # Sla op in chatgeschiedenis
                        st.session_state.messages.append({
                            "role": "assistant", 
                            "content": "*Concept art gegenereerd door Elliot.*",
                            "image": image_bytes
                        })
                
                # --- TEKSTGENERATIE LOGICA (Bestaand) ---
                else:
                    with st.spinner("Elliot schrijft code... ⌨️"):
                        config_args = {
                            "system_instruction": ELLIOT_SYSTEM_PROMPT,
                            "temperature": 0.2
                        }

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
            if "404" in error_msg or "NOT_FOUND" in error_msg:
                st.error(f"⚠️ **Model niet gevonden (404 Error)**\n\nGoogle herkent het model `{model_id}` niet. Check de exacte naamgeving.")
            elif "429" in error_msg or "RESOURCE_EXHAUSTED" in error_msg:
                st.warning("🛑 **Quota Bereikt of Geblokkeerd (429 Error)**\n\nLet op: voor het gratis plan heb je een limiet van 20 afbeeldingen per dag met het image model.")
            else:
                st.error(f"Er is iets misgegaan: {error_msg}")
