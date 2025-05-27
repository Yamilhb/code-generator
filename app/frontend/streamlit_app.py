import streamlit as st
import requests
from streamlit_ace import st_ace

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

# --- STEP 2: API Key ---
st.markdown("<div class='step-title'>Step 2: Paste your OpenAI API key</div>", unsafe_allow_html=True)
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
API_URL = "http://app:8000/api/generate_code"
if generate:
    st.session_state['last_error_feedback'] = None
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
                response = requests.post(API_URL, json=payload, timeout=120)
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
if st.session_state.get('download_url'):
    st.markdown("---")
    st.markdown("<div class='step-title' style='margin-bottom:0.3em;'>Explore your generated project</div>", unsafe_allow_html=True)

    def fetch_tree():
        url = "http://app:8000/api/list_project"
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

    # File selection state
    if "selected_file_global" not in st.session_state:
        st.session_state["selected_file_global"] = None

    def render_tree_indent(nodes, parent_path="", level=0):
        for node in nodes:
            current_path = f"{parent_path}/{node['name']}".lstrip("/")
            # Cada nivel de profundidad agrega columnas vacías
            cols = st.columns([0.05] * level + [0.06, 1 - 0.05*level - 0.06])
            if node["type"] == "folder":
                with cols[level]:
                    toggled = st.button(
                        "+" if not st.session_state.get(f"expand_{current_path}", node['name'] == "root") else "–",
                        key=f"btn_{current_path}",
                        help="Expand/Collapse folder"
                    )
                with cols[level+1]:
                    st.markdown(f"<b>📁 {node['name']}</b>", unsafe_allow_html=True)
                if toggled:
                    st.session_state[f"expand_{current_path}"] = not st.session_state.get(f"expand_{current_path}", node['name'] == "root")
                if st.session_state.get(f"expand_{current_path}", node['name'] == "root"):
                    render_tree_indent(node["children"], current_path, level+1)
            else:
                with cols[level+1]:
                    select_key = f"select_{current_path}"
                    if st.button(f"📄 {node['name']}", key=select_key):
                        st.session_state["selected_file_global"] = current_path
                    if st.session_state.get("selected_file_global", "") == current_path:
                        st.markdown(f"<span class='selected-file'>[Selected]</span>", unsafe_allow_html=True)


    render_tree_indent(project_tree)
    selected_file = st.session_state.get("selected_file_global", None)
    if selected_file:
        real_path = selected_file[len("root/"):] if selected_file.startswith("root/") else selected_file
        st.info(f"Selected file: `{real_path}`")
        url_file = f"http://app:8000/api/get_file?path={real_path}"
        try:
            file_resp = requests.get(url_file, timeout=10)
            if file_resp.status_code == 200:
                file_content = file_resp.text
                # Minimal syntax highlight
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
