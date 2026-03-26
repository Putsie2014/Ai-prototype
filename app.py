from gradio_client import Client, handle_file
import streamlit as st

def generate_3d_instantmesh(prompt):
    with st.spinner("Elliot bouwt een high-poly model met InstantMesh... 🔨"):
        try:
            # We maken verbinding met de publieke InstantMesh space
            client = Client("TencentARC/InstantMesh")
            
            # Stap 1: De AI maakt eerst een 'multi-view' afbeelding van je prompt
            # (InstantMesh heeft vaak een afbeelding nodig, dus we simuleren dit)
            # LET OP: Sommige spaces hebben verschillende 'api_names', 
            # deze kun je checken op de HF Space onder 'Use via API'.
            result = client.predict(
                input_image=handle_file('https://raw.githubusercontent.com/gradio-app/gradio/main/test/test_files/bus.png'), # Voorbeeld, we kunnen hier je Nano Banana output gebruiken
                api_name="/preprocess"
            )
            
            # Stap 2: Genereer de 3D mesh (.obj of .glb)
            mesh_result = client.predict(
                api_name="/generate_mvs"
            )
            
            # Stap 3: De finale stap geeft meestal een pad naar een .obj of .glb bestand
            final_model_path = client.predict(api_name="/generate_bundle")
            
            return final_model_path
        except Exception as e:
            st.error(f"Gradio-fout: {e}")
            return None
