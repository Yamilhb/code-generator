import streamlit as st
import requests

st.set_page_config(page_title="Generador de Código", layout="wide")

st.title("Generador de Código Asistido por IA")

# 1. Cajita para el prompt del usuario
prompt = st.text_area(
    "Describe la aplicación que quieres desarrollar",
    placeholder="Ejemplo: Una API REST en FastAPI para sumar dos números...",
    height=200,
    key="prompt"
)

# 2. Cajita para el OpenAI API Token (usar tipo 'password' para seguridad)
api_token = st.text_input(
    "Introduce tu OpenAI API Key",
    placeholder="sk-...",
    type="password",
    key="api_token"
)

# 3. Botón para generar
generate = st.button("GENERAR!")

# Conectamos con el Backend

API_URL = "http://app:8000/api/generate_code"
if generate:
    if not prompt.strip():
        st.warning("Por favor, describe la aplicación que quieres generar.")
    elif not api_token.strip():
        st.warning("Por favor, introduce tu OpenAI API Key.")
    else:
        with st.spinner("Generando código... espera un momento."):
            payload = {
                "prompt": prompt,
                "api_key": api_token
            }
            try:
                response = requests.post(API_URL, json=payload, timeout=120)
                if response.status_code == 200:
                    data = response.json()
                    st.success("¡Proceso completado!")
                    st.write(data.get("message", "Código generado."))
                    # Guardamos la url para el siguiente paso
                    st.session_state['download_url'] = data.get("download_url")
                else:
                    st.error(f"Error: {response.status_code}\n{response.text}")
            except Exception as e:
                st.error(f"Error conectando con el backend: {e}")