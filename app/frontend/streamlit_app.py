import streamlit as st
from streamlit_ace import st_ace
import requests
import time
from dotenv import load_dotenv
import os
from pathlib import Path


ZIP_URL = os.getenv("ZIP_URL")
APP_URL = os.getenv("APP_URL")
MAX_IMAGE_SIZE_MB = int(os.getenv("MAX_IMAGE_SIZE_MB"))
MAX_IMAGE_SIZE_BYTES = MAX_IMAGE_SIZE_MB * 1024 * 1024


# ---- MINIMALIST/PRO STYLE ----
st.set_page_config(page_title="AI-Assisted App Builder", layout="wide")

st.markdown("""
    <style>
    /* Hide Streamlit branding and menu */
    #MainMenu, header, footer {visibility: hidden;}
    .block-container {padding-top: 2.5rem;}
    /* Inputs */
    .stTextInput > div > div > input, .stTextArea textarea {
        background: #f8f9fa !important;
        border-radius: 12px;
        border: 1.3px solid #e3e3e3;
        padding: 0.7em 1.1em;
        font-size: 1.07em;
        font-family: 'Montserrat', 'Segoe UI', Arial, sans-serif;
    }
    /* Button */
    .stButton > button {
        border-radius: 10px;
        background: #22223b;
        color: #fff;
        border: none;
        padding: 0.5em 2em;
        font-weight: 600;
        font-size: 1.07em;
        transition: background 0.22s;
        margin: 0.5em 0 1.3em 0;
        letter-spacing: 0.02em;
    }
    .stButton > button:hover {
        background: #4a4e69;
        color: #fff;
    }
    /* Markdown, alerts, spacing */
    .stMarkdown, .stInfo, .stError, .stSuccess, .stWarning {
        border-radius: 10px;
        font-size: 1.05em;
        padding-left: 10px;
    }
    /* Center step titles */
    .step-title {text-align: center; color:#22223b; margin-top:0.7em; margin-bottom:0.6em;}
    /* Explorer selected */
    .selected-file {
        background:#c9ada7;
        color:#22223b;
        font-weight:bold;
        border-radius:5px;
        padding:2.5px 9px;
    }
    </style>
""", unsafe_allow_html=True)

# ---- MAIN TITLE ----
st.markdown("<h1 style='font-family:Montserrat,Segoe UI,Arial,sans-serif;font-weight:650; color:#22223b; margin-bottom: 0.6em;'>🚀 AI-Assisted App Builder</h1>", unsafe_allow_html=True)

# --- STEP 1: Prompt ---
st.markdown("<div class='step-title'>Step 1: Describe your application</div>", unsafe_allow_html=True)
prompt = st.text_area(
    "",
    placeholder="Example: A REST API in FastAPI to add two numbers...",
    height=160,
    key="prompt"
)

# --- STEP 3: API Key ---
st.markdown("<div class='step-title'>Step 2: Upload an image (optional)</div>", unsafe_allow_html=True)
uploaded_file = st.file_uploader("Upload an image to help your description", type=["jpg", "jpeg", "png"])

image_ok = True
if uploaded_file is not None:
    if uploaded_file.size > MAX_IMAGE_SIZE_BYTES:
        st.error(f"Image is too large! Please upload a file smaller than {MAX_IMAGE_SIZE_MB} MB.")
        image_ok = False 
else:
    uploaded_file = None  


# --- STEP 3: API Key ---
st.markdown("<div class='step-title'>Step 3: Paste your OpenAI API key</div>", unsafe_allow_html=True)
api_token = st.text_input(
    "",
    placeholder="sk-...",
    type="password",
    key="api_token"
)

# --- STEP 3: Run ---
st.markdown("<div style='height:18px'></div>", unsafe_allow_html=True)
col_run = st.columns([2, 1, 2])
with col_run[1]:
    generate = st.button("RUN!", key="main_run_btn")

# --- Send request and feedback logic ---
API_URL = f"{APP_URL}/generate_code"

if generate:
    files = {"image_file": uploaded_file} if uploaded_file else None
    st.session_state['last_error_feedback'] = None
    if not image_ok:
        st.warning("The image is too large. Please upload a smaller file.")
    if not prompt.strip():
        st.warning("Please describe the application you want to generate.")
    elif not api_token.strip():
        st.warning("Please enter your OpenAI API Key.")
    else:
        with st.spinner("Hold on, we're generating your code..."):
            payload = {
                "prompt": prompt,
                "api_key": api_token
            }
            try:
                if files:
                    response = requests.post(API_URL, data=payload, files=files, timeout=300)
                else:
                    response = requests.post(API_URL, data=payload, timeout=300)
                if response.status_code == 200:
                    data = response.json()
                    msg = data.get("message", "")
                    st.session_state['download_url'] = data.get("download_url")
                    # Show warning in red if present
                    if ("Warning" in msg) or ("out of context" in msg):
                        st.session_state['last_error_feedback'] = "🚨 " + msg
                    elif "failed" in msg.lower():
                        st.error(msg)
                    else:
                        st.success("🎉 The process is complete!")
                        st.write(msg)
                else:
                    st.error(f"Error: {response.text}")
                    if 'download_url' in st.session_state:
                        del st.session_state['download_url']
            except Exception as e:
                st.error(f"Error connecting to the backend: {e}")
                if 'download_url' in st.session_state:
                    del st.session_state['download_url']

# --- Show warning block if needed ---
if st.session_state.get('last_error_feedback'):
    st.error(st.session_state['last_error_feedback'])

# ---- FILE EXPLORER ----

def check_zip_exists():
    # Consulta al backend si el ZIP existe (HEAD sería mejor pero usamos GET)
    resp = requests.get(f"{APP_URL}/download/project.zip", stream=True)
    return resp.status_code == 200

if st.session_state.get('download_url'):
    st.markdown("---")

    # Card/Panel para el explorador y la descarga
    with st.container():
        # Encabezado + botón de descarga en la misma fila
        explorer_cols = st.columns([0.7, 0.3])
        with explorer_cols[0]:
            st.markdown("<div class='step-title' style='margin-bottom:0.3em;text-align:left;'>📁 Explore your generated project</div>", unsafe_allow_html=True)
        with explorer_cols[1]:
            if check_zip_exists():
                st.markdown(
                    f"""
                    <a href="{ZIP_URL}" target="_blank" style="
                        display:inline-block;
                        background:#4a4e69;
                        color:white;
                        border:none;
                        padding:8px 22px;
                        border-radius:8px;
                        font-weight:600;
                        font-size:1.05em;
                        float:right;
                        margin-top:8px;
                        text-decoration:none;
                        transition:background 0.22s;
                    ">
                        📦 Download ZIP
                    </a>
                    """,
                    unsafe_allow_html=True
                )
            else:
                st.info("ℹ️ The ZIP will be available after generation.")

        # Fetch tree structure
        def fetch_tree():
            url = f"{APP_URL}/list_project"
            try:
                resp = requests.get(url, timeout=20)
                return resp.json() if resp.status_code == 200 else []
            except Exception as e:
                st.warning(f"Failed to load structure: {e}")
                return []

        tree = fetch_tree()
        project_tree = [{
            "type": "folder",
            "name": "root",
            "path": "",
            "children": tree
        }]

        # Estado global de archivo seleccionado
        if "selected_file_global" not in st.session_state:
            st.session_state["selected_file_global"] = None

        def render_tree_indent(nodes, parent_path="", level=0):
            for node in nodes:
                current_path = f"{parent_path}/{node['name']}".lstrip("/")
                indent_px = 20 * level
                if node["type"] == "folder":
                    exp_key = f"expand_{current_path}"
                    if exp_key not in st.session_state:
                        st.session_state[exp_key] = node['name'] == "root"
                    expander_row = st.columns([0.05, 0.9])
                    with expander_row[0]:
                        toggled = st.button(
                            "–" if st.session_state[exp_key] else "+",
                            key=f"btn_{current_path}",
                            help="Expand/Collapse folder"
                        )
                        if toggled:
                            st.session_state[exp_key] = not st.session_state[exp_key]
                    with expander_row[1]:
                        st.markdown(
                            f"<div style='margin-left:{indent_px}px;display:inline-block;'><b>📁 {node['name']}</b></div>",
                            unsafe_allow_html=True
                        )
                    if st.session_state[exp_key]:
                        render_tree_indent(node["children"], current_path, level + 1)
                else:
                    sel = st.session_state.get("selected_file_global", "") == current_path
                    file_cols = st.columns([0.05, 0.9])
                    with file_cols[1]:
                        file_style = (
                            f"margin-left:{indent_px+26}px;display:inline-block;"
                            "background:#22223b;color:#fff;padding:4px 14px 4px 8px;"
                            "border-radius:9px;font-size:0.97em;font-family:monospace;"
                            "margin-top:3px;margin-bottom:3px;"
                            "box-shadow:0 1px 3px #ddd;"
                            f"{'box-shadow:0 0 0 2px #c9ada7;' if sel else ''}"
                        )
                        if st.button(f"📄 {node['name']}", key=f"select_{current_path}"):
                            st.session_state["selected_file_global"] = current_path
                        # Feedback visual, solo texto verde a la derecha
                        if sel:
                            st.markdown(
                                f"<span style='color:#c9ada7;margin-left:8px;font-weight:bold;'>[Selected]</span>",
                                unsafe_allow_html=True
                            )

                # No action for row[2] (espaciador)

        render_tree_indent(project_tree)

        # Mostrar el archivo seleccionado
        selected_file = st.session_state.get("selected_file_global", None)
        if selected_file:
            real_path = selected_file[len("root/"):] if selected_file.startswith("root/") else selected_file
            st.info(f"Selected file: `{real_path}`")
            url_file = f"{APP_URL}/get_file?path={real_path}"
            try:
                file_resp = requests.get(url_file, timeout=10)
                if file_resp.status_code == 200:
                    file_content = file_resp.text
                    if real_path.endswith((".py", ".txt", ".md", ".json", ".yaml", ".yml", ".toml", "Dockerfile")):
                        st_ace(
                            value=file_content,
                            language="python" if real_path.endswith(".py") else "text",
                            theme="chrome",
                            readonly=True,
                            height=400,
                            key=f"ace_{real_path}",
                        )
                    else:
                        st.code(file_content)
                else:
                    st.warning("Could not load the file (does it exist?)")
            except Exception as e:
                st.warning(f"Failed to load structure: {e}")
