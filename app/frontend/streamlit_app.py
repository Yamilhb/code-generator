import streamlit as st

st.set_page_config(page_title="Generador de Código", layout="wide")

st.title("Generador de Código Asistido por IA")

# 1. Cajita para el prompt del usuario
prompt = st.text_area(
    "Describe la aplicación que quieres desarrollar",
    placeholder="Ejemplo: Una API REST en Flask para sumar dos números...",
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
generate = st.button("GENERAR 🚀")

# Por ahora solo mostramos los valores si se pulsa el botón (prueba de integración)
if generate:
    st.success("¡Solicitud enviada!")
    st.write("**Prompt:**", prompt)
    st.write("**API Key:**", "*" * len(api_token))
