from huggingface_hub import InferenceClient
import streamlit as st

# 1. Vul hier je token in (of zet hem in je Streamlit secrets)
HF_TOKEN = "PLAK_HIER_JE_HF_TOKEN" 

# 2. Maak de 'client' aan
client = InferenceClient(api_key=HF_TOKEN)

def maak_3d_preview(prompt):
    st.info("Elliot is bezig met je 3D model... Even geduld.")
    try:
        # We sturen de vraag naar het Shap-E model
        image_bytes = client.post(
            model="openai/shap-e",
            json={"inputs": prompt}
        )
        # De API stuurt een GIF terug
        return image_bytes
    except Exception as e:
        st.error(f"Er ging iets mis: {e}")
        return None

# 3. Gebruik het in je interface
if st.button("Genereer 3D"):
    if prompt:
        resultaat = maak_3d_preview(prompt)
        if resultaat:
            st.image(resultaat, caption="Hier is je 3D preview!")
    else:
        st.warning("Typ eerst wat je wilt maken!")
