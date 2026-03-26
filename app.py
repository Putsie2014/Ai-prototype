import streamlit as st
from google import genai
from google.genai import types

st.set_page_config(page_title="Gemini Thinking App", page_icon="🧠")
st.title("🤖 Gemini Thinking Assistant")

# Sidebar voor instellingen
with st.sidebar:
    api_key = st.text_input("Voer je Gemini API Key in:", type="password")
    model_choice = st.selectbox("Kies Model:", ["gemini-2.5-flash", "gemini-3.1-pro-preview"])
    # Instellen van het 'Thinking' niveau (voor ondersteunde modellen)
    thinking_level = st.select_slider("Thinking Budget (Redeneer-diepte):", 
                                      options=["MINIMAL", "LOW", "MEDIUM", "HIGH"], 
                                      value="MEDIUM")

if api_key:
    client = genai.Client(api_key=api_key)

    prompt = st.chat_input("Stel je complexe vraag...")

    if prompt:
        with st.chat_message("user"):
            st.markdown(prompt)

        with st.chat_message("assistant"):
            with st.spinner("Aan het nadenken..."):
                # Aanroep naar het model met specifieke configuratie
                response = client.models.generate_content(
                    model=model_choice,
                    contents=prompt,
                    config=types.GenerateContentConfig(
                        # Voor Gemini 3+ modellen gebruik je thinking_level
                        thinking_level=thinking_level 
                    )
                )
                st.markdown(response.text)
else:
    st.info("Voer je API-key in de sidebar in om te beginnen.")
